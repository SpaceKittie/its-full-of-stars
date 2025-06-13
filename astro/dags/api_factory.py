"""
DAG Factory for API data ingestion into Snowflake.
Dynamically generates Airflow DAGs for multiple API sources.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import pendulum
from airflow.decorators import task
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

from include.get_astronauts import AstronautsStrategy
from include.get_in_space import InSpaceStrategy
from include.get_iss_location import IssLocationStrategy
from include.get_nasa_apod import NasaApodStrategy
from include.utils.api_strategy import ApiStrategy
from include.utils.snowflake_loader import load_to_snowflake

# Snowflake configuration
SNOWFLAKE_CONN_ID = "snowflake_default"
SNOWFLAKE_DATABASE = "SPACE_CADET_DB"
SNOWFLAKE_SCHEMA = "CARGO_BAY"

# dbt configuration
DBT_PROJECT_PATH = Path("/opt/airflow/dbt")
DBT_EXECUTABLE_PATH = "dbt"
DBT_PROFILE_PATH = Path("/opt/airflow/dbt")

API_SOURCES = [
    {
        "name": "iss_location",
        "api_client": IssLocationStrategy(),
        "schedule": "*/1 * * * *", 
        "raw_table_name": "CB_ISS_LOCATION",
        "overwrite_table": False, 
        "timestamp_cols": [{'name': 'API_TIMESTAMP', 'unit': 's'}],
        "dbt_models": ["mc_iss_location"],
    },
    {
        "name": "nasa_apod",
        "api_client": NasaApodStrategy(),
        "schedule": "@daily",
        "raw_table_name": "CB_NASA_APOD",
        "overwrite_table": True,  
        "timestamp_cols": [{'name': 'APOD_DATE'}],
        "dbt_models": ["mc_apod"],
    },
    {
        "name": "astronauts",
        "api_client": AstronautsStrategy(),
        "schedule": "@weekly",
        "raw_table_name": "CB_ASTRONAUTS",
        "overwrite_table": True, 
        "timestamp_cols": [],
        "dbt_models": [],
    },
    {
        "name": "in_space",
        "api_client": InSpaceStrategy(),
        "schedule": "@daily",
        "raw_table_name": "CB_IN_SPACE",
        "overwrite_table": True, 
        "timestamp_cols": [],
        "dbt_models": ["mc_astronauts"],
    },
]

def create_dag(
    dag_id: str,
    schedule: str,
    doc_md: str,
    api_client: ApiStrategy,
    raw_table_name: str,
    overwrite: bool,
    timestamp_cols: list[dict] = None,
    dbt_models: list[str] = None
) -> DAG:
    """
    Create a DAG for fetching API data and loading to Snowflake.
    
    Args:
        dag_id: Unique DAG identifier
        schedule: Cron schedule for the DAG
        doc_md: DAG documentation in markdown
        api_client: Strategy for API interaction
        raw_table_name: Target Snowflake table
        overwrite: Whether to overwrite existing data
        timestamp_cols: Columns to parse as timestamps
        dbt_models: List of dbt models to run after loading
    
    Returns:
        Configured Airflow DAG instance
    """

    default_args = {
        'owner': 'airflow',
        'retries': 1,
        'retry_delay': pendulum.duration(minutes=5),
    }

    # Start with base tags and add more based on functionality
    tags = ['api_ingestion', 'snowflake']
    if dbt_models:
        tags.append('dbt_transform')

    # Define tags to categorize the DAG's functionality
    with DAG(
        dag_id=dag_id,
        start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
        schedule=schedule,
        catchup=False,
        doc_md=doc_md,
        default_args=default_args,
        tags=tags,
    ) as dag:

        @task
        def fetch_data_task() -> list[dict]:
            """Generic task to fetch data using the provided API client."""
            logging.info(f"DAG: {dag_id} - Running fetch_data_task using API client: {api_client.__class__.__name__}")
            data = api_client.fetch_data()
            logging.info(f"DAG: {dag_id} - Fetched {len(data)} records.")
            return data

        @task
        def load_data_task(data: list[dict]):
            """Generic task to load data into a specified Snowflake table."""
            logging.info(f"DAG: {dag_id} - Running load_data_task for table: {raw_table_name}")
            load_to_snowflake(
                data=data,
                table_name=raw_table_name,
                snowflake_conn_id=SNOWFLAKE_CONN_ID,
                database=SNOWFLAKE_DATABASE,
                schema=SNOWFLAKE_SCHEMA,
                overwrite=overwrite,
                timestamp_cols=timestamp_cols,
            )
            logging.info(f"DAG: {dag_id} - Successfully loaded data into {raw_table_name}.")

        load_task = load_data_task(fetch_data_task())

        if dbt_models:
            models_to_run = " ".join([f"+{model}" for model in dbt_models])
            
            dbt_vars = {
                "raw_db": SNOWFLAKE_DATABASE,
                "raw_schema": SNOWFLAKE_SCHEMA
            }

            bash_command = (
                f"cd {DBT_PROJECT_PATH} && "
                f"{DBT_EXECUTABLE_PATH} run "
                f"--select {models_to_run} "
                f"--profiles-dir {DBT_PROFILE_PATH} "
                f"--vars '{json.dumps(dbt_vars)}'"
            )

            dbt_run_task = BashOperator(
                task_id="dbt_run_models",
                bash_command=bash_command,
                retries=2,
            )

            load_task >> dbt_run_task
    
    return dag

for source in API_SOURCES:
    dag_id = f"{source['name']}_api_dag"
    api_client_name = source['api_client'].__class__.__name__
    raw_table_name = source['raw_table_name']
    overwrite = source.get('overwrite_table', True)
    timestamp_cols = source.get('timestamp_cols')
    dbt_models = source.get('dbt_models')
    doc_md = f"""
    ### Dynamically Generated DAG: {source['name'].replace('_', ' ').title()}\n
    **Purpose:** This DAG fetches data from an external API and loads it into a raw Snowflake table.`.

    ---

    #### Key Metadata:
    - **Data Source:** `{source['name']}`
    - **API Strategy:** `{api_client_name}`
    - **Schedule:** `{source['schedule']}`
    - **Write Disposition:** `{'Overwrite' if overwrite else 'Append'}`
    - **Target Snowflake Table:** `{SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.{raw_table_name}`
    
    ---

    #### Tasks:
    1.  **`fetch_data_task`**: Uses the `{api_client_name}` class to pull data from the source API.
    2.  **`load_data_task`**: Loads the fetched data into `{raw_table_name}`.
    3.  **`dbt_run_models`**: This task will run the associated models using a `BashOperator`.
    """

    globals()[dag_id] = create_dag(
        dag_id=dag_id,
        schedule=source['schedule'],
        doc_md=doc_md,
        api_client=source['api_client'],
        raw_table_name=raw_table_name,
        overwrite=overwrite,
        timestamp_cols=timestamp_cols,
        dbt_models=dbt_models,
    )







