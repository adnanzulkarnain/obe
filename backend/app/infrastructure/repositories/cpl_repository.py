"""
CPL Repository

Data access layer for CPL (Capaian Pembelajaran Lulusan) entity.
Following Clean Code: Single Responsibility, Clear naming.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.models.kurikulum_models import CPL, CPLKategori


class CPLRepository(BaseRepository[CPL]):
    """
    Repository for CPL operations.

    Extends BaseRepository with CPL-specific queries.
    """

    def __init__(self, session: Session):
        """
        Initialize CPL repository.

        Args:
            session: Database session
        """
        super().__init__(CPL, session)

    def get_by_kurikulum(
        self,
        id_kurikulum: int,
        active_only: bool = True
    ) -> List[CPL]:
        """
        Get all CPL for a curriculum.

        Args:
            id_kurikulum: Curriculum ID
            active_only: If True, return only active CPL

        Returns:
            List[CPL]: List of CPL
        """
        criteria = {"id_kurikulum": id_kurikulum}
        if active_only:
            criteria["is_active"] = True

        return self.session.query(CPL).filter_by(**criteria).order_by(
            CPL.urutan,
            CPL.kode_cpl
        ).all()

    def get_by_kode(
        self,
        id_kurikulum: int,
        kode_cpl: str
    ) -> Optional[CPL]:
        """
        Get CPL by curriculum and code.

        Args:
            id_kurikulum: Curriculum ID
            kode_cpl: CPL code

        Returns:
            Optional[CPL]: CPL if found, None otherwise
        """
        return self.get_one_by_criteria(
            id_kurikulum=id_kurikulum,
            kode_cpl=kode_cpl
        )

    def get_by_kategori(
        self,
        id_kurikulum: int,
        kategori: CPLKategori
    ) -> List[CPL]:
        """
        Get CPL by category within a curriculum.

        Args:
            id_kurikulum: Curriculum ID
            kategori: CPL category

        Returns:
            List[CPL]: List of CPL in the category
        """
        return self.get_by_criteria(
            id_kurikulum=id_kurikulum,
            kategori=kategori,
            is_active=True
        )

    def check_duplicate_code(
        self,
        id_kurikulum: int,
        kode_cpl: str
    ) -> bool:
        """
        Check if CPL code already exists in curriculum.

        Args:
            id_kurikulum: Curriculum ID
            kode_cpl: CPL code to check

        Returns:
            bool: True if code exists, False otherwise
        """
        return self.exists(id_kurikulum=id_kurikulum, kode_cpl=kode_cpl)

    def get_next_urutan(self, id_kurikulum: int) -> int:
        """
        Get next urutan number for CPL in curriculum.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            int: Next urutan number
        """
        max_urutan = self.session.query(CPL.urutan).filter(
            CPL.id_kurikulum == id_kurikulum
        ).order_by(CPL.urutan.desc()).first()

        return (max_urutan[0] + 1) if max_urutan and max_urutan[0] else 1

    def count_by_kategori(self, id_kurikulum: int) -> dict:
        """
        Count CPL by category in a curriculum.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            dict: Count by category
        """
        from sqlalchemy import func

        results = self.session.query(
            CPL.kategori,
            func.count(CPL.id_cpl).label('count')
        ).filter(
            CPL.id_kurikulum == id_kurikulum,
            CPL.is_active == True
        ).group_by(CPL.kategori).all()

        return {kategori: count for kategori, count in results}
