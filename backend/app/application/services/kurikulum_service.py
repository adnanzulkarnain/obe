"""
Kurikulum Service

Business logic for curriculum management operations.
Following Clean Code: Business rule enforcement, Clear responsibilities.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.infrastructure.repositories.kurikulum_repository import KurikulumRepository
from app.infrastructure.models.kurikulum_models import Kurikulum, KurikulumStatus
from app.presentation.schemas.kurikulum_schemas import (
    KurikulumCreate,
    KurikulumUpdate
)
from app.domain.exceptions import (
    EntityNotFoundException,
    DuplicateEntityException,
    InvalidOperationException
)


class KurikulumService:
    """
    Handles curriculum management operations.

    Responsibilities:
    - Curriculum CRUD operations
    - Curriculum lifecycle management (draft → review → approved → active)
    - Primary curriculum management
    - Business rule enforcement
    """

    def __init__(self, session: Session):
        """
        Initialize kurikulum service.

        Args:
            session: Database session for data access
        """
        self.session = session
        self.kurikulum_repo = KurikulumRepository(session)

    def create_kurikulum(self, kurikulum_data: KurikulumCreate) -> Kurikulum:
        """
        Create a new curriculum.

        Args:
            kurikulum_data: Curriculum creation data

        Returns:
            Kurikulum: Newly created curriculum

        Raises:
            DuplicateEntityException: If curriculum code already exists
        """
        # Check for duplicate code within program
        if self.kurikulum_repo.check_duplicate_code(
            kurikulum_data.id_prodi,
            kurikulum_data.kode_kurikulum
        ):
            raise DuplicateEntityException(
                "Kurikulum",
                "kode_kurikulum",
                kurikulum_data.kode_kurikulum
            )

        # Create curriculum with status=draft
        kurikulum = self.kurikulum_repo.create(
            id_prodi=kurikulum_data.id_prodi,
            kode_kurikulum=kurikulum_data.kode_kurikulum,
            nama_kurikulum=kurikulum_data.nama_kurikulum,
            tahun_berlaku=kurikulum_data.tahun_berlaku,
            tahun_berakhir=kurikulum_data.tahun_berakhir,
            deskripsi=kurikulum_data.deskripsi,
            nomor_sk=kurikulum_data.nomor_sk,
            tanggal_sk=kurikulum_data.tanggal_sk,
            status=KurikulumStatus.DRAFT,
            is_primary=False
        )

        return kurikulum

    def get_kurikulum_by_id(self, id_kurikulum: int) -> Kurikulum:
        """
        Get curriculum by ID.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            Kurikulum: Curriculum instance

        Raises:
            EntityNotFoundException: If curriculum not found
        """
        return self.kurikulum_repo.get_by_id_or_fail(id_kurikulum)

    def get_kurikulum_with_statistics(self, id_kurikulum: int) -> dict:
        """
        Get curriculum with statistics (CPL, MK, student counts).

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            dict: Curriculum data with statistics
        """
        return self.kurikulum_repo.get_with_statistics(id_kurikulum)

    def get_all_kurikulum(
        self,
        id_prodi: Optional[str] = None,
        status: Optional[KurikulumStatus] = None
    ) -> List[Kurikulum]:
        """
        Get all curricula with optional filtering.

        Args:
            id_prodi: Optional filter by program study
            status: Optional filter by status

        Returns:
            List[Kurikulum]: List of curricula
        """
        if id_prodi and status:
            return self.kurikulum_repo.get_by_criteria(
                id_prodi=id_prodi,
                status=status
            )
        elif id_prodi:
            return self.kurikulum_repo.get_by_criteria(id_prodi=id_prodi)
        elif status:
            return self.kurikulum_repo.get_by_status(status)
        else:
            return self.kurikulum_repo.get_all()

    def get_active_kurikulum(self, id_prodi: str) -> List[Kurikulum]:
        """
        Get all active curricula for a program.

        Business Rule BR-K05: Support multiple parallel active curricula.

        Args:
            id_prodi: Program study ID

        Returns:
            List[Kurikulum]: List of active curricula
        """
        return self.kurikulum_repo.get_active_curricula(id_prodi)

    def get_primary_kurikulum(self, id_prodi: str) -> Optional[Kurikulum]:
        """
        Get primary curriculum for a program.

        Args:
            id_prodi: Program study ID

        Returns:
            Optional[Kurikulum]: Primary curriculum if exists
        """
        return self.kurikulum_repo.get_primary_curriculum(id_prodi)

    def update_kurikulum(
        self,
        id_kurikulum: int,
        kurikulum_data: KurikulumUpdate
    ) -> Kurikulum:
        """
        Update curriculum information.

        Only allows updates if curriculum status is draft or review.

        Args:
            id_kurikulum: Curriculum ID
            kurikulum_data: Updated curriculum data

        Returns:
            Kurikulum: Updated curriculum

        Raises:
            EntityNotFoundException: If curriculum not found
            InvalidOperationException: If curriculum cannot be modified
        """
        kurikulum = self.get_kurikulum_by_id(id_kurikulum)

        # Check if curriculum can be modified
        if not kurikulum.can_be_modified():
            raise InvalidOperationException(
                f"Kurikulum dengan status '{kurikulum.status.value}' "
                "tidak dapat dimodifikasi"
            )

        # Update only provided fields
        update_dict = kurikulum_data.model_dump(exclude_unset=True)
        return self.kurikulum_repo.update(kurikulum, **update_dict)

    def submit_for_review(self, id_kurikulum: int) -> Kurikulum:
        """
        Submit curriculum for review.

        Changes status from draft to review.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            Kurikulum: Updated curriculum

        Raises:
            InvalidOperationException: If curriculum is not in draft status
        """
        kurikulum = self.get_kurikulum_by_id(id_kurikulum)

        if kurikulum.status != KurikulumStatus.DRAFT:
            raise InvalidOperationException(
                "Hanya kurikulum dengan status 'draft' yang dapat disubmit"
            )

        return self.kurikulum_repo.update(
            kurikulum,
            status=KurikulumStatus.REVIEW
        )

    def approve_kurikulum(self, id_kurikulum: int) -> Kurikulum:
        """
        Approve curriculum.

        Changes status from review to approved.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            Kurikulum: Approved curriculum

        Raises:
            InvalidOperationException: If curriculum is not in review status
        """
        kurikulum = self.get_kurikulum_by_id(id_kurikulum)

        if kurikulum.status != KurikulumStatus.REVIEW:
            raise InvalidOperationException(
                "Hanya kurikulum dengan status 'review' yang dapat diapprove"
            )

        return self.kurikulum_repo.update(
            kurikulum,
            status=KurikulumStatus.APPROVED
        )

    def activate_kurikulum(
        self,
        id_kurikulum: int,
        set_as_primary: bool = False
    ) -> Kurikulum:
        """
        Activate a curriculum.

        Business Rule BR-K08: Only 1 primary curriculum per program.

        Args:
            id_kurikulum: Curriculum ID
            set_as_primary: Whether to set as primary curriculum

        Returns:
            Kurikulum: Activated curriculum

        Raises:
            InvalidOperationException: If curriculum is not approved
        """
        kurikulum = self.get_kurikulum_by_id(id_kurikulum)

        # Check if curriculum can be activated
        if not kurikulum.can_be_activated():
            raise InvalidOperationException(
                "Kurikulum harus dalam status 'approved' untuk diaktifkan"
            )

        # If setting as primary, remove primary flag from others
        if set_as_primary:
            self._remove_primary_flag(kurikulum.id_prodi)

        # Activate curriculum
        return self.kurikulum_repo.update(
            kurikulum,
            status=KurikulumStatus.AKTIF,
            is_primary=set_as_primary
        )

    def deactivate_kurikulum(self, id_kurikulum: int) -> Kurikulum:
        """
        Deactivate a curriculum.

        Changes status to non-aktif. Curriculum still exists but doesn't
        accept new students.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            Kurikulum: Deactivated curriculum
        """
        kurikulum = self.get_kurikulum_by_id(id_kurikulum)

        return self.kurikulum_repo.update(
            kurikulum,
            status=KurikulumStatus.NON_AKTIF,
            is_primary=False
        )

    def archive_kurikulum(self, id_kurikulum: int) -> Kurikulum:
        """
        Archive a curriculum.

        Can only archive if no active students are using it.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            Kurikulum: Archived curriculum

        Raises:
            InvalidOperationException: If curriculum still has active students
        """
        from app.infrastructure.models.master_models import Mahasiswa, StatusMahasiswa

        kurikulum = self.get_kurikulum_by_id(id_kurikulum)

        # Check if there are active students
        active_students = self.session.query(Mahasiswa).filter(
            Mahasiswa.id_kurikulum == id_kurikulum,
            Mahasiswa.status == StatusMahasiswa.AKTIF
        ).count()

        if active_students > 0:
            raise InvalidOperationException(
                f"Kurikulum masih digunakan oleh {active_students} mahasiswa aktif. "
                "Tidak dapat diarsipkan."
            )

        return self.kurikulum_repo.update(
            kurikulum,
            status=KurikulumStatus.ARSIP,
            is_primary=False
        )

    # Private helper methods

    def _remove_primary_flag(self, id_prodi: str) -> None:
        """
        Remove primary flag from all curricula in a program.

        Args:
            id_prodi: Program study ID
        """
        from sqlalchemy import update

        self.session.execute(
            update(Kurikulum)
            .where(Kurikulum.id_prodi == id_prodi)
            .values(is_primary=False)
        )
        self.session.commit()
