"""
Utility for loading data into Snowflake from various sources.

This module provides functionality to efficiently load pandas DataFrames into
Snowflake tables with support for different loading strategies and data types.
"""
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import pandas as pd
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook # type: ignore
from snowflake.connector.pandas_tools import write_pandas

logger = logging.getLogger(__name__)

def load_to_snowflake(
    data: List[Dict[str, Any]],
    table_name: str,
    snowflake_conn_id: str,
    database: str,
    schema: str,
    overwrite: bool = True,
    timestamp_cols: Optional[List[Dict[str, str]]] = None
) -> None:
    """
    Load data into a Snowflake table from a list of dictionaries.
    
    The target table must already exist in Snowflake. This function handles
    data type conversions and provides options for full refresh or append loading.
    
    Args:
        data: List of dictionaries where each dict represents a row of data
        table_name: Name of the target Snowflake table (case-insensitive)
        snowflake_conn_id: Airflow connection ID for Snowflake
        database: Target database name
        schema: Target schema name
        overwrite: If True, truncates the table before loading (full refresh).
                  If False, appends to existing data (incremental load).
        timestamp_cols: Optional list of dicts specifying timestamp columns to convert.
                      Example: [{'name': 'API_TIMESTAMP', 'unit': 's'}]
                      
    Note:
        - Automatically converts column names to uppercase
        - Adds a LOAD_TS column with the current UTC timestamp
    """
    if not data:
        logger.info("No data provided to load. Exiting.")
        return

    hook = SnowflakeHook(snowflake_conn_id=snowflake_conn_id)
    table_name = table_name.upper()

    with hook.get_conn() as conn:
        logger.info("Loading %d records into %s (overwrite=%s)", len(data), table_name, overwrite)
        conn.cursor().execute(f"USE DATABASE {database}")
        conn.cursor().execute(f"USE SCHEMA {schema}")

        df = pd.DataFrame(data)
        df.columns = [col.upper() for col in df.columns]

        if timestamp_cols:
            for col_info in timestamp_cols:
                col_name = col_info['name'].upper()
                if col_name in df.columns:
                    unit = col_info.get('unit')
                    logger.debug("Converting column '%s' to datetime (unit: %s)", col_name, unit or 'default')
                    df[col_name] = pd.to_datetime(df[col_name], unit=unit, utc=True).dt.tz_localize(None)

        df["LOAD_TS"] = datetime.now(timezone.utc).replace(tzinfo=None)

        if overwrite:
            conn.cursor().execute(f"TRUNCATE TABLE IF EXISTS {table_name};")
            logger.info("Table %s truncated", table_name)

        logger.debug("DataFrame info before loading to Snowflake")
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("\n%s", df.info())

        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name=table_name,
            auto_create_table=False,
            overwrite=False, 
            use_logical_type=True,
        )
        
        if success:
            print(f"Successfully loaded {nrows} rows into {table_name}.")
        else:
            raise Exception(f"Failed to load data into {table_name}.")

    print("Snowflake connection closed.") 