from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, Text, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class RPS(Base):
    __tablename__ = "rps"

    id_rps = Column(Integer, primary_key=True, index=True)
    kode_mk = Column(String(20))
    id_kurikulum = Column(Integer)
    semester_berlaku = Column(String(10), nullable=False)
    tahun_ajaran = Column(String(10), nullable=False)
    status = Column(
        String(20),
        CheckConstraint("status IN ('draft','submitted','revised','approved','active','archived')"),
        default='draft'
    )
    ketua_pengembang = Column(String(20), ForeignKey("dosen.id_dosen"))
    tanggal_disusun = Column(Date, server_default=func.current_date())
    deskripsi_mk = Column(Text)
    prasyarat = Column(Text)
    created_by = Column(String(20), ForeignKey("dosen.id_dosen"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    matakuliah = relationship("MataKuliah", back_populates="rps", foreign_keys=[kode_mk, id_kurikulum], primaryjoin="and_(RPS.kode_mk==MataKuliah.kode_mk, RPS.id_kurikulum==MataKuliah.id_kurikulum)")
    cpmk = relationship("CPMK", back_populates="rps", cascade="all, delete-orphan")
    versions = relationship("RPSVersion", back_populates="rps", cascade="all, delete-orphan")


class RPSVersion(Base):
    __tablename__ = "rps_version"

    id_version = Column(Integer, primary_key=True, index=True)
    id_rps = Column(Integer, ForeignKey("rps.id_rps", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    status = Column(String(20))
    snapshot_data = Column(JSONB)
    created_by = Column(String(20), ForeignKey("dosen.id_dosen"))
    approved_by = Column(String(20), ForeignKey("dosen.id_dosen"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True))
    keterangan = Column(Text)
    is_active = Column(Boolean, default=False)

    # Relationships
    rps = relationship("RPS", back_populates="versions")


class RPSApproval(Base):
    __tablename__ = "rps_approval"

    id_approval = Column(Integer, primary_key=True, index=True)
    id_rps = Column(Integer, ForeignKey("rps.id_rps"))
    approver = Column(String(20), ForeignKey("dosen.id_dosen"))
    approval_level = Column(Integer)
    status = Column(String(20), CheckConstraint("status IN ('pending','approved','rejected','revised')"))
    komentar = Column(Text)
    approved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
