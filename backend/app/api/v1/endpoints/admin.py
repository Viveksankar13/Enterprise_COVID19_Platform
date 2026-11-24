import logging
import re
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload

from app.database.session import get_db, async_engine
from app.api.v1.dependencies.auth import get_current_user, PermissionChecker
from app.core.cache import invalidate_cache_prefix
from app.models.user import User
from app.schemas.auth import UserOut

router = APIRouter()
logger = logging.getLogger("app.api.admin")


@router.post("/cache/clear", status_code=status.HTTP_200_OK, summary="Clear Redis API cache")
async def clear_cache(
    _current_user = Depends(PermissionChecker("admin", "write"))
):
    """
    Clears all cached API response payloads in Redis.
    """
    try:
        # Invalidates everything starting with empty string prefix (all api cache keys)
        invalidate_cache_prefix("")
        return {"message": "All cached response metrics cleared successfully."}
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Cache clearing failed: {str(e)}"
        )


@router.get("/db-pool", summary="Get Database connection pool stats")
async def get_db_pool(
    _current_user = Depends(PermissionChecker("admin", "read"))
):
    """
    Returns diagnostic details on the active database connection pool.
    """
    try:
        pool = async_engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
        }
    except Exception as e:
        logger.error(f"Failed to fetch DB pool diagnostics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving database pool analytics"
        )


class QueryRequest(BaseModel):
    sql: str

@router.post("/query", summary="Run read-only database query")
async def execute_query(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(PermissionChecker("sql_explorer", "write"))
):
    """
    Executes a read-only SELECT query against the COVID-19 database.
    """
    sql_query = request.sql.strip()
    
    # Security: check if it's read-only
    normalized = sql_query.lower()
    for restricted in ["insert", "update", "delete", "drop", "truncate", "alter", "create", "grant", "revoke"]:
        if re.search(rf"\b{restricted}\b", normalized):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Security Violations: Restricted keyword '{restricted}' is prohibited in queries."
            )
            
    if not normalized.startswith("select") and not normalized.startswith("with"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security Violations: Queries must start with SELECT or WITH statement."
        )

    try:
        result = await db.execute(text(sql_query))
        
        # Check if query returned rows (e.g. SELECT)
        if result.returns_rows:
            columns = list(result.keys())
            rows = [dict(row) for row in result.mappings().all()]
            return {"columns": columns, "rows": rows}
        else:
            return {"columns": [], "rows": [], "message": "Query executed successfully with 0 output rows."}
            
    except Exception as e:
        logger.error(f"SQL execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database execution error: {str(e)}"
        )


@router.get("/users", response_model=List[UserOut], summary="List platform user accounts")
async def list_users(
    db: AsyncSession = Depends(get_db),
    _current_user = Depends(PermissionChecker("admin", "read"))
):
    """
    Returns a list of all registered platform user accounts with role details.
    """
    try:
        stmt = select(User).options(selectinload(User.role)).order_by(User.username)
        result = await db.execute(stmt)
        users = result.scalars().all()
        return users
    except Exception as e:
        logger.error(f"Failed to query users: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error querying database user records"
        )


