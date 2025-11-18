from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CPMK(Base):
    __tablename__ = "cpmk"

    id_cpmk = Column(Integer, primary_key=True, index=True)
    id_rps = Column(Integer, ForeignKey("rps.id_rps", ondelete="CASCADE"), nullable=False)
    kode_cpmk = Column(String(20), nullable=False)
    deskripsi = Column(Text, nullable=False)
    urutan = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    rps = relationship("RPS", back_populates="cpmk")
    subcpmk = relationship("SubCPMK", back_populates="cpmk", cascade="all, delete-orphan")
    relasi_cpl = relationship("RelasiCPMKCPL", back_populates="cpmk", cascade="all, delete-orphan")


class SubCPMK(Base):
    __tablename__ = "subcpmk"

    id_subcpmk = Column(Integer, primary_key=True, index=True)
    id_cpmk = Column(Integer, ForeignKey("cpmk.id_cpmk", ondelete="CASCADE"), nullable=False)
    kode_subcpmk = Column(String(20), nullable=False)
    deskripsi = Column(Text, nullable=False)
    indikator = Column(Text)
    urutan = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    cpmk = relationship("CPMK", back_populates="subcpmk")


class RelasiCPMKCPL(Base):
    __tablename__ = "relasi_cpmk_cpl"

    id_relasi = Column(Integer, primary_key=True, index=True)
    id_cpmk = Column(Integer, ForeignKey("cpmk.id_cpmk", ondelete="CASCADE"), nullable=False)
    id_cpl = Column(Integer, ForeignKey("cpl.id_cpl", ondelete="CASCADE"), nullable=False)
    bobot_kontribusi = Column(Numeric(5, 2), default=100.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    cpmk = relationship("CPMK", back_populates="relasi_cpl")
    cpl = relationship("CPL", back_populates="relasi_cpmk")
