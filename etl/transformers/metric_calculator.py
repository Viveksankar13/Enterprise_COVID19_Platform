import logging
import numpy as np
import pandas as pd

logger = logging.getLogger("etl.metric_calculator")


class MetricCalculator:
    """
    Performs custom derived metric calculations at the dataframe layer.
    Ensures NaN values are cast to correct database-compatible types (None/NaN).
    """

    def calculate_derived_metrics(
        self,
        daily_metrics_df: pd.DataFrame,
        vaccinations_df: pd.DataFrame,
        testing_df: pd.DataFrame
    ) -> None:
        """
        In-place updates of dataframes with calculated metrics.
        """
        logger.info("Calculating custom derived metrics.")

        # Replace numpy NaN values with Python None for direct database insertion compatibility
        self._replace_nan_with_none(daily_metrics_df)
        self._replace_nan_with_none(vaccinations_df)
        self._replace_nan_with_none(testing_df)

    def _replace_nan_with_none(self, df: pd.DataFrame) -> None:
        """
        Converts pandas/numpy NaN elements into Python None objects.
        This is necessary so psycopg2 inserts NULL instead of NaN float string into Postgres.
        """
        df.replace({np.nan: None, pd.NA: None}, inplace=True)
