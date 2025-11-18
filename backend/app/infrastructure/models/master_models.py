"""
Master Data Models

SQLAlchemy models for organizational structure and personnel.
Following Clean Code: Single Responsibility, Clear relationships.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    event
)
from sqlalchemy.orm import relationship
import enum

from app.infrastructure.database import Base
from app.domain.exceptions import CurriculumImmutableException


class Jenjang(str, enum.Enum):
    """Academic level enumeration."""

    D3 = "D3"
    D4 = "D4"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"


class StatusDosen(str, enum.Enum):
    """Lecturer status enumeration."""

    AKTIF = "aktif"
    CUTI = "cuti"
    PENSIUN = "pensiun"


class StatusMahasiswa(str, enum.Enum):
    """Student status enumeration."""

    AKTIF = "aktif"
    CUTI = "cuti"
    LULUS = "lulus"
    DO = "DO"


class Fakultas(Base):
    """
    Faculty model.

    Represents a faculty within the institution.
    """

    __tablename__ = "fakultas"

    id_fakultas = Column(String(20), primary_key=True)
    nama = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    prodi_list = relationship(
        "Prodi",
        back_populates="fakultas",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Fakultas(id='{self.id_fakultas}', nama='{self.nama}')>"


class Prodi(Base):
    """
    Study Program (Program Studi) model.

    Represents an academic program within a faculty.
    """

    __tablename__ = "prodi"

    id_prodi = Column(String(20), primary_key=True)
    id_fakultas = Column(
        String(20),
        ForeignKey("fakultas.id_fakultas", ondelete="CASCADE"),
        nullable=False
    )
    nama = Column(String(100), nullable=False)
    jenjang = Column(SQLEnum(Jenjang), nullable=False)
    akreditasi = Column(String(5), nullable=True)
    tahun_berdiri = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    fakultas = relationship("Fakultas", back_populates="prodi_list")
    dosen_list = relationship("Dosen", back_populates="prodi")
    mahasiswa_list = relationship("Mahasiswa", back_populates="prodi")
    kurikulum_list = relationship("Kurikulum", back_populates="prodi")

    def __repr__(self) -> str:
        return f"<Prodi(id='{self.id_prodi}', nama='{self.nama}')>"


class Dosen(Base):
    """
    Lecturer (Dosen) model.

    Represents faculty members who teach courses.
    """

    __tablename__ = "dosen"

    id_dosen = Column(String(20), primary_key=True)
    nidn = Column(String(20), unique=True, nullable=True, index=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    id_prodi = Column(
        String(20),
        ForeignKey("prodi.id_prodi", ondelete="SET NULL"),
        nullable=True
    )
    status = Column(SQLEnum(StatusDosen), default=StatusDosen.AKTIF, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    prodi = relationship("Prodi", back_populates="dosen_list")

    def __repr__(self) -> str:
        return f"<Dosen(id='{self.id_dosen}', nama='{self.nama}')>"

    def is_active(self) -> bool:
        """Check if lecturer is currently active."""
        return self.status == StatusDosen.AKTIF


class Mahasiswa(Base):
    """
    Student (Mahasiswa) model.

    Represents students enrolled in study programs.

    Business Rule BR-K01: Student curriculum is IMMUTABLE.
    Once assigned, id_kurikulum cannot be changed.
    """

    __tablename__ = "mahasiswa"

    nim = Column(String(20), primary_key=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    id_prodi = Column(
        String(20),
        ForeignKey("prodi.id_prodi", ondelete="CASCADE"),
        nullable=False
    )
    id_kurikulum = Column(
        Integer,
        ForeignKey("kurikulum.id_kurikulum", ondelete="RESTRICT"),
        nullable=True  # Will be set on first enrollment
    )
    angkatan = Column(String(10), nullable=False, index=True)
    status = Column(
        SQLEnum(StatusMahasiswa),
        default=StatusMahasiswa.AKTIF,
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    prodi = relationship("Prodi", back_populates="mahasiswa_list")
    kurikulum = relationship("Kurikulum", back_populates="mahasiswa_list")

    def __repr__(self) -> str:
        return f"<Mahasiswa(nim='{self.nim}', nama='{self.nama}')>"

    def is_active(self) -> bool:
        """Check if student is currently active."""
        return self.status == StatusMahasiswa.AKTIF


# Business Rule BR-K01: Prevent curriculum change after initial assignment
@event.listens_for(Mahasiswa, 'before_update')
def prevent_curriculum_change(mapper, connection, target):
    """
    Enforce immutability of student curriculum (BR-K01).

    Raises:
        CurriculumImmutableException: If curriculum is being changed
    """
    state = target._sa_instance_state
    history = state.get_history('id_kurikulum', True)

    # If id_kurikulum is being changed (not initial assignment)
    if history.has_changes() and history.deleted:
        # Check if there was a previous value
        old_value = history.deleted[0] if history.deleted else None
        new_value = history.added[0] if history.added else None

        # If both have values and they're different, prevent the change
        if old_value is not None and new_value != old_value:
            raise CurriculumImmutableException()
