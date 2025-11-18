from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, CheckConstraint, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class MataKuliah(Base):
    __tablename__ = "matakuliah"

    kode_mk = Column(String(20), primary_key=True)
    id_kurikulum = Column(Integer, ForeignKey("kurikulum.id_kurikulum"), primary_key=True)
    nama_mk = Column(String(100), nullable=False)
    nama_mk_eng = Column(String(100))
    sks = Column(Integer, CheckConstraint("sks > 0"))
    semester = Column(Integer, CheckConstraint("semester BETWEEN 1 AND 14"))
    rumpun = Column(String(50))
    jenis_mk = Column(String(50), CheckConstraint("jenis_mk IN ('wajib','pilihan','MKWU')"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    kurikulum = relationship("Kurikulum", back_populates="matakuliah")
    rps = relationship("RPS", back_populates="matakuliah")
    prasyarat_untuk = relationship("PrasyaratMK", foreign_keys="PrasyaratMK.kode_mk_prasyarat", back_populates="mk_prasyarat")
    memerlukan_prasyarat = relationship("PrasyaratMK", foreign_keys="PrasyaratMK.kode_mk", back_populates="mk")


class PrasyaratMK(Base):
    __tablename__ = "prasyarat_mk"

    id_prasyarat = Column(Integer, primary_key=True, index=True)
    kode_mk = Column(String(20))
    id_kurikulum = Column(Integer)
    kode_mk_prasyarat = Column(String(20))
    id_kurikulum_prasyarat = Column(Integer)
    jenis = Column(String(20), CheckConstraint("jenis IN ('wajib','alternatif')"), default='wajib')

    # Relationships
    mk = relationship("MataKuliah", foreign_keys=[kode_mk, id_kurikulum], primaryjoin="and_(PrasyaratMK.kode_mk==MataKuliah.kode_mk, PrasyaratMK.id_kurikulum==MataKuliah.id_kurikulum)")
    mk_prasyarat = relationship("MataKuliah", foreign_keys=[kode_mk_prasyarat, id_kurikulum_prasyarat], primaryjoin="and_(PrasyaratMK.kode_mk_prasyarat==MataKuliah.kode_mk, PrasyaratMK.id_kurikulum_prasyarat==MataKuliah.id_kurikulum)")


class PemetaanMKKurikulum(Base):
    __tablename__ = "pemetaan_mk_kurikulum"

    id_pemetaan = Column(Integer, primary_key=True, index=True)
    kode_mk_lama = Column(String(20))
    id_kurikulum_lama = Column(Integer, ForeignKey("kurikulum.id_kurikulum"))
    kode_mk_baru = Column(String(20))
    id_kurikulum_baru = Column(Integer, ForeignKey("kurikulum.id_kurikulum"))
    jenis_pemetaan = Column(String(20), CheckConstraint("jenis_pemetaan IN ('ekuivalen','sebagian','diganti','dihapus')"))
    bobot_konversi = Column(Numeric(5, 2), default=100.00)
    catatan = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
