from typing import Any, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository class containing common database actions for models.
    """

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self.model = model
        self.db = db_session

    async def get(self, id: Any) -> Optional[ModelType]:
        """
        Fetch a single record by its primary key ID.
        """
        return await self.db.get(self.model, id)

    async def get_by_attribute(self, attr_name: str, value: Any) -> Optional[ModelType]:
        """
        Fetch a single record matching an attribute value.
        """
        attr = getattr(self.model, attr_name)
        stmt = select(self.model).where(attr == value)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list(
        self, skip: int = 0, limit: int = 100, order_by: Optional[Any] = None
    ) -> List[ModelType]:
        """
        Fetch a paginated list of records.
        """
        stmt = select(self.model).offset(skip).limit(limit)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj_in: ModelType) -> ModelType:
        """
        Insert a new model instance.
        """
        self.db.add(obj_in)
        await self.db.flush()
        return obj_in

    async def update(self, db_obj: ModelType, update_data: dict[str, Any]) -> ModelType:
        """
        Update an existing model instance with the provided fields.
        """
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        self.db.add(db_obj)
        await self.db.flush()
        return db_obj

    async def delete(self, id: Any) -> Optional[ModelType]:
        """
        Delete a record by ID.
        """
        obj = await self.get(id)
        if obj:
            await self.db.delete(obj)
            await self.db.flush()
        return obj
