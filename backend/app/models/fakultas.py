from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Fakultas(Base):
    __tablename__ = "fakultas"

    id_fakultas = Column(String(20), primary_key=True)
    nama = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    prodi = relationship("Prodi", back_populates="fakultas")


class Prodi(Base):
    __tablename__ = "prodi"

    id_prodi = Column(String(20), primary_key=True)
    id_fakultas = Column(String(20), ForeignKey("fakultas.id_fakultas"))
    nama = Column(String(100), nullable=False)
    jenjang = Column(String(10), CheckConstraint("jenjang IN ('D3','D4','S1','S2','S3')"))
    akreditasi = Column(String(5))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    fakultas = relationship("Fakultas", back_populates="prodi")
    kurikulum = relationship("Kurikulum", back_populates="prodi")
