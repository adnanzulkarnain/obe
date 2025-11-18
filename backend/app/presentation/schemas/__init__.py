"""
Pydantic Schemas

Request and response models for API endpoints.
All schemas follow Clean Code principles with validation.
"""

# Base schemas
from app.presentation.schemas.base_schemas import (
    BaseResponse,
    SuccessResponse,
    ErrorResponse,
    PaginationParams,
    PaginatedResponse,
    PaginationMeta,
    TimestampMixin,
    IDResponse,
    StatusResponse,
)

# User schemas
from app.presentation.schemas.user_schemas import (
    UserBase,
    UserCreate,
    UserUpdate,
    PasswordChange,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    RoleResponse,
    UserWithRolesResponse,
)

# Kurikulum schemas
from app.presentation.schemas.kurikulum_schemas import (
    KurikulumBase,
    KurikulumCreate,
    KurikulumUpdate,
    KurikulumResponse,
    KurikulumWithStats,
    KurikulumActivateRequest,
    CPLBase,
    CPLCreate,
    CPLUpdate,
    CPLResponse,
    CPLListByCategory,
    MataKuliahBase,
    MataKuliahCreate,
    MataKuliahUpdate,
    MataKuliahResponse,
    MataKuliahWithPrerequisites,
    MataKuliahStatistics,
    CurriculumComparison,
)

__all__ = [
    # Base
    "BaseResponse",
    "SuccessResponse",
    "ErrorResponse",
    "PaginationParams",
    "PaginatedResponse",
    "PaginationMeta",
    "TimestampMixin",
    "IDResponse",
    "StatusResponse",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "PasswordChange",
    "UserResponse",
    "LoginRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "RoleResponse",
    "UserWithRolesResponse",
    # Kurikulum
    "KurikulumBase",
    "KurikulumCreate",
    "KurikulumUpdate",
    "KurikulumResponse",
    "KurikulumWithStats",
    "KurikulumActivateRequest",
    "CPLBase",
    "CPLCreate",
    "CPLUpdate",
    "CPLResponse",
    "CPLListByCategory",
    "MataKuliahBase",
    "MataKuliahCreate",
    "MataKuliahUpdate",
    "MataKuliahResponse",
    "MataKuliahWithPrerequisites",
    "MataKuliahStatistics",
    "CurriculumComparison",
]
