import os
from pathlib import Path
from dotenv import load_dotenv

# Load workspace environment variables
load_dotenv()

class ETLConfig:
    """
    Configuration settings and path initializations for the ETL engine.
    """
    OWID_DATASET_URL: str = os.getenv(
        "OWID_DATASET_URL", 
        "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    )
    
    # Base Data directory
    DATA_DIR: Path = Path(os.getenv("ETL_DATA_DIR", "data"))
    
    # Subdirectories
    RAW_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    ARCHIVE_DIR: Path = DATA_DIR / "archive"
    LOGS_DIR: Path = Path(os.getenv("ETL_LOGS_DIR", "logs/etl"))
    
    # Operational parameters
    BATCH_SIZE: int = int(os.getenv("ETL_BATCH_SIZE", "5000"))
    
    @property
    def DATABASE_URL(self) -> str:
        url = os.getenv("DATABASE_URL")
        if not url:
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            user = os.getenv("POSTGRES_USER", "covid_admin")
            password = os.getenv("POSTGRES_PASSWORD", "change_me_strong_password")
            db = os.getenv("POSTGRES_DB", "covid19_analytics")
            return f"postgresql://{user}:{password}@{host}:{port}/{db}"
        return url

    def __init__(self) -> None:
        # Auto-create all required directory structures
        self.RAW_DIR.mkdir(parents=True, exist_ok=True)
        self.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        self.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)


etl_config = ETLConfig()
