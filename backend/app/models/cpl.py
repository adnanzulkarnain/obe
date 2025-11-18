from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, CheckConstraint, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CPL(Base):
    __tablename__ = "cpl"

    id_cpl = Column(Integer, primary_key=True, index=True)
    id_kurikulum = Column(Integer, ForeignKey("kurikulum.id_kurikulum", ondelete="CASCADE"), nullable=False)
    kode_cpl = Column(String(20), nullable=False)
    deskripsi = Column(Text, nullable=False)
    kategori = Column(
        String(50),
        CheckConstraint("kategori IN ('sikap','pengetahuan','keterampilan_umum','keterampilan_khusus')")
    )
    urutan = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    kurikulum = relationship("Kurikulum", back_populates="cpl")
    relasi_cpmk = relationship("RelasiCPMKCPL", back_populates="cpl")
