"""
### COVID-19 Daily Ingestion & Materialized View Refresh Pipeline

This pipeline runs daily to:
1. Download the latest COVID-19 dataset from Our World in Data (OWID).
2. Perform vectorized schema and validation checks.
3. Normalize wide table data into the relational snowflake schema.
4. Execute bulk upserts (INSERT ON CONFLICT DO UPDATE) in 5,000-row chunks.
5. Concurrent refresh of all analytical views and materialized metrics.
"""
import logging
from datetime import datetime, timedelta
from airflow import DAG

# In Airflow 2.x, the plugins directory is added to sys.path, 
# allowing clean direct imports of custom operators.
from covid19_operators.etl_operator import Covid19ETLOperator

logger = logging.getLogger("airflow.task")

# ── Callback Functions ──

def on_failure_callback(context):
    """
    Executes when a task fails.
    In a real enterprise environment, this would trigger PagerDuty, Slack, or email alerts.
    """
    task_instance = context.get("task_instance")
    error = context.get("exception")
    logger.error(
        f"🚨 DAG ALERT: Task '{task_instance.task_id}' failed in DAG '{task_instance.dag_id}'. "
        f"Execution Date: {context.get('execution_date')}. Error: {error}"
    )

def on_success_callback(context):
    """
    Executes when the DAG succeeds.
    """
    logger.info(
        f"✅ DAG SUCCESS: ETL Pipeline '{context.get('dag').dag_id}' completed successfully."
    )

def on_sla_miss_callback(dag, task_list, blocking_task_list, slas, blocking_tis):
    """
    Executes when the SLA is missed.
    """
    logger.warning(f"⚠️ SLA MISS: The ETL pipeline exceeded the expected duration.")


# ── DAG Configuration ──

default_args = {
    "owner": "data_engineering",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": on_failure_callback,
    "sla": timedelta(hours=1), # SLA of 1 hour to complete the pipeline
}

with DAG(
    dag_id="covid19_enterprise_etl",
    default_args=default_args,
    description="Extracts, cleans, and loads global COVID-19 epidemiological data from OWID.",
    schedule_interval="0 2 * * *", # Run daily at 2:00 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["covid19", "production", "etl", "daily"],
    on_success_callback=on_success_callback,
    sla_miss_callback=on_sla_miss_callback,
    doc_md=__doc__,
) as dag:

    # ── Tasks ──

    run_etl_task = Covid19ETLOperator(
        task_id="extract_transform_load_covid_data",
        force_run=False, # Set to True to force run regardless of checksum
        execution_timeout=timedelta(minutes=45),
        doc_md="Downloads raw OWID CSV, performs quality validations, normalizes into dimensional model, and bulk upserts to Postgres."
    )

    run_etl_task
