import logging
from typing import List, Dict, Any, Tuple
import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
from etl.config import etl_config

logger = logging.getLogger("etl.loader")


class PostgresLoader:
    """
    Bulk loads normalized pandas DataFrames into PostgreSQL database.
    Implements ON CONFLICT DO UPDATE (upsert) behavior using fast psycopg2 batch inserts.
    """

    def __init__(self) -> None:
        self.conn_url = etl_config.DATABASE_URL
        self.batch_size = etl_config.BATCH_SIZE

    def _get_connection(self) -> Any: # type: ignore
        return psycopg2.connect(self.conn_url)

    def bulk_upsert(
        self, 
        table_name: str, 
        df: Any,  # pandas DataFrame # type: ignore
        conflict_keys: List[str], 
        update_cols: List[str]
    ) -> Tuple[int, int]:
        """
        Executes a bulk upsert operation on the target table.
        Returns: (inserted_count, updated_count) - approximated.
        """
        if df.empty:
            return 0, 0

        columns = list(df.columns)
        
        # Build dynamic SQL statement
        # INSERT INTO table (col1, col2) VALUES %s ON CONFLICT (key1, key2) DO UPDATE SET col1 = EXCLUDED.col1
        placeholders_str = "%s"
        columns_str = ", ".join(columns)
        conflict_str = ", ".join(conflict_keys)
        
        update_clauses = [f"{col} = EXCLUDED.{col}" for col in update_cols]
        update_str = ", ".join(update_clauses)
        
        query = f"""
            INSERT INTO {table_name} ({columns_str})
            VALUES %s
            ON CONFLICT ({conflict_str})
            DO UPDATE SET {update_str};
        """
        
        # Convert dataframe rows to tuples for insert
        # Replace NaN/NaT with None to ensure psycopg2 maps them to SQL NULL
        df_none = df.astype(object).where(pd.notnull(df), None)
        data_tuples = [tuple(x) for x in df_none.to_numpy()]
        
        conn = self._get_connection()
        cur = conn.cursor()
        
        total_rows = len(df)
        logger.info(f"Loading {total_rows} rows into '{table_name}' table in batches of {self.batch_size}.")
        
        try:
            for i in range(0, total_rows, self.batch_size):
                batch = data_tuples[i:i + self.batch_size]
                execute_values(cur, query, batch)
            conn.commit()
            logger.info(f"Successfully upserted {total_rows} rows into '{table_name}'.")
            return total_rows, 0
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed loading table '{table_name}': {e}")
            raise
        finally:
            cur.close()
            conn.close()

    def refresh_views(self) -> None:
        """
        Invokes the stored procedure to refresh all analytical materialized views.
        """
        logger.info("Invoking materialized view refresh procedure...")
        conn = self._get_connection()
        cur = conn.cursor()
        try:
            cur.execute("CALL refresh_all_materialized_views();")
            conn.commit()
            logger.info("Materialized views successfully refreshed.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to refresh materialized views: {e}")
            raise
        finally:
            cur.close()
            conn.close()
