"""
MataKuliah Repository

Data access layer for MataKuliah (Course) entity.
Following Clean Code: Single Responsibility, Type safety.
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.models.kurikulum_models import MataKuliah, JenisMK


class MataKuliahRepository(BaseRepository[MataKuliah]):
    """
    Repository for MataKuliah operations.

    Note: MataKuliah has composite primary key (kode_mk, id_kurikulum).
    """

    def __init__(self, session: Session):
        """
        Initialize MataKuliah repository.

        Args:
            session: Database session
        """
        super().__init__(MataKuliah, session)

    def get_by_composite_key(
        self,
        kode_mk: str,
        id_kurikulum: int
    ) -> Optional[MataKuliah]:
        """
        Get MataKuliah by composite primary key.

        Args:
            kode_mk: Course code
            id_kurikulum: Curriculum ID

        Returns:
            Optional[MataKuliah]: MataKuliah if found, None otherwise
        """
        return self.session.query(MataKuliah).filter(
            and_(
                MataKuliah.kode_mk == kode_mk,
                MataKuliah.id_kurikulum == id_kurikulum
            )
        ).first()

    def get_by_kurikulum(
        self,
        id_kurikulum: int,
        active_only: bool = True
    ) -> List[MataKuliah]:
        """
        Get all courses in a curriculum.

        Args:
            id_kurikulum: Curriculum ID
            active_only: If True, return only active courses

        Returns:
            List[MataKuliah]: List of courses
        """
        criteria = {"id_kurikulum": id_kurikulum}
        if active_only:
            criteria["is_active"] = True

        return self.session.query(MataKuliah).filter_by(**criteria).order_by(
            MataKuliah.semester,
            MataKuliah.kode_mk
        ).all()

    def get_by_semester(
        self,
        id_kurikulum: int,
        semester: int
    ) -> List[MataKuliah]:
        """
        Get courses by semester in a curriculum.

        Args:
            id_kurikulum: Curriculum ID
            semester: Semester number (1-14)

        Returns:
            List[MataKuliah]: List of courses in the semester
        """
        return self.get_by_criteria(
            id_kurikulum=id_kurikulum,
            semester=semester,
            is_active=True
        )

    def get_by_jenis(
        self,
        id_kurikulum: int,
        jenis_mk: JenisMK
    ) -> List[MataKuliah]:
        """
        Get courses by type (wajib/pilihan/MKWU).

        Args:
            id_kurikulum: Curriculum ID
            jenis_mk: Course type

        Returns:
            List[MataKuliah]: List of courses of that type
        """
        return self.get_by_criteria(
            id_kurikulum=id_kurikulum,
            jenis_mk=jenis_mk,
            is_active=True
        )

    def check_duplicate_code(
        self,
        kode_mk: str,
        id_kurikulum: int
    ) -> bool:
        """
        Check if course code already exists in curriculum.

        Business Rule BR-K02: Same code can exist in different curricula.

        Args:
            kode_mk: Course code
            id_kurikulum: Curriculum ID

        Returns:
            bool: True if code exists in this curriculum, False otherwise
        """
        return self.get_by_composite_key(kode_mk, id_kurikulum) is not None

    def calculate_total_sks(self, id_kurikulum: int) -> int:
        """
        Calculate total SKS in a curriculum.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            int: Total SKS
        """
        from sqlalchemy import func

        result = self.session.query(
            func.sum(MataKuliah.sks)
        ).filter(
            and_(
                MataKuliah.id_kurikulum == id_kurikulum,
                MataKuliah.is_active == True
            )
        ).scalar()

        return result or 0

    def get_statistics_by_semester(self, id_kurikulum: int) -> dict:
        """
        Get course statistics grouped by semester.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            dict: Statistics by semester
        """
        from sqlalchemy import func

        results = self.session.query(
            MataKuliah.semester,
            func.count(MataKuliah.kode_mk).label('count'),
            func.sum(MataKuliah.sks).label('total_sks')
        ).filter(
            and_(
                MataKuliah.id_kurikulum == id_kurikulum,
                MataKuliah.is_active == True
            )
        ).group_by(MataKuliah.semester).order_by(MataKuliah.semester).all()

        return {
            semester: {"count": count, "total_sks": total_sks}
            for semester, count, total_sks in results
        }

    def soft_delete_by_composite_key(
        self,
        kode_mk: str,
        id_kurikulum: int
    ) -> MataKuliah:
        """
        Soft delete course by composite key.

        Business Rule BR-K03: MK cannot be hard deleted.

        Args:
            kode_mk: Course code
            id_kurikulum: Curriculum ID

        Returns:
            MataKuliah: Soft-deleted course
        """
        mk = self.get_by_composite_key(kode_mk, id_kurikulum)
        if not mk:
            from app.domain.exceptions import EntityNotFoundException
            raise EntityNotFoundException(
                "MataKuliah",
                f"{kode_mk} (kurikulum: {id_kurikulum})"
            )

        return self.soft_delete(mk)
