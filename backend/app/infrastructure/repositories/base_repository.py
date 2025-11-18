"""
Base Repository

Generic repository implementation following Repository pattern.
Following Clean Code: DRY, Generic programming, Type safety.
"""

from typing import TypeVar, Generic, Type, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.infrastructure.database import Base
from app.domain.exceptions import EntityNotFoundException

# Generic type for database models
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic base repository for CRUD operations.

    Provides common database operations for all entities.
    Following Single Responsibility and DRY principles.

    Type Parameters:
        ModelType: The SQLAlchemy model class
    """

    def __init__(self, model: Type[ModelType], session: Session):
        """
        Initialize repository with model and session.

        Args:
            model: SQLAlchemy model class
            session: Database session
        """
        self.model = model
        self.session = session

    def create(self, **kwargs) -> ModelType:
        """
        Create a new entity.

        Args:
            **kwargs: Entity attributes

        Returns:
            ModelType: Created entity instance
        """
        entity = self.model(**kwargs)
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def get_by_id(self, entity_id: Any) -> Optional[ModelType]:
        """
        Get entity by primary key.

        Args:
            entity_id: Primary key value

        Returns:
            Optional[ModelType]: Entity if found, None otherwise
        """
        return self.session.query(self.model).get(entity_id)

    def get_by_id_or_fail(self, entity_id: Any) -> ModelType:
        """
        Get entity by ID or raise exception if not found.

        Args:
            entity_id: Primary key value

        Returns:
            ModelType: Entity instance

        Raises:
            EntityNotFoundException: If entity not found
        """
        entity = self.get_by_id(entity_id)
        if not entity:
            raise EntityNotFoundException(
                self.model.__name__,
                str(entity_id)
            )
        return entity

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        Get all entities with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Column name to order by

        Returns:
            List[ModelType]: List of entities
        """
        query = self.session.query(self.model)

        if order_by:
            query = query.order_by(order_by)

        return query.offset(skip).limit(limit).all()

    def get_by_criteria(self, **criteria) -> List[ModelType]:
        """
        Get entities matching criteria.

        Args:
            **criteria: Filter criteria as key-value pairs

        Returns:
            List[ModelType]: List of matching entities
        """
        return self.session.query(self.model).filter_by(**criteria).all()

    def get_one_by_criteria(self, **criteria) -> Optional[ModelType]:
        """
        Get single entity matching criteria.

        Args:
            **criteria: Filter criteria as key-value pairs

        Returns:
            Optional[ModelType]: Entity if found, None otherwise
        """
        return self.session.query(self.model).filter_by(**criteria).first()

    def exists(self, **criteria) -> bool:
        """
        Check if entity exists with given criteria.

        Args:
            **criteria: Filter criteria as key-value pairs

        Returns:
            bool: True if entity exists, False otherwise
        """
        return self.session.query(
            self.session.query(self.model).filter_by(**criteria).exists()
        ).scalar()

    def update(self, entity: ModelType, **update_data) -> ModelType:
        """
        Update entity with new data.

        Args:
            entity: Entity to update
            **update_data: Fields to update

        Returns:
            ModelType: Updated entity
        """
        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        self.session.commit()
        self.session.refresh(entity)
        return entity

    def update_by_id(self, entity_id: Any, **update_data) -> ModelType:
        """
        Update entity by ID.

        Args:
            entity_id: Primary key value
            **update_data: Fields to update

        Returns:
            ModelType: Updated entity

        Raises:
            EntityNotFoundException: If entity not found
        """
        entity = self.get_by_id_or_fail(entity_id)
        return self.update(entity, **update_data)

    def delete(self, entity: ModelType) -> None:
        """
        Delete entity (hard delete).

        Args:
            entity: Entity to delete
        """
        self.session.delete(entity)
        self.session.commit()

    def delete_by_id(self, entity_id: Any) -> None:
        """
        Delete entity by ID (hard delete).

        Args:
            entity_id: Primary key value

        Raises:
            EntityNotFoundException: If entity not found
        """
        entity = self.get_by_id_or_fail(entity_id)
        self.delete(entity)

    def soft_delete(self, entity: ModelType) -> ModelType:
        """
        Soft delete entity by setting is_active = False.

        Args:
            entity: Entity to soft delete

        Returns:
            ModelType: Updated entity with is_active = False

        Note:
            Entity must have is_active field
        """
        if not hasattr(entity, 'is_active'):
            raise AttributeError(
                f"{self.model.__name__} does not support soft delete "
                "(missing is_active field)"
            )

        return self.update(entity, is_active=False)

    def count(self, **criteria) -> int:
        """
        Count entities matching criteria.

        Args:
            **criteria: Filter criteria as key-value pairs

        Returns:
            int: Number of matching entities
        """
        query = self.session.query(self.model)
        if criteria:
            query = query.filter_by(**criteria)
        return query.count()

    def bulk_create(self, entities: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Create multiple entities in one transaction.

        Args:
            entities: List of entity data dictionaries

        Returns:
            List[ModelType]: List of created entities
        """
        instances = [self.model(**data) for data in entities]
        self.session.bulk_save_objects(instances, return_defaults=True)
        self.session.commit()
        return instances

    def refresh(self, entity: ModelType) -> ModelType:
        """
        Refresh entity from database.

        Args:
            entity: Entity to refresh

        Returns:
            ModelType: Refreshed entity
        """
        self.session.refresh(entity)
        return entity

    def commit(self) -> None:
        """Commit current transaction."""
        self.session.commit()

    def rollback(self) -> None:
        """Rollback current transaction."""
        self.session.rollback()
