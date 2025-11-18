"""
Authentication Service

Business logic for user authentication and authorization.
Following Clean Code: Single Responsibility, Clear intent, Type safety.
"""

from typing import Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    TokenManager
)
from app.core.config import settings
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.models.user_models import User
from app.presentation.schemas.user_schemas import (
    UserCreate,
    LoginRequest,
    TokenResponse
)
from app.domain.exceptions import (
    AuthenticationException,
    DuplicateEntityException,
    EntityNotFoundException
)


class AuthenticationService:
    """
    Handles user authentication operations.

    Responsibilities:
    - User registration
    - User login
    - Token generation and validation
    - Password verification
    """

    def __init__(self, session: Session):
        """
        Initialize authentication service.

        Args:
            session: Database session for data access
        """
        self.session = session
        self.user_repo = UserRepository(session)

    def register_user(self, user_data: UserCreate) -> User:
        """
        Register a new user.

        Args:
            user_data: User registration data

        Returns:
            User: Newly created user

        Raises:
            DuplicateEntityException: If username or email already exists
        """
        # Check for duplicate username
        if self.user_repo.check_username_exists(user_data.username):
            raise DuplicateEntityException(
                "User",
                "username",
                user_data.username
            )

        # Check for duplicate email
        if self.user_repo.check_email_exists(user_data.email):
            raise DuplicateEntityException(
                "User",
                "email",
                user_data.email
            )

        # Hash password
        password_hash = hash_password(user_data.password)

        # Create user
        user = self.user_repo.create(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            user_type=user_data.user_type,
            ref_id=user_data.ref_id,
            is_active=True
        )

        return user

    def authenticate_user(self, login_data: LoginRequest) -> User:
        """
        Authenticate user with username/email and password.

        Args:
            login_data: Login credentials

        Returns:
            User: Authenticated user

        Raises:
            AuthenticationException: If credentials are invalid
        """
        # Try to find user by username or email
        user = self._find_user_by_username_or_email(login_data.username_or_email)

        if not user:
            raise AuthenticationException("Username atau email tidak ditemukan")

        # Verify password
        if not self._verify_user_password(user, login_data.password):
            raise AuthenticationException("Password salah")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationException("Akun tidak aktif")

        # Update last login
        self._update_last_login(user)

        return user

    def generate_tokens(self, user: User) -> TokenResponse:
        """
        Generate access and refresh tokens for user.

        Args:
            user: User to generate tokens for

        Returns:
            TokenResponse: Access and refresh tokens
        """
        # Create access token with user claims
        access_token = create_access_token(
            subject=str(user.id_user),
            user_type=user.user_type.value,
            username=user.username
        )

        # Create refresh token
        refresh_token = create_refresh_token(subject=str(user.id_user))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.security.access_token_expire_minutes * 60
        )

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Generate new access token from refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            TokenResponse: New access and refresh tokens

        Raises:
            AuthenticationException: If refresh token is invalid
        """
        # Verify refresh token type
        if not TokenManager.verify_token_type(refresh_token, "refresh"):
            raise AuthenticationException("Token refresh tidak valid")

        # Extract user ID from token
        user_id = TokenManager.extract_user_id(refresh_token)
        if not user_id:
            raise AuthenticationException("Token refresh tidak valid")

        # Get user from database
        user = self.user_repo.get_by_id(int(user_id))
        if not user or not user.is_active:
            raise AuthenticationException("User tidak ditemukan atau tidak aktif")

        # Generate new tokens
        return self.generate_tokens(user)

    def validate_token(self, token: str) -> Optional[User]:
        """
        Validate access token and return user.

        Args:
            token: JWT access token

        Returns:
            Optional[User]: User if token is valid, None otherwise
        """
        # Decode token
        payload = decode_token(token)
        if not payload:
            return None

        # Extract user ID
        user_id = payload.get("sub")
        if not user_id:
            return None

        # Get user from database
        user = self.user_repo.get_by_id(int(user_id))
        if not user or not user.is_active:
            return None

        return user

    def change_password(
        self,
        user: User,
        old_password: str,
        new_password: str
    ) -> None:
        """
        Change user password.

        Args:
            user: User whose password to change
            old_password: Current password
            new_password: New password

        Raises:
            AuthenticationException: If old password is incorrect
        """
        # Verify old password
        if not verify_password(old_password, user.password_hash):
            raise AuthenticationException("Password lama salah")

        # Hash new password
        new_password_hash = hash_password(new_password)

        # Update password
        self.user_repo.update(user, password_hash=new_password_hash)

    # Private helper methods

    def _find_user_by_username_or_email(self, username_or_email: str) -> Optional[User]:
        """
        Find user by username or email.

        Args:
            username_or_email: Username or email to search for

        Returns:
            Optional[User]: User if found, None otherwise
        """
        # Try username first
        user = self.user_repo.get_by_username(username_or_email)
        if user:
            return user

        # Try email
        user = self.user_repo.get_by_email(username_or_email)
        return user

    def _verify_user_password(self, user: User, password: str) -> bool:
        """
        Verify user password.

        Args:
            user: User to verify password for
            password: Password to verify

        Returns:
            bool: True if password is correct, False otherwise
        """
        return verify_password(password, user.password_hash)

    def _update_last_login(self, user: User) -> None:
        """
        Update user's last login timestamp.

        Args:
            user: User to update
        """
        self.user_repo.update(user, last_login=datetime.utcnow())
