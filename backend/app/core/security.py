"""
Security Module

Handles authentication, password hashing, and JWT token management.
Following Clean Code: Single Responsibility, Clear naming, Type safety.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context using bcrypt
# Separated from class for reusability and testability
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordHasher:
    """
    Handles password hashing and verification.

    Separated into its own class following Single Responsibility Principle.
    """

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """
        Hash a plain text password.

        Args:
            plain_password: The password to hash

        Returns:
            str: Hashed password
        """
        return pwd_context.hash(plain_password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password: The plain text password
            hashed_password: The hashed password to compare against

        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)


class TokenManager:
    """
    Manages JWT token creation and validation.

    Handles both access and refresh tokens.
    """

    @staticmethod
    def create_access_token(
        subject: str,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new JWT access token.

        Args:
            subject: The subject (usually user ID or username)
            additional_claims: Additional data to include in token

        Returns:
            str: Encoded JWT token
        """
        expires_delta = timedelta(
            minutes=settings.security.access_token_expire_minutes
        )
        return TokenManager._create_token(
            subject=subject,
            expires_delta=expires_delta,
            additional_claims=additional_claims
        )

    @staticmethod
    def create_refresh_token(subject: str) -> str:
        """
        Create a new JWT refresh token.

        Args:
            subject: The subject (usually user ID or username)

        Returns:
            str: Encoded JWT refresh token
        """
        expires_delta = timedelta(days=settings.security.refresh_token_expire_days)
        return TokenManager._create_token(
            subject=subject,
            expires_delta=expires_delta,
            token_type="refresh"
        )

    @staticmethod
    def _create_token(
        subject: str,
        expires_delta: timedelta,
        additional_claims: Optional[Dict[str, Any]] = None,
        token_type: str = "access"
    ) -> str:
        """
        Internal method to create JWT tokens.

        Args:
            subject: The subject of the token
            expires_delta: How long until token expires
            additional_claims: Extra data to include
            token_type: Type of token (access or refresh)

        Returns:
            str: Encoded JWT token
        """
        expire = datetime.utcnow() + expires_delta

        # Build token payload
        to_encode = {
            "sub": subject,
            "exp": expire,
            "type": token_type,
            "iat": datetime.utcnow()
        }

        # Add additional claims if provided
        if additional_claims:
            to_encode.update(additional_claims)

        # Encode token
        encoded_jwt = jwt.encode(
            to_encode,
            settings.security.secret_key,
            algorithm=settings.security.algorithm
        )

        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate a JWT token.

        Args:
            token: The JWT token to decode

        Returns:
            Optional[Dict]: Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.security.secret_key,
                algorithms=[settings.security.algorithm]
            )
            return payload
        except JWTError:
            return None

    @staticmethod
    def verify_token_type(token: str, expected_type: str) -> bool:
        """
        Verify that a token is of the expected type.

        Args:
            token: The JWT token
            expected_type: Expected token type (access or refresh)

        Returns:
            bool: True if token type matches, False otherwise
        """
        payload = TokenManager.decode_token(token)
        if not payload:
            return False

        return payload.get("type") == expected_type

    @staticmethod
    def extract_user_id(token: str) -> Optional[str]:
        """
        Extract user ID from token.

        Args:
            token: The JWT token

        Returns:
            Optional[str]: User ID if token is valid, None otherwise
        """
        payload = TokenManager.decode_token(token)
        if not payload:
            return None

        return payload.get("sub")


# Convenience functions for backward compatibility and ease of use
def hash_password(password: str) -> str:
    """Hash a password."""
    return PasswordHasher.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password."""
    return PasswordHasher.verify_password(plain_password, hashed_password)


def create_access_token(subject: str, **kwargs) -> str:
    """Create an access token."""
    return TokenManager.create_access_token(subject, kwargs if kwargs else None)


def create_refresh_token(subject: str) -> str:
    """Create a refresh token."""
    return TokenManager.create_refresh_token(subject)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode a token."""
    return TokenManager.decode_token(token)
