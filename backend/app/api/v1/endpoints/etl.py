import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.etl_repository import ETLRepository
from app.api.v1.dependencies.auth import get_current_user, PermissionChecker
from app.core.cache import invalidate_cache_prefix

# Import the ETL module runner directly
from etl.runner import ETLRunner

router = APIRouter()
logger = logging.getLogger("app.api.etl")


def run_etl_background(force: bool):
    """
    Background worker task to trigger ingestion pipeline.
    """
    logger.info("ETL Background task triggered.")
    try:
        runner = ETLRunner()
        runner.run(force=force)
        # Invalidate all cache on success because fresh data has been ingested
        invalidate_cache_prefix("")
        logger.info("ETL Background task completed and cache invalidated.")
    except Exception as e:
        logger.error(f"ETL Background task failed: {e}")


@router.get("/runs", summary="List historical ETL pipeline executions")
async def get_etl_runs(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(PermissionChecker("etl", "read"))
):
    """
    Returns latest historical operational run logs.
    """
    repo = ETLRepository(db)
    return await repo.get_latest_runs(limit=limit)


@router.get("/active", summary="List active running ingestion tasks")
async def get_active_runs(
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(PermissionChecker("etl", "read"))
):
    """
    Returns lists of currently active ETL executions.
    """
    repo = ETLRepository(db)
    return await repo.get_active_runs()


@router.post("/trigger", status_code=status.HTTP_202_ACCEPTED, summary="Manually trigger ETL data load")
async def trigger_etl(
    background_tasks: BackgroundTasks,
    force: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(PermissionChecker("etl", "write"))
):
    """
    Asynchronously triggers the ingestion pipeline to refresh datasets and views.
    """
    repo = ETLRepository(db)
    active_runs = await repo.get_active_runs()
    
    if active_runs:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An ETL pipeline run is already in progress."
        )
        
    background_tasks.add_task(run_etl_background, force)
    return {"message": "ETL pipeline triggered successfully in background."}
