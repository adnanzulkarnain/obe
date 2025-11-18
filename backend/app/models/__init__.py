from .user import User, Role, UserRole
from .fakultas import Fakultas, Prodi
from .kurikulum import Kurikulum
from .cpl import CPL
from .matakuliah import MataKuliah, PrasyaratMK, PemetaanMKKurikulum
from .rps import RPS, RPSVersion, RPSApproval
from .cpmk import CPMK, SubCPMK, RelasiCPMKCPL
from .kelas import Kelas, TugasMengajar, Enrollment
from .penilaian import (
    JenisPenilaian,
    TemplatePenilaian,
    KomponenPenilaian,
    NilaiDetail,
    KetercapaianCPMK
)
from .mahasiswa import Mahasiswa
from .dosen import Dosen

__all__ = [
    "User",
    "Role",
    "UserRole",
    "Fakultas",
    "Prodi",
    "Kurikulum",
    "CPL",
    "MataKuliah",
    "PrasyaratMK",
    "PemetaanMKKurikulum",
    "RPS",
    "RPSVersion",
    "RPSApproval",
    "CPMK",
    "SubCPMK",
    "RelasiCPMKCPL",
    "Kelas",
    "TugasMengajar",
    "Enrollment",
    "JenisPenilaian",
    "TemplatePenilaian",
    "KomponenPenilaian",
    "NilaiDetail",
    "KetercapaianCPMK",
    "Mahasiswa",
    "Dosen",
]
