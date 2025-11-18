from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class JenisPenilaian(Base):
    __tablename__ = "jenis_penilaian"

    id_jenis = Column(Integer, primary_key=True, index=True)
    nama_jenis = Column(String(50), unique=True, nullable=False)
    deskripsi = Column(Text)

    # Relationships
    template_penilaian = relationship("TemplatePenilaian", back_populates="jenis")


class TemplatePenilaian(Base):
    __tablename__ = "template_penilaian"

    id_template = Column(Integer, primary_key=True, index=True)
    id_rps = Column(Integer, ForeignKey("rps.id_rps", ondelete="CASCADE"), nullable=False)
    id_cpmk = Column(Integer, ForeignKey("cpmk.id_cpmk"))
    id_jenis = Column(Integer, ForeignKey("jenis_penilaian.id_jenis"))
    bobot = Column(Numeric(5, 2), CheckConstraint("bobot >= 0 AND bobot <= 100"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    jenis = relationship("JenisPenilaian", back_populates="template_penilaian")


class KomponenPenilaian(Base):
    __tablename__ = "komponen_penilaian"

    id_komponen = Column(Integer, primary_key=True, index=True)
    id_kelas = Column(Integer, ForeignKey("kelas.id_kelas", ondelete="CASCADE"), nullable=False)
    id_template = Column(Integer, ForeignKey("template_penilaian.id_template"))
    nama_komponen = Column(String(100), nullable=False)
    deskripsi = Column(Text)
    tanggal_pelaksanaan = Column(Date)
    bobot_realisasi = Column(Numeric(5, 2))
    nilai_maksimal = Column(Numeric(5, 2), default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    nilai_detail = relationship("NilaiDetail", back_populates="komponen", cascade="all, delete-orphan")


class NilaiDetail(Base):
    __tablename__ = "nilai_detail"

    id_nilai_detail = Column(Integer, primary_key=True, index=True)
    id_enrollment = Column(Integer, ForeignKey("enrollment.id_enrollment", ondelete="CASCADE"), nullable=False)
    id_komponen = Column(Integer, ForeignKey("komponen_penilaian.id_komponen"))
    nilai_mentah = Column(Numeric(5, 2), CheckConstraint("nilai_mentah >= 0"))
    nilai_tertimbang = Column(Numeric(5, 2))
    catatan = Column(Text)
    dinilai_oleh = Column(String(20), ForeignKey("dosen.id_dosen"))
    tanggal_input = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    enrollment = relationship("Enrollment", back_populates="nilai_detail")
    komponen = relationship("KomponenPenilaian", back_populates="nilai_detail")


class KetercapaianCPMK(Base):
    __tablename__ = "ketercapaian_cpmk"

    id_ketercapaian = Column(Integer, primary_key=True, index=True)
    id_enrollment = Column(Integer, ForeignKey("enrollment.id_enrollment"), nullable=False)
    id_cpmk = Column(Integer, ForeignKey("cpmk.id_cpmk"))
    nilai_cpmk = Column(Numeric(5, 2))
    status_tercapai = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    enrollment = relationship("Enrollment", back_populates="ketercapaian_cpmk")
