"""
User Service

Business logic for user management operations.
Following Clean Code: Single Responsibility, Business logic separation.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.infrastructure.repositories.user_repository import UserRepository, RoleRepository
from app.infrastructure.models.user_models import User, UserType
from app.presentation.schemas.user_schemas import UserUpdate
from app.domain.exceptions import EntityNotFoundException, DuplicateEntityException


class UserService:
    """
    Handles user management operations.

    Responsibilities:
    - User CRUD operations
    - User role management
    - User activation/deactivation
    """

    def __init__(self, session: Session):
        """
        Initialize user service.

        Args:
            session: Database session for data access
        """
        self.session = session
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)

    def get_user_by_id(self, user_id: int) -> User:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User: User instance

        Raises:
            EntityNotFoundException: If user not found
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException("User", str(user_id))
        return user

    def get_user_with_roles(self, user_id: int) -> User:
        """
        Get user with roles eagerly loaded.

        Args:
            user_id: User ID

        Returns:
            User: User instance with roles

        Raises:
            EntityNotFoundException: If user not found
        """
        user = self.user_repo.get_with_roles(user_id)
        if not user:
            raise EntityNotFoundException("User", str(user_id))
        return user

    def get_all_users(
        self,
        skip: int = 0,
        limit: int = 100,
        user_type: Optional[UserType] = None
    ) -> List[User]:
        """
        Get all users with optional filtering.

        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            user_type: Optional filter by user type

        Returns:
            List[User]: List of users
        """
        if user_type:
            return self.user_repo.get_by_type(user_type)

        return self.user_repo.get_all(skip=skip, limit=limit)

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        Update user information.

        Args:
            user_id: User ID to update
            user_data: Updated user data

        Returns:
            User: Updated user

        Raises:
            EntityNotFoundException: If user not found
            DuplicateEntityException: If email already exists
        """
        user = self.get_user_by_id(user_id)

        # Check for duplicate email if being updated
        if user_data.email and user_data.email != user.email:
            if self.user_repo.check_email_exists(user_data.email):
                raise DuplicateEntityException("User", "email", user_data.email)

        # Update only provided fields
        update_dict = user_data.model_dump(exclude_unset=True)
        return self.user_repo.update(user, **update_dict)

    def activate_user(self, user_id: int) -> User:
        """
        Activate a user account.

        Args:
            user_id: User ID to activate

        Returns:
            User: Activated user

        Raises:
            EntityNotFoundException: If user not found
        """
        return self.user_repo.activate_user(user_id)

    def deactivate_user(self, user_id: int) -> User:
        """
        Deactivate a user account.

        Args:
            user_id: User ID to deactivate

        Returns:
            User: Deactivated user

        Raises:
            EntityNotFoundException: If user not found
        """
        return self.user_repo.deactivate_user(user_id)

    def delete_user(self, user_id: int) -> None:
        """
        Delete a user (hard delete).

        Warning: This permanently deletes the user.
        Consider using deactivate_user instead.

        Args:
            user_id: User ID to delete

        Raises:
            EntityNotFoundException: If user not found
        """
        self.user_repo.delete_by_id(user_id)

    def count_users(self, user_type: Optional[UserType] = None) -> int:
        """
        Count total number of users.

        Args:
            user_type: Optional filter by user type

        Returns:
            int: Number of users
        """
        if user_type:
            return self.user_repo.count(user_type=user_type, is_active=True)
        return self.user_repo.count(is_active=True)

    def search_users(self, query: str) -> List[User]:
        """
        Search users by username or email.

        Args:
            query: Search query

        Returns:
            List[User]: List of matching users
        """
        from sqlalchemy import or_

        return self.session.query(User).filter(
            or_(
                User.username.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            ),
            User.is_active == True
        ).all()

    def assign_role(self, user_id: int, role_name: str) -> User:
        """
        Assign a role to user.

        Args:
            user_id: User ID
            role_name: Name of role to assign

        Returns:
            User: User with updated roles

        Raises:
            EntityNotFoundException: If user or role not found
        """
        from app.infrastructure.models.user_models import UserRole

        user = self.get_user_by_id(user_id)
        role = self.role_repo.get_by_name(role_name)

        if not role:
            raise EntityNotFoundException("Role", role_name)

        # Check if user already has this role
        existing = self.session.query(UserRole).filter_by(
            id_user=user_id,
            id_role=role.id_role
        ).first()

        if not existing:
            # Create user-role association
            user_role = UserRole(id_user=user_id, id_role=role.id_role)
            self.session.add(user_role)
            self.session.commit()

        return self.get_user_with_roles(user_id)

    def remove_role(self, user_id: int, role_name: str) -> User:
        """
        Remove a role from user.

        Args:
            user_id: User ID
            role_name: Name of role to remove

        Returns:
            User: User with updated roles

        Raises:
            EntityNotFoundException: If user or role not found
        """
        from app.infrastructure.models.user_models import UserRole

        user = self.get_user_by_id(user_id)
        role = self.role_repo.get_by_name(role_name)

        if not role:
            raise EntityNotFoundException("Role", role_name)

        # Remove user-role association
        self.session.query(UserRole).filter_by(
            id_user=user_id,
            id_role=role.id_role
        ).delete()
        self.session.commit()

        return self.get_user_with_roles(user_id)
