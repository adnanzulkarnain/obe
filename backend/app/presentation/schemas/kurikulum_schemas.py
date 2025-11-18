"""
Kurikulum API Schemas

Pydantic models for request/response validation and serialization.
Following Clean Code: Clear naming, type safety, comprehensive validation.
"""

from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


# Enums matching domain entities
class KurikulumStatusEnum(str, Enum):
    """Curriculum status enumeration."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    AKTIF = "aktif"
    NON_AKTIF = "non-aktif"
    ARSIP = "arsip"


class CPLKategoriEnum(str, Enum):
    """CPL category enumeration."""

    SIKAP = "sikap"
    PENGETAHUAN = "pengetahuan"
    KETERAMPILAN_UMUM = "keterampilan_umum"
    KETERAMPILAN_KHUSUS = "keterampilan_khusus"


class JenisMKEnum(str, Enum):
    """Course type enumeration."""

    WAJIB = "wajib"
    PILIHAN = "pilihan"
    MKWU = "MKWU"


# ===== Kurikulum Schemas =====

class KurikulumCreateRequest(BaseModel):
    """Schema for creating a new curriculum."""

    id_prodi: str = Field(..., description="Program studi ID", min_length=1, max_length=20)
    kode_kurikulum: str = Field(..., description="Curriculum code", min_length=1, max_length=20)
    nama_kurikulum: str = Field(..., description="Curriculum name", min_length=1, max_length=200)
    tahun_berlaku: int = Field(..., description="Year curriculum becomes effective", ge=1900)
    tahun_berakhir: Optional[int] = Field(None, description="Year curriculum ends", ge=1900)
    deskripsi: Optional[str] = Field(None, description="Curriculum description")
    is_primary: bool = Field(False, description="Is this the primary curriculum?")

    @validator("tahun_berakhir")
    def validate_year_range(cls, v, values):
        """Ensure end year is after start year."""
        if v and "tahun_berlaku" in values:
            if v < values["tahun_berlaku"]:
                raise ValueError("Tahun berakhir harus lebih besar dari tahun berlaku")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id_prodi": "TIF",
                "kode_kurikulum": "K2024",
                "nama_kurikulum": "Kurikulum OBE 2024",
                "tahun_berlaku": 2024,
                "deskripsi": "Kurikulum berbasis OBE untuk tahun 2024",
                "is_primary": True
            }
        }
    )


class KurikulumUpdateRequest(BaseModel):
    """Schema for updating curriculum."""

    nama_kurikulum: Optional[str] = Field(None, min_length=1, max_length=200)
    tahun_berakhir: Optional[int] = Field(None, ge=1900)
    deskripsi: Optional[str] = None
    nomor_sk: Optional[str] = Field(None, max_length=100)
    tanggal_sk: Optional[date] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nama_kurikulum": "Kurikulum OBE 2024 (Revisi)",
                "deskripsi": "Kurikulum revisi berdasarkan feedback akreditasi",
                "nomor_sk": "SK/123/2024",
                "tanggal_sk": "2024-01-15"
            }
        }
    )


class KurikulumActivateRequest(BaseModel):
    """Schema for activating curriculum."""

    nomor_sk: str = Field(..., description="SK number for activation", min_length=1, max_length=100)
    tanggal_sk: date = Field(..., description="SK date")
    set_as_primary: bool = Field(False, description="Set as primary curriculum")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nomor_sk": "SK/456/2024",
                "tanggal_sk": "2024-06-01",
                "set_as_primary": True
            }
        }
    )


class KurikulumStatisticsResponse(BaseModel):
    """Schema for curriculum statistics."""

    total_cpl: int = Field(..., description="Total CPL count")
    total_matakuliah: int = Field(..., description="Total course count")
    total_mahasiswa: int = Field(..., description="Total student count")

    model_config = ConfigDict(from_attributes=True)


class KurikulumResponse(BaseModel):
    """Schema for curriculum response."""

    id_kurikulum: int
    id_prodi: str
    kode_kurikulum: str
    nama_kurikulum: str
    tahun_berlaku: int
    tahun_berakhir: Optional[int]
    deskripsi: Optional[str]
    status: KurikulumStatusEnum
    is_primary: bool
    nomor_sk: Optional[str]
    tanggal_sk: Optional[date]
    created_at: datetime
    updated_at: datetime
    statistics: Optional[KurikulumStatisticsResponse] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id_kurikulum": 1,
                "id_prodi": "TIF",
                "kode_kurikulum": "K2024",
                "nama_kurikulum": "Kurikulum OBE 2024",
                "tahun_berlaku": 2024,
                "tahun_berakhir": None,
                "deskripsi": "Kurikulum berbasis OBE",
                "status": "aktif",
                "is_primary": True,
                "nomor_sk": "SK/456/2024",
                "tanggal_sk": "2024-06-01",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-06-01T00:00:00"
            }
        }
    )


class KurikulumListResponse(BaseModel):
    """Schema for list of curricula."""

    total: int = Field(..., description="Total number of records")
    data: List[KurikulumResponse] = Field(..., description="List of curricula")


# ===== CPL Schemas =====

class CPLCreateRequest(BaseModel):
    """Schema for creating CPL."""

    kode_cpl: str = Field(..., description="CPL code", min_length=1, max_length=20)
    deskripsi: str = Field(..., description="CPL description", min_length=1)
    kategori: CPLKategoriEnum = Field(..., description="CPL category")
    urutan: Optional[int] = Field(None, description="Display order", ge=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "kode_cpl": "CPL01",
                "deskripsi": "Mampu menerapkan pemikiran logis, kritis, inovatif",
                "kategori": "keterampilan_khusus",
                "urutan": 1
            }
        }
    )


class CPLUpdateRequest(BaseModel):
    """Schema for updating CPL."""

    deskripsi: Optional[str] = Field(None, min_length=1)
    kategori: Optional[CPLKategoriEnum] = None
    urutan: Optional[int] = Field(None, ge=1)


class CPLResponse(BaseModel):
    """Schema for CPL response."""

    id_cpl: int
    id_kurikulum: int
    kode_cpl: str
    deskripsi: str
    kategori: CPLKategoriEnum
    urutan: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CPLListResponse(BaseModel):
    """Schema for list of CPL."""

    total: int
    data: List[CPLResponse]


# ===== Mata Kuliah Schemas =====

class MataKuliahCreateRequest(BaseModel):
    """Schema for creating course."""

    kode_mk: str = Field(..., description="Course code", min_length=1, max_length=20)
    nama_mk: str = Field(..., description="Course name", min_length=1, max_length=100)
    nama_mk_eng: Optional[str] = Field(None, max_length=100)
    sks: int = Field(..., description="Credit hours", ge=1)
    semester: int = Field(..., description="Semester", ge=1, le=14)
    rumpun: Optional[str] = Field(None, max_length=50)
    jenis_mk: JenisMKEnum = Field(..., description="Course type")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "kode_mk": "TIF101",
                "nama_mk": "Dasar Pemrograman",
                "nama_mk_eng": "Programming Fundamentals",
                "sks": 3,
                "semester": 1,
                "rumpun": "Pemrograman",
                "jenis_mk": "wajib"
            }
        }
    )


class MataKuliahUpdateRequest(BaseModel):
    """Schema for updating course."""

    nama_mk: Optional[str] = Field(None, min_length=1, max_length=100)
    nama_mk_eng: Optional[str] = Field(None, max_length=100)
    sks: Optional[int] = Field(None, ge=1)
    semester: Optional[int] = Field(None, ge=1, le=14)
    rumpun: Optional[str] = Field(None, max_length=50)
    jenis_mk: Optional[JenisMKEnum] = None


class MataKuliahResponse(BaseModel):
    """Schema for course response."""

    kode_mk: str
    id_kurikulum: int
    nama_mk: str
    nama_mk_eng: Optional[str]
    sks: int
    semester: int
    rumpun: Optional[str]
    jenis_mk: JenisMKEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MataKuliahListResponse(BaseModel):
    """Schema for list of courses."""

    total: int
    data: List[MataKuliahResponse]


# ===== Common Schemas =====

class MessageResponse(BaseModel):
    """Schema for simple message response."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Optional data payload")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Kurikulum berhasil diaktifkan",
                "data": {"id_kurikulum": 1}
            }
        }
    )


class ErrorResponse(BaseModel):
    """Schema for error response."""

    success: bool = Field(False, description="Always false for errors")
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "error_code": "KURIKULUM_NOT_FOUND",
                "message": "Kurikulum dengan ID tersebut tidak ditemukan",
                "details": {"id_kurikulum": 999}
            }
        }
    )
