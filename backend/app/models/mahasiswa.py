from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Mahasiswa(Base):
    __tablename__ = "mahasiswa"

    nim = Column(String(20), primary_key=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    id_prodi = Column(String(20), ForeignKey("prodi.id_prodi"))
    id_kurikulum = Column(Integer, ForeignKey("kurikulum.id_kurikulum"), nullable=False)
    angkatan = Column(String(10), nullable=False)
    status = Column(String(20), CheckConstraint("status IN ('aktif','cuti','lulus','DO')"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    kurikulum = relationship("Kurikulum", back_populates="mahasiswa")
    enrollment = relationship("Enrollment", back_populates="mahasiswa")
