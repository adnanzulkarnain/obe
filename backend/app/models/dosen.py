from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Dosen(Base):
    __tablename__ = "dosen"

    id_dosen = Column(String(20), primary_key=True)
    nidn = Column(String(20), unique=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    id_prodi = Column(String(20), ForeignKey("prodi.id_prodi"))
    status = Column(String(20), CheckConstraint("status IN ('aktif','cuti','pensiun')"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tugas_mengajar = relationship("TugasMengajar", back_populates="dosen")
