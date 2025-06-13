FROM quay.io/astronomer/astro-runtime:13.0.0

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY dbt/ /opt/airflow/dbt/

USER root
RUN chown -R astro:astro /opt/airflow/dbt
USER astro