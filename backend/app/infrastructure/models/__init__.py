"""
Database Models

SQLAlchemy ORM models representing database tables.
"""

from app.infrastructure.models.user_models import User, Role, UserRole
from app.infrastructure.models.master_models import (
    Fakultas,
    Prodi,
    Dosen,
    Mahasiswa
)
from app.infrastructure.models.kurikulum_models import (
    Kurikulum,
    CPL,
    MataKuliah,
    PrasyaratMK,
    PemetaanMKKurikulum
)

__all__ = [
    # User models
    "User",
    "Role",
    "UserRole",
    # Master data models
    "Fakultas",
    "Prodi",
    "Dosen",
    "Mahasiswa",
    # Kurikulum models
    "Kurikulum",
    "CPL",
    "MataKuliah",
    "PrasyaratMK",
    "PemetaanMKKurikulum",
]
