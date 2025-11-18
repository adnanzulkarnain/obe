"""
Domain Entities for Kurikulum Management

Pure Python business objects independent of infrastructure.
Following Clean Architecture: Entities contain enterprise business rules.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class KurikulumStatus(str, Enum):
    """Curriculum status lifecycle."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    AKTIF = "aktif"
    NON_AKTIF = "non-aktif"
    ARSIP = "arsip"


class CPLKategori(str, Enum):
    """CPL category types based on SNPT."""

    SIKAP = "sikap"
    PENGETAHUAN = "pengetahuan"
    KETERAMPILAN_UMUM = "keterampilan_umum"
    KETERAMPILAN_KHUSUS = "keterampilan_khusus"


class JenisMK(str, Enum):
    """Course type enumeration."""

    WAJIB = "wajib"
    PILIHAN = "pilihan"
    MKWU = "MKWU"


@dataclass
class KurikulumEntity:
    """
    Kurikulum (Curriculum) domain entity.

    Represents a curriculum version for a study program.
    Contains business logic for curriculum lifecycle management.

    Business Rules:
    - BR-K05: Support 2+ curricula running in parallel
    - BR-K08: Only 1 curriculum can be primary per prodi
    """

    id_kurikulum: Optional[int]
    id_prodi: str
    kode_kurikulum: str
    nama_kurikulum: str
    tahun_berlaku: int
    status: KurikulumStatus
    is_primary: bool = False
    tahun_berakhir: Optional[int] = None
    deskripsi: Optional[str] = None
    nomor_sk: Optional[str] = None
    tanggal_sk: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate entity after initialization."""
        self._validate()

    def _validate(self) -> None:
        """
        Validate business rules.

        Raises:
            ValueError: If any business rule is violated
        """
        if self.tahun_berlaku < 1900:
            raise ValueError("Tahun berlaku harus lebih besar dari 1900")

        if self.tahun_berakhir and self.tahun_berakhir < self.tahun_berlaku:
            raise ValueError("Tahun berakhir harus lebih besar dari tahun berlaku")

        if not self.kode_kurikulum.strip():
            raise ValueError("Kode kurikulum tidak boleh kosong")

        if not self.nama_kurikulum.strip():
            raise ValueError("Nama kurikulum tidak boleh kosong")

    def is_active(self) -> bool:
        """Check if curriculum is currently active."""
        return self.status == KurikulumStatus.AKTIF

    def can_be_activated(self) -> bool:
        """
        Check if curriculum can be activated.

        Returns:
            bool: True if curriculum is in APPROVED status
        """
        return self.status == KurikulumStatus.APPROVED

    def can_be_modified(self) -> bool:
        """
        Check if curriculum can be modified.

        Returns:
            bool: True if curriculum is in DRAFT or REVIEW status
        """
        return self.status in [KurikulumStatus.DRAFT, KurikulumStatus.REVIEW]

    def can_be_deleted(self) -> bool:
        """
        Check if curriculum can be deleted.

        Returns:
            bool: True if curriculum is in DRAFT status (not yet used)
        """
        return self.status == KurikulumStatus.DRAFT

    def activate(self) -> None:
        """
        Activate curriculum.

        Raises:
            ValueError: If curriculum cannot be activated
        """
        if not self.can_be_activated():
            raise ValueError(
                f"Kurikulum dengan status {self.status} tidak dapat diaktifkan. "
                "Status harus APPROVED."
            )
        self.status = KurikulumStatus.AKTIF

    def deactivate(self) -> None:
        """Deactivate curriculum."""
        if self.status == KurikulumStatus.AKTIF:
            self.status = KurikulumStatus.NON_AKTIF

    def archive(self) -> None:
        """Archive curriculum (soft delete)."""
        self.status = KurikulumStatus.ARSIP

    def approve(self) -> None:
        """
        Approve curriculum for activation.

        Raises:
            ValueError: If curriculum is not in REVIEW status
        """
        if self.status != KurikulumStatus.REVIEW:
            raise ValueError(
                f"Kurikulum dengan status {self.status} tidak dapat disetujui. "
                "Status harus REVIEW."
            )
        self.status = KurikulumStatus.APPROVED

    def submit_for_review(self) -> None:
        """
        Submit curriculum for review.

        Raises:
            ValueError: If curriculum is not in DRAFT status
        """
        if self.status != KurikulumStatus.DRAFT:
            raise ValueError(
                f"Kurikulum dengan status {self.status} tidak dapat diajukan review. "
                "Status harus DRAFT."
            )
        self.status = KurikulumStatus.REVIEW


@dataclass
class CPLEntity:
    """
    CPL (Capaian Pembelajaran Lulusan) domain entity.

    Program Learning Outcome entity tied to a curriculum.

    Business Rule BR-K07: CPL belongs to curriculum, not directly to prodi.
    """

    id_cpl: Optional[int]
    id_kurikulum: int
    kode_cpl: str
    deskripsi: str
    kategori: CPLKategori
    urutan: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate entity after initialization."""
        self._validate()

    def _validate(self) -> None:
        """
        Validate business rules.

        Raises:
            ValueError: If any business rule is violated
        """
        if not self.kode_cpl.strip():
            raise ValueError("Kode CPL tidak boleh kosong")

        if not self.deskripsi.strip():
            raise ValueError("Deskripsi CPL tidak boleh kosong")

        if self.urutan is not None and self.urutan < 1:
            raise ValueError("Urutan CPL harus lebih besar dari 0")

    def deactivate(self) -> None:
        """Deactivate CPL (soft delete)."""
        self.is_active = False

    def reactivate(self) -> None:
        """Reactivate CPL."""
        self.is_active = True


@dataclass
class MataKuliahEntity:
    """
    Mata Kuliah (Course) domain entity.

    Business Rule BR-K02: Same kode_mk can exist in different curricula.
    Business Rule BR-K03: Cannot be hard deleted (soft delete only).
    """

    kode_mk: str
    id_kurikulum: int
    nama_mk: str
    sks: int
    semester: int
    jenis_mk: JenisMK
    nama_mk_eng: Optional[str] = None
    rumpun: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate entity after initialization."""
        self._validate()

    def _validate(self) -> None:
        """
        Validate business rules.

        Raises:
            ValueError: If any business rule is violated
        """
        if not self.kode_mk.strip():
            raise ValueError("Kode MK tidak boleh kosong")

        if not self.nama_mk.strip():
            raise ValueError("Nama MK tidak boleh kosong")

        if self.sks <= 0:
            raise ValueError("SKS harus lebih besar dari 0")

        if not (1 <= self.semester <= 14):
            raise ValueError("Semester harus antara 1 dan 14")

    def deactivate(self) -> None:
        """
        Deactivate course (soft delete).

        Business Rule BR-K03: MK cannot be hard deleted.
        """
        self.is_active = False

    def reactivate(self) -> None:
        """Reactivate course."""
        self.is_active = True

    def update_sks(self, new_sks: int) -> None:
        """
        Update course credits.

        Args:
            new_sks: New SKS value

        Raises:
            ValueError: If new_sks is invalid
        """
        if new_sks <= 0:
            raise ValueError("SKS harus lebih besar dari 0")
        self.sks = new_sks


@dataclass
class KurikulumStatistics:
    """
    Curriculum statistics value object.

    Provides aggregated information about curriculum.
    """

    total_cpl: int = 0
    total_matakuliah: int = 0
    total_mahasiswa: int = 0
    total_sks: int = 0

    def is_ready_for_activation(self) -> bool:
        """
        Check if curriculum has minimum requirements for activation.

        Returns:
            bool: True if curriculum has CPL and courses defined
        """
        return self.total_cpl > 0 and self.total_matakuliah > 0
