from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, CheckConstraint, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Kurikulum(Base):
    __tablename__ = "kurikulum"

    id_kurikulum = Column(Integer, primary_key=True, index=True)
    id_prodi = Column(String(20), ForeignKey("prodi.id_prodi"), nullable=False)
    kode_kurikulum = Column(String(20), nullable=False)
    nama_kurikulum = Column(String(200), nullable=False)
    tahun_berlaku = Column(Integer, nullable=False)
    tahun_berakhir = Column(Integer)
    status = Column(
        String(20),
        CheckConstraint("status IN ('draft','review','approved','aktif','non-aktif','arsip')"),
        default='draft',
        nullable=False
    )
    is_primary = Column(Boolean, default=False)
    deskripsi = Column(Text)
    nomor_sk = Column(String(100))
    tanggal_sk = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    prodi = relationship("Prodi", back_populates="kurikulum")
    cpl = relationship("CPL", back_populates="kurikulum", cascade="all, delete-orphan")
    matakuliah = relationship("MataKuliah", back_populates="kurikulum", cascade="all, delete-orphan")
    mahasiswa = relationship("Mahasiswa", back_populates="kurikulum")
