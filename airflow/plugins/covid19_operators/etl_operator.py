import logging
import sys
import os
from pathlib import Path
from airflow.models import BaseOperator

# ── Path Fix ──────────────────────────────────────────────────────────────────
# Airflow adds <AIRFLOW_HOME>/plugins/ to sys.path, but the `etl` package
# lives at the project root (two levels above this file:
#   project_root/airflow/plugins/covid19_operators/etl_operator.py
#   project_root/etl/runner.py
# ).
# We resolve the project root at import time and prepend it so that
# `from etl.runner import ETLRunner` works correctly inside the operator.
_OPERATOR_DIR = Path(__file__).resolve().parent          # .../plugins/covid19_operators
_PLUGINS_DIR  = _OPERATOR_DIR.parent                     # .../plugins
_AIRFLOW_DIR  = _PLUGINS_DIR.parent                      # .../airflow
_PROJECT_ROOT = _AIRFLOW_DIR.parent                      # project root

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
# ──────────────────────────────────────────────────────────────────────────────

from etl.runner import ETLRunner  # noqa: E402 — must come after sys.path fix


class Covid19ETLOperator(BaseOperator):
    """
    Custom Airflow Operator that encapsulates the COVID-19 ETL execution logic.
    Instead of using a generic PythonOperator, this dedicated operator provides cleaner logs,
    distinct UI representation, and encapsulates the runner configuration.
    """

    def __init__(self, force_run: bool = False, *args, **kwargs):
        super(Covid19ETLOperator, self).__init__(*args, **kwargs)
        self.force_run = force_run

    def execute(self, context):
        self.log.info("Starting Covid19ETLOperator execution.")

        # Accessing Airflow's execution context
        execution_date = context.get("execution_date")
        self.log.info(f"Target Execution Date: {execution_date}")

        try:
            self.log.info(f"Instantiating ETL Runner (force={self.force_run})")
            runner = ETLRunner()
            runner.run(force=self.force_run)
            self.log.info("ETL Runner finished successfully.")
        except Exception as e:
            self.log.error(f"ETL execution failed: {str(e)}")
            raise

