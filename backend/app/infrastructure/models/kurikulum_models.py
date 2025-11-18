"""
Curriculum Models

SQLAlchemy models for curriculum management.
Following Clean Code: Business rule enforcement, Clear relationships.
"""

from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    ForeignKeyConstraint,
    Text,
    Numeric,
    Enum as SQLEnum,
    UniqueConstraint,
    CheckConstraint,
    event
)
from sqlalchemy.orm import relationship
import enum

from app.infrastructure.database import Base


class KurikulumStatus(str, enum.Enum):
    """Curriculum status lifecycle."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    AKTIF = "aktif"
    NON_AKTIF = "non-aktif"
    ARSIP = "arsip"


class CPLKategori(str, enum.Enum):
    """CPL category types based on SNPT."""

    SIKAP = "sikap"
    PENGETAHUAN = "pengetahuan"
    KETERAMPILAN_UMUM = "keterampilan_umum"
    KETERAMPILAN_KHUSUS = "keterampilan_khusus"


class JenisMK(str, enum.Enum):
    """Course type enumeration."""

    WAJIB = "wajib"
    PILIHAN = "pilihan"
    MKWU = "MKWU"


class TipePrasyarat(str, enum.Enum):
    """Prerequisite type."""

    WAJIB = "wajib"
    ALTERNATIF = "alternatif"


class TipePemetaan(str, enum.Enum):
    """Course mapping type between curricula."""

    EKUIVALEN = "ekuivalen"  # 100% equivalent
    SEBAGIAN = "sebagian"  # Partial equivalence
    DIGANTI = "diganti"  # Replaced by another course
    DIHAPUS = "dihapus"  # Removed, no equivalent


class Kurikulum(Base):
    """
    Curriculum model.

    Represents a curriculum version for a study program.
    Multiple curricula can be active in parallel.

    Business Rules:
    - BR-K05: Support 2+ curricula running in parallel
    - BR-K08: Only 1 curriculum can be primary per prodi
    """

    __tablename__ = "kurikulum"

    id_kurikulum = Column(Integer, primary_key=True, index=True)
    id_prodi = Column(
        String(20),
        ForeignKey("prodi.id_prodi", ondelete="CASCADE"),
        nullable=False
    )
    kode_kurikulum = Column(String(20), nullable=False)
    nama_kurikulum = Column(String(200), nullable=False)
    tahun_berlaku = Column(Integer, nullable=False)
    tahun_berakhir = Column(Integer, nullable=True)
    deskripsi = Column(Text, nullable=True)
    status = Column(
        SQLEnum(KurikulumStatus),
        default=KurikulumStatus.DRAFT,
        nullable=False
    )
    is_primary = Column(Boolean, default=False, nullable=False)
    nomor_sk = Column(String(100), nullable=True)
    tanggal_sk = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint('id_prodi', 'kode_kurikulum', name='uq_prodi_kode_kurikulum'),
        CheckConstraint('tahun_berlaku > 1900', name='chk_tahun_berlaku_valid'),
    )

    # Relationships
    prodi = relationship("Prodi", back_populates="kurikulum_list")
    cpl_list = relationship("CPL", back_populates="kurikulum", cascade="all, delete-orphan")
    matakuliah_list = relationship("MataKuliah", back_populates="kurikulum")
    mahasiswa_list = relationship("Mahasiswa", back_populates="kurikulum")

    def __repr__(self) -> str:
        return (
            f"<Kurikulum(kode='{self.kode_kurikulum}', "
            f"nama='{self.nama_kurikulum}', status='{self.status}')>"
        )

    def is_active(self) -> bool:
        """Check if curriculum is currently active."""
        return self.status == KurikulumStatus.AKTIF

    def can_be_activated(self) -> bool:
        """Check if curriculum can be activated."""
        return self.status == KurikulumStatus.APPROVED

    def can_be_modified(self) -> bool:
        """Check if curriculum can be modified."""
        return self.status in [KurikulumStatus.DRAFT, KurikulumStatus.REVIEW]


class CPL(Base):
    """
    Program Learning Outcome (Capaian Pembelajaran Lulusan) model.

    CPL belongs to a curriculum, not to a study program directly.

    Business Rule BR-K07: CPL is tied to curriculum.
    Same kode_cpl can exist in different curricula with different descriptions.
    """

    __tablename__ = "cpl"

    id_cpl = Column(Integer, primary_key=True, index=True)
    id_kurikulum = Column(
        Integer,
        ForeignKey("kurikulum.id_kurikulum", ondelete="CASCADE"),
        nullable=False
    )
    kode_cpl = Column(String(20), nullable=False)
    deskripsi = Column(Text, nullable=False)
    kategori = Column(SQLEnum(CPLKategori), nullable=False)
    urutan = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint('id_kurikulum', 'kode_cpl', name='uq_kurikulum_kode_cpl'),
    )

    # Relationships
    kurikulum = relationship("Kurikulum", back_populates="cpl_list")

    def __repr__(self) -> str:
        return f"<CPL(kode='{self.kode_cpl}', kategori='{self.kategori}')>"


class MataKuliah(Base):
    """
    Course (Mata Kuliah) model.

    Business Rule BR-K02: Same kode_mk can exist in different curricula.
    Composite primary key: (kode_mk, id_kurikulum)

    Business Rule BR-K03: Cannot be hard deleted (soft delete only).
    """

    __tablename__ = "matakuliah"

    kode_mk = Column(String(20), primary_key=True)
    id_kurikulum = Column(
        Integer,
        ForeignKey("kurikulum.id_kurikulum", ondelete="CASCADE"),
        primary_key=True
    )
    nama_mk = Column(String(100), nullable=False)
    nama_mk_eng = Column(String(100), nullable=True)
    sks = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    rumpun = Column(String(50), nullable=True)
    jenis_mk = Column(SQLEnum(JenisMK), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Constraints
    __table_args__ = (
        CheckConstraint('sks > 0', name='chk_sks_positive'),
        CheckConstraint('semester BETWEEN 1 AND 14', name='chk_semester_valid'),
    )

    # Relationships
    kurikulum = relationship("Kurikulum", back_populates="matakuliah_list")
    prasyarat_list = relationship(
        "PrasyaratMK",
        foreign_keys="[PrasyaratMK.kode_mk, PrasyaratMK.id_kurikulum]",
        back_populates="matakuliah"
    )

    def __repr__(self) -> str:
        return f"<MataKuliah(kode='{self.kode_mk}', nama='{self.nama_mk}')>"


class PrasyaratMK(Base):
    """
    Course prerequisite model.

    Defines prerequisites that must be completed before taking a course.
    Prerequisites must be from the same curriculum.
    """

    __tablename__ = "prasyarat_mk"

    id_prasyarat = Column(Integer, primary_key=True, index=True)
    kode_mk = Column(String(20), nullable=False)
    id_kurikulum = Column(Integer, nullable=False)
    kode_mk_prasyarat = Column(String(20), nullable=False)
    tipe_prasyarat = Column(
        SQLEnum(TipePrasyarat),
        default=TipePrasyarat.WAJIB,
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Foreign key constraint
    __table_args__ = (
        ForeignKeyConstraint(
            ['kode_mk', 'id_kurikulum'],
            ['matakuliah.kode_mk', 'matakuliah.id_kurikulum'],
            ondelete='CASCADE',
            name='fk_prasyarat_mk'
        ),
        UniqueConstraint(
            'kode_mk',
            'id_kurikulum',
            'kode_mk_prasyarat',
            name='uq_mk_prasyarat'
        ),
    )

    # Relationships
    matakuliah = relationship(
        "MataKuliah",
        foreign_keys=[kode_mk, id_kurikulum],
        back_populates="prasyarat_list"
    )

    def __repr__(self) -> str:
        return (
            f"<PrasyaratMK(mk='{self.kode_mk}', "
            f"prasyarat='{self.kode_mk_prasyarat}')>"
        )


class PemetaanMKKurikulum(Base):
    """
    Course mapping between curricula.

    Used for student transfers, curriculum conversion, and RPL.

    Business Rule BR-K06: Support MK mapping for conversion.
    """

    __tablename__ = "pemetaan_mk_kurikulum"

    id_pemetaan = Column(Integer, primary_key=True, index=True)
    id_kurikulum_lama = Column(
        Integer,
        ForeignKey("kurikulum.id_kurikulum", ondelete="CASCADE"),
        nullable=False
    )
    kode_mk_lama = Column(String(20), nullable=False)
    id_kurikulum_baru = Column(
        Integer,
        ForeignKey("kurikulum.id_kurikulum", ondelete="CASCADE"),
        nullable=False
    )
    kode_mk_baru = Column(String(20), nullable=True)  # Null if DIHAPUS
    tipe_pemetaan = Column(SQLEnum(TipePemetaan), nullable=False)
    persentase_ekuivalensi = Column(
        Numeric(5, 2),
        nullable=False,
        default=0.00
    )
    catatan = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            'persentase_ekuivalensi BETWEEN 0 AND 100',
            name='chk_persentase_valid'
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<PemetaanMKKurikulum(lama='{self.kode_mk_lama}', "
            f"baru='{self.kode_mk_baru}', tipe='{self.tipe_pemetaan}')>"
        )


# Business Rule BR-K03: Prevent hard delete of MataKuliah
@event.listens_for(MataKuliah, 'before_delete')
def prevent_matakuliah_hard_delete(mapper, connection, target):
    """
    Enforce soft delete only for MataKuliah (BR-K03).

    Raises:
        InvalidOperationException: Always, to prevent hard delete
    """
    from app.domain.exceptions import InvalidOperationException

    raise InvalidOperationException(
        "Mata Kuliah tidak dapat dihapus secara permanen (hard delete). "
        "Gunakan soft delete dengan mengubah is_active = False. "
        "Ini adalah business rule BR-K03."
    )
