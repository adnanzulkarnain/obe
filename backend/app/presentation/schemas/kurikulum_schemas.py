"""
Kurikulum Pydantic Schemas

Request and response schemas for curriculum management endpoints.
Following Clean Code: Validation, Business rules enforcement.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import date

from app.presentation.schemas.base_schemas import TimestampMixin
from app.infrastructure.models.kurikulum_models import (
    KurikulumStatus,
    CPLKategori,
    JenisMK
)


# =============================================================================
# KURIKULUM SCHEMAS
# =============================================================================

class KurikulumBase(BaseModel):
    """Base kurikulum schema with common fields."""

    kode_kurikulum: str = Field(
        min_length=2,
        max_length=20,
        description="Unique curriculum code (e.g., K2024)"
    )
    nama_kurikulum: str = Field(
        min_length=3,
        max_length=200,
        description="Curriculum name"
    )
    tahun_berlaku: int = Field(
        ge=2000,
        le=2100,
        description="Year curriculum takes effect"
    )
    tahun_berakhir: Optional[int] = Field(
        None,
        ge=2000,
        le=2100,
        description="Year curriculum ends"
    )
    deskripsi: Optional[str] = Field(None, description="Curriculum description")

    @validator('tahun_berakhir')
    def validate_year_range(cls, v: Optional[int], values: dict) -> Optional[int]:
        """Ensure tahun_berakhir is after tahun_berlaku."""
        if v is not None and 'tahun_berlaku' in values:
            if v <= values['tahun_berlaku']:
                raise ValueError('tahun_berakhir must be after tahun_berlaku')
        return v


class KurikulumCreate(KurikulumBase):
    """Schema for creating a new curriculum."""

    id_prodi: str = Field(max_length=20, description="Program study ID")
    nomor_sk: Optional[str] = Field(
        None,
        max_length=100,
        description="SK (Decree) number"
    )
    tanggal_sk: Optional[date] = Field(None, description="SK date")


class KurikulumUpdate(BaseModel):
    """
    Schema for updating curriculum.

    All fields are optional - only provided fields will be updated.
    """

    nama_kurikulum: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200,
        description="Curriculum name"
    )
    deskripsi: Optional[str] = Field(None, description="Curriculum description")
    tahun_berakhir: Optional[int] = Field(None, description="Year curriculum ends")
    nomor_sk: Optional[str] = Field(None, description="SK number")
    tanggal_sk: Optional[date] = Field(None, description="SK date")


class KurikulumResponse(KurikulumBase, TimestampMixin):
    """Curriculum response schema."""

    id_kurikulum: int = Field(description="Curriculum ID")
    id_prodi: str = Field(description="Program study ID")
    status: KurikulumStatus = Field(description="Curriculum status")
    is_primary: bool = Field(description="Whether this is the primary curriculum")
    nomor_sk: Optional[str] = Field(None, description="SK number")
    tanggal_sk: Optional[date] = Field(None, description="SK date")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class KurikulumWithStats(KurikulumResponse):
    """
    Curriculum response with statistics.

    Includes counts of CPL, MK, and students.
    """

    total_cpl: int = Field(default=0, description="Total number of CPL")
    total_matakuliah: int = Field(default=0, description="Total number of courses")
    total_mahasiswa: int = Field(default=0, description="Total number of students")


class KurikulumActivateRequest(BaseModel):
    """Request to activate a curriculum."""

    set_as_primary: bool = Field(
        default=False,
        description="Set this curriculum as primary"
    )


# =============================================================================
# CPL SCHEMAS
# =============================================================================

class CPLBase(BaseModel):
    """Base CPL schema with common fields."""

    kode_cpl: str = Field(
        min_length=2,
        max_length=20,
        description="CPL code (e.g., CPL-1)"
    )
    deskripsi: str = Field(
        min_length=10,
        description="CPL description"
    )
    kategori: CPLKategori = Field(description="CPL category")
    urutan: Optional[int] = Field(None, ge=1, description="Display order")


class CPLCreate(CPLBase):
    """Schema for creating a new CPL."""

    id_kurikulum: int = Field(description="Curriculum ID this CPL belongs to")


class CPLUpdate(BaseModel):
    """
    Schema for updating CPL.

    All fields are optional.
    """

    deskripsi: Optional[str] = Field(None, min_length=10, description="CPL description")
    kategori: Optional[CPLKategori] = Field(None, description="CPL category")
    urutan: Optional[int] = Field(None, ge=1, description="Display order")
    is_active: Optional[bool] = Field(None, description="Active status")


class CPLResponse(CPLBase, TimestampMixin):
    """CPL response schema."""

    id_cpl: int = Field(description="CPL ID")
    id_kurikulum: int = Field(description="Curriculum ID")
    is_active: bool = Field(description="Whether CPL is active")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class CPLListByCategory(BaseModel):
    """
    CPL list grouped by category.

    Useful for displaying CPL organized by kategori.
    """

    kategori: CPLKategori = Field(description="CPL category")
    cpl_list: List[CPLResponse] = Field(description="List of CPL in this category")
    count: int = Field(description="Number of CPL in this category")


# =============================================================================
# MATA KULIAH SCHEMAS
# =============================================================================

class MataKuliahBase(BaseModel):
    """Base course schema with common fields."""

    nama_mk: str = Field(
        min_length=3,
        max_length=100,
        description="Course name in Indonesian"
    )
    nama_mk_eng: Optional[str] = Field(
        None,
        max_length=100,
        description="Course name in English"
    )
    sks: int = Field(ge=1, le=6, description="Credit hours (SKS)")
    semester: int = Field(ge=1, le=14, description="Semester number")
    rumpun: Optional[str] = Field(None, max_length=50, description="Course cluster")
    jenis_mk: JenisMK = Field(description="Course type")


class MataKuliahCreate(MataKuliahBase):
    """Schema for creating a new course."""

    kode_mk: str = Field(
        min_length=2,
        max_length=20,
        description="Course code (e.g., IF101)"
    )
    id_kurikulum: int = Field(description="Curriculum ID")

    @validator('kode_mk')
    def validate_course_code(cls, v: str) -> str:
        """Validate course code format (uppercase alphanumeric)."""
        if not v.replace('-', '').isalnum():
            raise ValueError('Course code must be alphanumeric')
        return v.upper()


class MataKuliahUpdate(BaseModel):
    """
    Schema for updating course.

    All fields are optional. Note: kode_mk and id_kurikulum cannot be changed.
    """

    nama_mk: Optional[str] = Field(None, min_length=3, description="Course name")
    nama_mk_eng: Optional[str] = Field(None, description="English name")
    sks: Optional[int] = Field(None, ge=1, le=6, description="Credit hours")
    semester: Optional[int] = Field(None, ge=1, le=14, description="Semester")
    rumpun: Optional[str] = Field(None, description="Course cluster")
    jenis_mk: Optional[JenisMK] = Field(None, description="Course type")
    is_active: Optional[bool] = Field(None, description="Active status")


class MataKuliahResponse(MataKuliahBase, TimestampMixin):
    """Course response schema."""

    kode_mk: str = Field(description="Course code")
    id_kurikulum: int = Field(description="Curriculum ID")
    is_active: bool = Field(description="Whether course is active")

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class MataKuliahWithPrerequisites(MataKuliahResponse):
    """
    Course response with prerequisites.

    Includes list of prerequisite courses.
    """

    prerequisites: List[str] = Field(
        default_factory=list,
        description="List of prerequisite course codes"
    )


class MataKuliahStatistics(BaseModel):
    """
    Course statistics for a curriculum.

    Provides overview of courses by semester and type.
    """

    total_courses: int = Field(description="Total number of courses")
    total_sks: int = Field(description="Total credit hours")
    by_semester: dict = Field(description="Statistics by semester")
    by_jenis: dict = Field(description="Statistics by course type")


# =============================================================================
# CURRICULUM COMPARISON SCHEMAS
# =============================================================================

class CurriculumComparison(BaseModel):
    """
    Schema for comparing two curricula.

    Shows differences in CPL, MK, and total SKS.
    """

    kurikulum_lama: KurikulumResponse = Field(description="Old curriculum")
    kurikulum_baru: KurikulumResponse = Field(description="New curriculum")
    cpl_changes: dict = Field(description="Changes in CPL")
    mk_changes: dict = Field(description="Changes in courses")
    sks_difference: int = Field(description="Difference in total SKS")
