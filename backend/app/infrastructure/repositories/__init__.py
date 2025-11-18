"""
Repository Layer

Implements the Repository pattern for data access.
Following Clean Code: Separation of Concerns, Dependency Inversion.
"""

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.repositories.kurikulum_repository import KurikulumRepository
from app.infrastructure.repositories.cpl_repository import CPLRepository
from app.infrastructure.repositories.matakuliah_repository import MataKuliahRepository
from app.infrastructure.repositories.user_repository import UserRepository

__all__ = [
    "BaseRepository",
    "KurikulumRepository",
    "CPLRepository",
    "MataKuliahRepository",
    "UserRepository",
]
