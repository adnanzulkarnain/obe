"""
User Repository

Data access layer for User and authentication.
Following Clean Code: Security best practices, Clear separation.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.models.user_models import User, Role, UserRole, UserType


class UserRepository(BaseRepository[User]):
    """
    Repository for User operations.

    Handles user authentication and authorization data access.
    """

    def __init__(self, session: Session):
        """
        Initialize User repository.

        Args:
            session: Database session
        """
        super().__init__(User, session)

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: Username to search for

        Returns:
            Optional[User]: User if found, None otherwise
        """
        return self.get_one_by_criteria(username=username)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: Email address to search for

        Returns:
            Optional[User]: User if found, None otherwise
        """
        return self.get_one_by_criteria(email=email)

    def get_with_roles(self, user_id: int) -> Optional[User]:
        """
        Get user with their roles eagerly loaded.

        Args:
            user_id: User ID

        Returns:
            Optional[User]: User with roles if found
        """
        return self.session.query(User).options(
            joinedload(User.roles).joinedload(UserRole.role)
        ).filter(User.id_user == user_id).first()

    def check_username_exists(self, username: str) -> bool:
        """
        Check if username already exists.

        Args:
            username: Username to check

        Returns:
            bool: True if exists, False otherwise
        """
        return self.exists(username=username)

    def check_email_exists(self, email: str) -> bool:
        """
        Check if email already exists.

        Args:
            email: Email to check

        Returns:
            bool: True if exists, False otherwise
        """
        return self.exists(email=email)

    def get_by_type(self, user_type: UserType) -> List[User]:
        """
        Get all users of a specific type.

        Args:
            user_type: Type of user (dosen, mahasiswa, admin, kaprodi)

        Returns:
            List[User]: List of users of that type
        """
        return self.get_by_criteria(user_type=user_type, is_active=True)

    def get_by_ref_id(self, ref_id: str) -> Optional[User]:
        """
        Get user by reference ID (id_dosen or nim).

        Args:
            ref_id: Reference ID

        Returns:
            Optional[User]: User if found
        """
        return self.get_one_by_criteria(ref_id=ref_id)

    def activate_user(self, user_id: int) -> User:
        """
        Activate a user account.

        Args:
            user_id: User ID

        Returns:
            User: Activated user
        """
        return self.update_by_id(user_id, is_active=True)

    def deactivate_user(self, user_id: int) -> User:
        """
        Deactivate a user account.

        Args:
            user_id: User ID

        Returns:
            User: Deactivated user
        """
        return self.update_by_id(user_id, is_active=False)


class RoleRepository(BaseRepository[Role]):
    """
    Repository for Role operations.
    """

    def __init__(self, session: Session):
        """
        Initialize Role repository.

        Args:
            session: Database session
        """
        super().__init__(Role, session)

    def get_by_name(self, role_name: str) -> Optional[Role]:
        """
        Get role by name.

        Args:
            role_name: Role name

        Returns:
            Optional[Role]: Role if found
        """
        return self.get_one_by_criteria(role_name=role_name)

    def check_role_exists(self, role_name: str) -> bool:
        """
        Check if role exists.

        Args:
            role_name: Role name to check

        Returns:
            bool: True if exists, False otherwise
        """
        return self.exists(role_name=role_name)
