from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, Time, Numeric, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Kelas(Base):
    __tablename__ = "kelas"

    id_kelas = Column(Integer, primary_key=True, index=True)
    kode_mk = Column(String(20))
    id_kurikulum = Column(Integer)
    id_rps = Column(Integer, ForeignKey("rps.id_rps"))
    nama_kelas = Column(String(10), nullable=False)
    semester = Column(String(10), nullable=False)
    tahun_ajaran = Column(String(10), nullable=False)
    kapasitas = Column(Integer, default=40)
    kuota_terisi = Column(Integer, default=0)
    hari = Column(String(20))
    jam_mulai = Column(Time)
    jam_selesai = Column(Time)
    ruangan = Column(String(50))
    status = Column(String(20), CheckConstraint("status IN ('draft','open','closed','completed')"), default='draft')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tugas_mengajar = relationship("TugasMengajar", back_populates="kelas", cascade="all, delete-orphan")
    enrollment = relationship("Enrollment", back_populates="kelas", cascade="all, delete-orphan")


class TugasMengajar(Base):
    __tablename__ = "tugas_mengajar"

    id_tugas = Column(Integer, primary_key=True, index=True)
    id_kelas = Column(Integer, ForeignKey("kelas.id_kelas", ondelete="CASCADE"), nullable=False)
    id_dosen = Column(String(20), ForeignKey("dosen.id_dosen"), nullable=False)
    peran = Column(String(50), CheckConstraint("peran IN ('koordinator','pengampu','asisten')"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    kelas = relationship("Kelas", back_populates="tugas_mengajar")
    dosen = relationship("Dosen", back_populates="tugas_mengajar")


class Enrollment(Base):
    __tablename__ = "enrollment"

    id_enrollment = Column(Integer, primary_key=True, index=True)
    nim = Column(String(20), ForeignKey("mahasiswa.nim"), nullable=False)
    id_kelas = Column(Integer, ForeignKey("kelas.id_kelas", ondelete="CASCADE"), nullable=False)
    tanggal_daftar = Column(Date, server_default=func.current_date())
    status = Column(String(20), CheckConstraint("status IN ('aktif','mengulang','drop','lulus')"), default='aktif')
    nilai_akhir = Column(Numeric(5, 2))
    nilai_huruf = Column(String(2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    mahasiswa = relationship("Mahasiswa", back_populates="enrollment")
    kelas = relationship("Kelas", back_populates="enrollment")
    nilai_detail = relationship("NilaiDetail", back_populates="enrollment", cascade="all, delete-orphan")
    ketercapaian_cpmk = relationship("KetercapaianCPMK", back_populates="enrollment", cascade="all, delete-orphan")
