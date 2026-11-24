from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, Role, Permission
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository for managing User accounts, Roles, and RBAC permissions.
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieves a user account by email (case-insensitive).
        Loads the associated Role.
        """
        stmt = (
            select(User)
            .where(func.lower(User.email) == func.lower(email))
            .options(selectinload(User.role))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieves a user account by username.
        Loads the associated Role.
        """
        stmt = (
            select(User)
            .where(User.username == username)
            .options(selectinload(User.role))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_permissions_for_role(self, role_id: int) -> List[Permission]:
        """
        Lists all permissions mapped to a given Role.
        """
        stmt = select(Permission).where(Permission.role_id == role_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def increment_login_stats(self, user: User, last_login: datetime) -> None:
        """
        Updates cumulative user statistics on successful authentication.
        """
        user.login_count += 1
        user.last_login_at = last_login
        self.db.add(user)
        await self.db.flush()
            
    async def get_active_roles(self) -> List[Role]:
        """
        Lists active roles available within the platform.
        """
        stmt = select(Role).where(Role.is_active == True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
