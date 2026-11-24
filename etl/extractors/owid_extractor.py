import hashlib
import time
import logging
from pathlib import Path
from typing import Tuple, List, Optional
import requests
import pandas as pd
from etl.config import etl_config

logger = logging.getLogger("etl.extractor")


class OWIDExtractor:
    """
    Downloads the COVID-19 dataset from Our World in Data, validates checksums,
    and detects schema drift before passing it to transformers.
    """

    # Expected column subset mapping to verify schema drift
    REQUIRED_COLUMNS: List[str] = [
        "iso_code", "continent", "location", "date",
        "new_cases", "total_cases", "new_deaths", "total_deaths",
        "reproduction_rate", "stringency_index",
        "people_vaccinated", "people_fully_vaccinated", "total_boosters",
        "new_vaccinations", "new_tests", "total_tests", "positive_rate",
        "icu_patients", "hosp_patients", "weekly_icu_admissions", "weekly_hosp_admissions",
        "population", "population_density", "median_age", "gdp_per_capita", "life_expectancy", "human_development_index"
    ]

    def __init__(self) -> None:
        self.url = etl_config.OWID_DATASET_URL
        self.raw_dir = etl_config.RAW_DIR

    def download_dataset(self) -> Tuple[Path, str]:
        """
        Streams and downloads the raw CSV file to raw directory.
        Calculates SHA-256 checksum on-the-fly.
        Returns: (file_path, sha256_checksum)
        """
        timestamp = int(time.time())
        dest_path = self.raw_dir / f"owid_covid_data_{timestamp}.csv"
        
        logger.info(f"Downloading dataset from: {self.url}")
        sha256_hash = hashlib.sha256()
        
        start_time = time.time()
        response = requests.get(self.url, stream=True, timeout=120)
        response.raise_for_status()
        
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                if chunk:
                    f.write(chunk)
                    sha256_hash.update(chunk)
                    
        elapsed = time.time() - start_time
        checksum = sha256_hash.hexdigest()
        
        logger.info(
            f"Download completed in {elapsed:.2f} seconds. "
            f"Checksum: {checksum} | File: {dest_path.name}"
        )
        return dest_path, checksum

    def detect_schema_drift(self, file_path: Path) -> Tuple[bool, List[str]]:
        """
        Loads only the header of the downloaded CSV and checks against REQUIRED_COLUMNS.
        Returns: (has_drifted, missing_columns)
        """
        logger.info(f"Analyzing downloaded dataset headers in: {file_path.name}")
        try:
            # Read only first line to parse columns without loading massive file
            df_head = pd.read_csv(file_path, nrows=0)
            actual_columns = list(df_head.columns)
            
            missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in actual_columns]
            
            if missing_cols:
                logger.error(f"Schema Drift Detected! Missing columns: {missing_cols}")
                return True, missing_cols
                
            logger.info("Schema verification completed. No missing required columns.")
            return False, []
        except Exception as e:
            logger.error(f"Failed to read headers for schema drift validation: {e}")
            raise
