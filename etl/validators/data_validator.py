import logging
from pathlib import Path
from typing import Tuple
import pandas as pd
from etl.config import etl_config

logger = logging.getLogger("etl.validator")


class DataValidator:
    """
    Performs vectorized data validation on the loaded Pandas DataFrame.
    Identifies invalid rows, logs them, and exports rejected rows for audit tracking.
    """

    def __init__(self) -> None:
        self.processed_dir = etl_config.PROCESSED_DIR

    def validate(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
        """
        Validates the dataset.
        Checks:
        - iso_code must be non-null and between 2 and 8 characters.
        - date must be parseable.
        - total_cases and total_deaths must be non-negative if present.
        
        Returns: (validated_df, rejected_row_count)
        """
        logger.info(f"Initiating validation checks on {len(df)} records.")
        
        # 1. Check for missing critical fields
        is_valid_iso = df["iso_code"].notna() & (df["iso_code"].astype(str).str.len().between(2, 8))
        is_valid_date = df["date"].notna()
        
        # 2. Check for negative cumulative values
        # If total_cases or total_deaths are negative, mark as invalid
        is_valid_cases = df["total_cases"].isna() | (df["total_cases"] >= 0)
        is_valid_deaths = df["total_deaths"].isna() | (df["total_deaths"] >= 0)
        
        # Combine validation masks
        valid_mask = is_valid_iso & is_valid_date & is_valid_cases & is_valid_deaths
        
        # Split valid and invalid rows
        valid_df = df[valid_mask].copy()
        invalid_df = df[~valid_mask].copy()
        
        rejected_count = len(invalid_df)
        
        if rejected_count > 0:
            logger.warning(f"Validation complete: rejected {rejected_count} invalid records.")
            # Export rejected rows for developer review
            rejected_path = self.processed_dir / "rejected_rows.csv"
            invalid_df.to_csv(rejected_path, index=False)
            logger.info(f"Rejected rows written to: {rejected_path.name}")
        else:
            logger.info("Validation complete: 0 records rejected.")
            
        return valid_df, rejected_count
