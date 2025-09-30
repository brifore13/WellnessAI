"""
Base repository with common database operations.
Provides reusable CRUD operations for children repositories
"""
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

# Generic type variable bound to SQLAlchemy Base
# Allows BaseRepository to work with any model class
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository implementing common CRUD operations
    All sepcific repositories inherit from this class
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository with model class and db session
        Args:
            model: SQLAlchemy model class
            db: Async database session
        """
        self.model = model
        self.db = db

    async def create(self, **kwargs: Any) -> ModelType:
        """
        Create a new record.
        Args:
            **kwargs: Field values for the new record
        Returns:
            Created model instance with ID assigned
        """
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Get a single record by primary key ID
        Args:
            id: Primary key value
        Returns:
            Model instance if found, None otherwise
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[Any] = None
    ) -> List[ModelType]:
        """
        Get all records with pagination and optional ordering.
        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            order_by: Optional SQLAlchemy column to order by
        Returns:
            List of model instances
        """
        query = select(self.model).offset(skip).limit(limit)

        if order_by is not None:
            query = query.order_by(order_by)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, id: int, **kwargs: Any) -> Optional[ModelType]:
        """
        Update a record by ID.
        Args:
            id: Primary key value
            **kwargs: Fields to update with new values
        Returns:
            Updated model instance if found, None otherwise
        """
        # Get existing record
        instance = await self.get_by_id(id)
        if not instance:
            return None
        # Update fields
        for key, value in kwargs.items():
            setattr(instance, key, value)

        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def delete(self, id: int) -> bool:
        """
        Delete a record by ID.
        Args:
            id: Primary key value
        Returns:
            True if deleted, False if not found
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False
        
        await self.db.delete(instance)
        await self.db.commit()
        return True

    async def count(self) -> int:
        """
        Count total number of records
        Returns:
            Total record count
        """
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.count().select_from(self.model))
        )
        return result.scalar_one()

    async def exists(self, id: int) -> bool:
        """
        Check if a record exists by ID.

        Args:
            id: Primary key value
        Returns:
            True if exists, False otherwise
        """
        result = await self.db.execute(
            select(self.model.id).where(self.model.id == id)
        )
        return result.scalar_one_or_none() is not None

