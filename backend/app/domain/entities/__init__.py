"""
Domain Entities

Pure business objects without framework dependencies.
"""

from app.domain.entities.kurikulum_entities import (
    KurikulumEntity,
    CPLEntity,
    MataKuliahEntity,
    KurikulumStatistics,
    KurikulumStatus,
    CPLKategori,
    JenisMK,
)

__all__ = [
    "KurikulumEntity",
    "CPLEntity",
    "MataKuliahEntity",
    "KurikulumStatistics",
    "KurikulumStatus",
    "CPLKategori",
    "JenisMK",
]
