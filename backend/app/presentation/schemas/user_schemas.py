"""
User Pydantic Schemas

Request and response schemas for user and authentication endpoints.
Following Clean Code: Validation, Type safety, Clear naming.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime

from app.presentation.schemas.base_schemas import TimestampMixin
from app.infrastructure.models.user_models import UserType


class UserBase(BaseModel):
    """Base user schema with common fields."""

    username: str = Field(
        min_length=3,
        max_length=50,
        description="Unique username"
    )
    email: EmailStr = Field(description="User email address")
    user_type: UserType = Field(description="Type of user")
    ref_id: Optional[str] = Field(
        None,
        max_length=20,
        description="Reference ID (id_dosen or nim)"
    )

    @validator('username')
    def validate_username(cls, v: str) -> str:
        """
        Validate username format.

        Username must be alphanumeric with optional underscores/hyphens.
        """
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v.lower()


class UserCreate(UserBase):
    """
    Schema for creating a new user.

    Includes password field for registration.
    """

    password: str = Field(
        min_length=8,
        max_length=100,
        description="User password (min 8 characters)"
    )

    @validator('password')
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password strength.

        Password must contain:
        - At least 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 number
        """
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class UserUpdate(BaseModel):
    """
    Schema for updating user information.

    All fields are optional - only provided fields will be updated.
    """

    email: Optional[EmailStr] = Field(None, description="New email address")
    is_active: Optional[bool] = Field(None, description="Active status")


class PasswordChange(BaseModel):
    """
    Schema for password change request.

    Requires old password for security verification.
    """

    old_password: str = Field(description="Current password")
    new_password: str = Field(
        min_length=8,
        max_length=100,
        description="New password"
    )

    @validator('new_password')
    def validate_new_password(cls, v: str, values: dict) -> str:
        """Ensure new password is different from old password."""
        if 'old_password' in values and v == values['old_password']:
            raise ValueError('New password must be different from old password')
        return v


class UserResponse(UserBase, TimestampMixin):
    """
    User response schema.

    Excludes sensitive information like password hash.
    """

    id_user: int = Field(description="User ID")
    is_active: bool = Field(description="Whether user account is active")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    roles: List[str] = Field(default_factory=list, description="User roles")

    class Config:
        """Pydantic configuration."""
        from_attributes = True

    @classmethod
    def from_orm_with_roles(cls, user):
        """
        Create UserResponse from ORM User model with roles.

        Args:
            user: SQLAlchemy User instance

        Returns:
            UserResponse: Response schema with role names
        """
        user_dict = {
            'id_user': user.id_user,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type,
            'ref_id': user.ref_id,
            'is_active': user.is_active,
            'last_login': user.last_login,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
            'roles': [ur.role.role_name for ur in user.roles] if user.roles else []
        }
        return cls(**user_dict)


class LoginRequest(BaseModel):
    """
    Login request schema.

    Can authenticate with username or email.
    """

    username_or_email: str = Field(description="Username or email address")
    password: str = Field(description="User password")


class TokenResponse(BaseModel):
    """
    Authentication token response.

    Returns both access and refresh tokens.
    """

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Token expiration time in seconds")


class RefreshTokenRequest(BaseModel):
    """
    Refresh token request schema.

    Used to get new access token using refresh token.
    """

    refresh_token: str = Field(description="Refresh token")


class RoleResponse(BaseModel):
    """
    Role response schema.

    Returns role information.
    """

    id_role: int = Field(description="Role ID")
    role_name: str = Field(description="Role name")
    description: Optional[str] = Field(None, description="Role description")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class UserWithRolesResponse(UserResponse):
    """
    Extended user response with detailed role information.

    Includes full role objects instead of just names.
    """

    roles_detail: List[RoleResponse] = Field(
        default_factory=list,
        description="Detailed role information"
    )
