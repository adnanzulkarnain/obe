"""
Pydantic Schemas

Request and response models for API endpoints.
"""

from app.presentation.schemas.kurikulum_schemas import (
    # Kurikulum schemas
    KurikulumCreateRequest,
    KurikulumUpdateRequest,
    KurikulumActivateRequest,
    KurikulumResponse,
    KurikulumListResponse,
    KurikulumStatisticsResponse,
    # CPL schemas
    CPLCreateRequest,
    CPLUpdateRequest,
    CPLResponse,
    CPLListResponse,
    # Mata Kuliah schemas
    MataKuliahCreateRequest,
    MataKuliahUpdateRequest,
    MataKuliahResponse,
    MataKuliahListResponse,
    # Common schemas
    MessageResponse,
    ErrorResponse,
    # Enums
    KurikulumStatusEnum,
    CPLKategoriEnum,
    JenisMKEnum,
)

__all__ = [
    # Kurikulum
    "KurikulumCreateRequest",
    "KurikulumUpdateRequest",
    "KurikulumActivateRequest",
    "KurikulumResponse",
    "KurikulumListResponse",
    "KurikulumStatisticsResponse",
    # CPL
    "CPLCreateRequest",
    "CPLUpdateRequest",
    "CPLResponse",
    "CPLListResponse",
    # Mata Kuliah
    "MataKuliahCreateRequest",
    "MataKuliahUpdateRequest",
    "MataKuliahResponse",
    "MataKuliahListResponse",
    # Common
    "MessageResponse",
    "ErrorResponse",
    # Enums
    "KurikulumStatusEnum",
    "CPLKategoriEnum",
    "JenisMKEnum",
]
