import logging
import sys
import traceback
import uuid
import time
from datetime import datetime
from typing import Optional
import pandas as pd
import psycopg2
from etl.config import etl_config
from etl.extractors.owid_extractor import OWIDExtractor
from etl.validators.data_validator import DataValidator
from etl.transformers.cleaner import DataCleaner
from etl.transformers.metric_calculator import MetricCalculator
from etl.loaders.postgres_loader import PostgresLoader

# Configure structured console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("etl.runner")


class ETLRunner:
    """
    Orchestrator for the complete COVID-19 ETL data pipeline.
    Manages process sequence, validates checksum states, and logs executions.
    """

    def __init__(self) -> None:
        self.extractor = OWIDExtractor()
        self.validator = DataValidator()
        self.cleaner = DataCleaner()
        self.calculator = MetricCalculator()
        self.loader = PostgresLoader()

    def _get_last_successful_checksum(self) -> Optional[str]:
        """
        Queries database logs to get the last successful run checksum.
        """
        conn = psycopg2.connect(etl_config.DATABASE_URL)
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT dataset_checksum FROM etl_logs WHERE status = 'SUCCESS' "
                "ORDER BY started_at DESC LIMIT 1"
            )
            row = cur.fetchone()
            return row[0] if row else None
        except Exception as e:
            logger.warning(f"Could not retrieve last successful checksum: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    def _log_run_start(self, run_id: uuid.UUID) -> None:
        """
        Inserts initial RUNNING log record in the database.
        """
        conn = psycopg2.connect(etl_config.DATABASE_URL)
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO etl_logs (run_id, pipeline_name, status, started_at) "
                "VALUES (%s, %s, %s, %s)",
                (str(run_id), "covid19_etl_pipeline", "RUNNING", datetime.utcnow())
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to log run start: {e}")
        finally:
            cur.close()
            conn.close()

    def _log_run_end(
        self, 
        run_id: uuid.UUID, 
        status: str, 
        rows_downloaded: int = 0,
        rows_validated: int = 0,
        rows_rejected: int = 0,
        rows_inserted: int = 0,
        checksum: Optional[str] = None,
        error_msg: Optional[str] = None,
        error_tb: Optional[str] = None
    ) -> None:
        """
        Updates the run record to SUCCESS or FAILED with execution stats.
        """
        conn = psycopg2.connect(etl_config.DATABASE_URL)
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE etl_logs 
                SET status = %s, 
                    rows_downloaded = %s,
                    rows_validated = %s,
                    rows_rejected = %s,
                    rows_inserted = %s,
                    dataset_checksum = %s,
                    error_message = %s,
                    error_traceback = %s,
                    completed_at = %s
                WHERE run_id = %s
                """,
                (
                    status, rows_downloaded, rows_validated, rows_rejected, 
                    rows_inserted, checksum, error_msg, error_tb, 
                    datetime.utcnow(), str(run_id)
                )
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to write run completion log: {e}")
        finally:
            cur.close()
            conn.close()

    def run(self, force: bool = False) -> None:
        """
        Orchestrates pipeline execution.
        """
        run_id = uuid.uuid4()
        logger.info(f"Starting ETL execution. Run ID: {run_id}")
        self._log_run_start(run_id)

        checksum = None
        rows_downloaded = 0
        rows_validated = 0
        rows_rejected = 0
        rows_inserted = 0

        try:
            # 1. Download raw CSV dataset
            file_path, checksum = self.extractor.download_dataset()
            
            # 2. Check for changes compared to last execution
            last_checksum = self._get_last_successful_checksum()
            if checksum == last_checksum and not force:
                logger.info("Dataset checksum matches last successful run. Skipping ETL processing.")
                self._log_run_end(run_id, "SKIPPED", checksum=checksum)
                # Cleanup downloaded file
                file_path.unlink(missing_ok=True)
                return
                
            # 3. Detect Schema Drift
            has_drifted, missing_cols = self.extractor.detect_schema_drift(file_path)
            if has_drifted:
                raise ValueError(f"Schema drift detected! Missing fields: {missing_cols}")
                
            # 4. Load Dataset into DataFrame
            logger.info("Loading dataset into pandas...")
            df = pd.read_csv(file_path)
            rows_downloaded = len(df)
            
            # 5. Validate Rows
            valid_df, rows_rejected = self.validator.validate(df)
            rows_validated = len(valid_df)
            
            # 6. Clean and Normalize Dataframes
            countries_df, demographics_df, daily_metrics_df, vacc_df, testing_df, hosp_df = \
                self.cleaner.clean_and_normalize(valid_df)
                
            # 7. Format Types and handle missing values
            self.calculator.calculate_derived_metrics(daily_metrics_df, vacc_df, testing_df)
            
            # Attach run ID to records for tracking
            daily_metrics_df["etl_run_id"] = str(run_id)
            vacc_df["etl_run_id"] = str(run_id)
            testing_df["etl_run_id"] = str(run_id)
            hosp_df["etl_run_id"] = str(run_id)
            
            # 8. Bulk Load into Database (Order matters!)
            # Dimensions
            self.loader.bulk_upsert("countries", countries_df, ["iso_code"], ["location", "continent", "income_group"])
            self.loader.bulk_upsert("demographics", demographics_df, ["iso_code"], list(demographics_df.columns[1:]))
            
            # Facts
            m_ins, _ = self.loader.bulk_upsert("daily_metrics", daily_metrics_df, ["iso_code", "date"], list(daily_metrics_df.columns[2:]))
            v_ins, _ = self.loader.bulk_upsert("vaccinations", vacc_df, ["iso_code", "date"], list(vacc_df.columns[2:]))
            t_ins, _ = self.loader.bulk_upsert("testing", testing_df, ["iso_code", "date"], list(testing_df.columns[2:]))
            h_ins, _ = self.loader.bulk_upsert("hospitalizations", hosp_df, ["iso_code", "date"], list(hosp_df.columns[2:]))
            
            rows_inserted = m_ins + v_ins + t_ins + h_ins
            
            # 9. Refresh Materialized Views
            self.loader.refresh_views()
            
            # Finalize Log
            logger.info("ETL run finished successfully.")
            self._log_run_end(
                run_id=run_id,
                status="SUCCESS",
                rows_downloaded=rows_downloaded,
                rows_validated=rows_validated,
                rows_rejected=rows_rejected,
                rows_inserted=rows_inserted,
                checksum=checksum
            )
            
            # Archive raw file
            archive_path = etl_config.ARCHIVE_DIR / file_path.name
            file_path.rename(archive_path)
            logger.info(f"Raw dataset archived to: {archive_path.name}")
            
        except Exception as e:
            error_msg = str(e)
            error_tb = traceback.format_exc()
            logger.error(f"ETL Execution Failure: {error_msg}\n{error_tb}")
            self._log_run_end(
                run_id=run_id,
                status="FAILED",
                rows_downloaded=rows_downloaded,
                rows_validated=rows_validated,
                rows_rejected=rows_rejected,
                rows_inserted=rows_inserted,
                checksum=checksum,
                error_msg=error_msg,
                error_tb=error_tb
            )
            # Cleanup temp raw file
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            raise


if __name__ == "__main__":
    # If run directly, run ETL pipeline
    runner = ETLRunner()
    runner.run(force=True)
