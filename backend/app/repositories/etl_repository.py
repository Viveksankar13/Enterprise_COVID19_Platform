from datetime import datetime
from typing import List, Optional, Any, Dict
from uuid import UUID
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.etl_log import ETLLog
from app.repositories.base import BaseRepository


class ETLRepository(BaseRepository[ETLLog]):
    """
    Repository for tracking ETL operational logs and pipeline executions.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(ETLLog, db_session)

    async def get_latest_runs(self, limit: int = 10) -> List[ETLLog]:
        """
        Retrieves the most recent ETL pipeline runs.
        """
        stmt = select(ETLLog).order_by(desc(ETLLog.started_at)).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_active_runs(self) -> List[ETLLog]:
        """
        Lists any currently executing ETL pipeline runs.
        """
        stmt = select(ETLLog).where(ETLLog.status == "RUNNING")
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_run_log(
        self,
        pipeline_name: str,
        dag_run_id: Optional[str] = None,
        dataset_url: Optional[str] = None,
    ) -> ETLLog:
        """
        Creates and registers a new ETL run log.
        """
        log = ETLLog(
            pipeline_name=pipeline_name,
            dag_run_id=dag_run_id,
            status="RUNNING",
            dataset_url=dataset_url,
            started_at=datetime.utcnow(),
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def complete_run_log(
        self,
        run_id: UUID,
        status: str,
        rows_downloaded: int = 0,
        rows_validated: int = 0,
        rows_rejected: int = 0,
        rows_inserted: int = 0,
        rows_updated: int = 0,
        dataset_checksum: Optional[str] = None,
        dataset_row_count: Optional[int] = None,
        source_date_min: Optional[datetime] = None,
        source_date_max: Optional[datetime] = None,
        error_message: Optional[str] = None,
        error_traceback: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ETLLog]:
        """
        Finalizes an existing ETL run log with run execution summary.
        """
        log = await self.get(run_id)
        if not log:
            return None
            
        log.status = status
        log.rows_downloaded = rows_downloaded
        log.rows_validated = rows_validated
        log.rows_rejected = rows_rejected
        log.rows_inserted = rows_inserted
        log.rows_updated = rows_updated
        log.completed_at = datetime.utcnow()
        log.dataset_checksum = dataset_checksum
        log.dataset_row_count = dataset_row_count
        log.source_date_min = source_date_min
        log.source_date_max = source_date_max
        log.error_message = error_message
        log.error_traceback = error_traceback
        
        if additional_metadata:
            log.meta_data.update(additional_metadata)
            
        self.db.add(log)
        await self.db.flush()
        return log
