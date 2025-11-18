"""
Kurikulum Repository

Data access layer for Kurikulum entity.
Following Clean Code: Single Responsibility, Clear intent.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.infrastructure.repositories.base_repository import BaseRepository
from app.infrastructure.models.kurikulum_models import Kurikulum, KurikulumStatus


class KurikulumRepository(BaseRepository[Kurikulum]):
    """
    Repository for Kurikulum operations.

    Extends BaseRepository with Kurikulum-specific queries.
    """

    def __init__(self, session: Session):
        """
        Initialize Kurikulum repository.

        Args:
            session: Database session
        """
        super().__init__(Kurikulum, session)

    def get_by_kode(self, id_prodi: str, kode_kurikulum: str) -> Optional[Kurikulum]:
        """
        Get curriculum by program and code.

        Args:
            id_prodi: Program study ID
            kode_kurikulum: Curriculum code

        Returns:
            Optional[Kurikulum]: Curriculum if found, None otherwise
        """
        return self.get_one_by_criteria(
            id_prodi=id_prodi,
            kode_kurikulum=kode_kurikulum
        )

    def get_active_curricula(self, id_prodi: str) -> List[Kurikulum]:
        """
        Get all active curricula for a program.

        Args:
            id_prodi: Program study ID

        Returns:
            List[Kurikulum]: List of active curricula
        """
        return self.session.query(Kurikulum).filter(
            and_(
                Kurikulum.id_prodi == id_prodi,
                Kurikulum.status == KurikulumStatus.AKTIF
            )
        ).all()

    def get_primary_curriculum(self, id_prodi: str) -> Optional[Kurikulum]:
        """
        Get primary curriculum for a program.

        Args:
            id_prodi: Program study ID

        Returns:
            Optional[Kurikulum]: Primary curriculum if exists
        """
        return self.get_one_by_criteria(
            id_prodi=id_prodi,
            is_primary=True,
            status=KurikulumStatus.AKTIF
        )

    def get_by_status(self, status: KurikulumStatus) -> List[Kurikulum]:
        """
        Get curricula by status.

        Args:
            status: Curriculum status

        Returns:
            List[Kurikulum]: List of curricula with given status
        """
        return self.get_by_criteria(status=status)

    def check_duplicate_code(self, id_prodi: str, kode_kurikulum: str) -> bool:
        """
        Check if curriculum code already exists for program.

        Args:
            id_prodi: Program study ID
            kode_kurikulum: Curriculum code to check

        Returns:
            bool: True if code exists, False otherwise
        """
        return self.exists(id_prodi=id_prodi, kode_kurikulum=kode_kurikulum)

    def get_curricula_by_year_range(
        self,
        id_prodi: str,
        year_from: int,
        year_to: int
    ) -> List[Kurikulum]:
        """
        Get curricula within a year range.

        Args:
            id_prodi: Program study ID
            year_from: Start year
            year_to: End year

        Returns:
            List[Kurikulum]: Curricula within the year range
        """
        return self.session.query(Kurikulum).filter(
            and_(
                Kurikulum.id_prodi == id_prodi,
                Kurikulum.tahun_berlaku >= year_from,
                Kurikulum.tahun_berlaku <= year_to
            )
        ).order_by(Kurikulum.tahun_berlaku.desc()).all()

    def get_with_statistics(self, id_kurikulum: int) -> dict:
        """
        Get curriculum with statistics (CPL count, MK count, student count).

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            dict: Curriculum data with statistics
        """
        from app.infrastructure.models.kurikulum_models import CPL, MataKuliah
        from app.infrastructure.models.master_models import Mahasiswa

        kurikulum = self.get_by_id_or_fail(id_kurikulum)

        # Count related entities
        cpl_count = self.session.query(CPL).filter(
            CPL.id_kurikulum == id_kurikulum,
            CPL.is_active == True
        ).count()

        mk_count = self.session.query(MataKuliah).filter(
            MataKuliah.id_kurikulum == id_kurikulum,
            MataKuliah.is_active == True
        ).count()

        student_count = self.session.query(Mahasiswa).filter(
            Mahasiswa.id_kurikulum == id_kurikulum
        ).count()

        return {
            "kurikulum": kurikulum,
            "statistics": {
                "total_cpl": cpl_count,
                "total_matakuliah": mk_count,
                "total_mahasiswa": student_count
            }
        }
