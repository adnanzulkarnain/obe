"""
Kurikulum Use Cases

Application layer business logic for curriculum management.
Following Clean Architecture: Use cases orchestrate the flow of data.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date

from app.domain.entities import (
    KurikulumEntity,
    KurikulumStatus,
    KurikulumStatistics,
    CPLEntity,
    MataKuliahEntity,
)
from app.domain.exceptions import (
    NotFoundException,
    DuplicateException,
    InvalidOperationException,
)
from app.infrastructure.repositories.kurikulum_repository import KurikulumRepository
from app.infrastructure.repositories.cpl_repository import CPLRepository
from app.infrastructure.repositories.matakuliah_repository import MataKuliahRepository
from app.infrastructure.models.kurikulum_models import (
    Kurikulum,
    KurikulumStatus as KurikulumStatusModel,
)


class KurikulumUseCases:
    """
    Use cases for Kurikulum management.

    Orchestrates business logic for curriculum operations.
    """

    def __init__(
        self,
        session: Session,
        kurikulum_repo: Optional[KurikulumRepository] = None,
        cpl_repo: Optional[CPLRepository] = None,
        mk_repo: Optional[MataKuliahRepository] = None,
    ):
        """
        Initialize use cases with repositories.

        Args:
            session: Database session
            kurikulum_repo: Kurikulum repository (optional, created if not provided)
            cpl_repo: CPL repository (optional)
            mk_repo: MataKuliah repository (optional)
        """
        self.session = session
        self.kurikulum_repo = kurikulum_repo or KurikulumRepository(session)
        self.cpl_repo = cpl_repo or CPLRepository(session)
        self.mk_repo = mk_repo or MataKuliahRepository(session)

    def create_kurikulum(
        self,
        id_prodi: str,
        kode_kurikulum: str,
        nama_kurikulum: str,
        tahun_berlaku: int,
        tahun_berakhir: Optional[int] = None,
        deskripsi: Optional[str] = None,
        is_primary: bool = False,
    ) -> Kurikulum:
        """
        Create new curriculum.

        Args:
            id_prodi: Program study ID
            kode_kurikulum: Curriculum code
            nama_kurikulum: Curriculum name
            tahun_berlaku: Year curriculum becomes effective
            tahun_berakhir: Optional year curriculum ends
            deskripsi: Optional description
            is_primary: Whether this is primary curriculum

        Returns:
            Kurikulum: Created curriculum

        Raises:
            DuplicateException: If curriculum code already exists for program
            InvalidOperationException: If business rules violated
        """
        # Check duplicate code
        if self.kurikulum_repo.check_duplicate_code(id_prodi, kode_kurikulum):
            raise DuplicateException(
                f"Kurikulum dengan kode '{kode_kurikulum}' sudah ada untuk prodi '{id_prodi}'"
            )

        # Validate using domain entity (will raise ValueError if invalid)
        try:
            entity = KurikulumEntity(
                id_kurikulum=None,
                id_prodi=id_prodi,
                kode_kurikulum=kode_kurikulum,
                nama_kurikulum=nama_kurikulum,
                tahun_berlaku=tahun_berlaku,
                tahun_berakhir=tahun_berakhir,
                deskripsi=deskripsi,
                status=KurikulumStatus.DRAFT,
                is_primary=is_primary,
            )
        except ValueError as e:
            raise InvalidOperationException(str(e))

        # If is_primary, unset other primary curricula
        if is_primary:
            self._unset_primary_curricula(id_prodi)

        # Create database model
        kurikulum = Kurikulum(
            id_prodi=id_prodi,
            kode_kurikulum=kode_kurikulum,
            nama_kurikulum=nama_kurikulum,
            tahun_berlaku=tahun_berlaku,
            tahun_berakhir=tahun_berakhir,
            deskripsi=deskripsi,
            status=KurikulumStatusModel.DRAFT,
            is_primary=is_primary,
        )

        created = self.kurikulum_repo.create(kurikulum)
        self.session.commit()
        self.session.refresh(created)

        return created

    def get_kurikulum_by_id(
        self,
        id_kurikulum: int,
        include_statistics: bool = False
    ) -> Kurikulum:
        """
        Get curriculum by ID.

        Args:
            id_kurikulum: Curriculum ID
            include_statistics: Whether to include statistics

        Returns:
            Kurikulum: Curriculum object

        Raises:
            NotFoundException: If curriculum not found
        """
        if include_statistics:
            result = self.kurikulum_repo.get_with_statistics(id_kurikulum)
            return result["kurikulum"]
        else:
            return self.kurikulum_repo.get_by_id_or_fail(id_kurikulum)

    def get_kurikulum_with_statistics(self, id_kurikulum: int) -> Dict[str, Any]:
        """
        Get curriculum with detailed statistics.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            Dict containing curriculum and statistics

        Raises:
            NotFoundException: If curriculum not found
        """
        return self.kurikulum_repo.get_with_statistics(id_kurikulum)

    def list_kurikulum(
        self,
        id_prodi: Optional[str] = None,
        status: Optional[KurikulumStatus] = None,
    ) -> List[Kurikulum]:
        """
        List curricula with optional filters.

        Args:
            id_prodi: Optional program study ID filter
            status: Optional status filter

        Returns:
            List[Kurikulum]: List of curricula
        """
        filters = {}
        if id_prodi:
            filters["id_prodi"] = id_prodi
        if status:
            # Convert domain enum to model enum
            filters["status"] = KurikulumStatusModel(status.value)

        return self.kurikulum_repo.get_by_criteria(**filters)

    def update_kurikulum(
        self,
        id_kurikulum: int,
        nama_kurikulum: Optional[str] = None,
        tahun_berakhir: Optional[int] = None,
        deskripsi: Optional[str] = None,
        nomor_sk: Optional[str] = None,
        tanggal_sk: Optional[date] = None,
    ) -> Kurikulum:
        """
        Update curriculum.

        Args:
            id_kurikulum: Curriculum ID
            nama_kurikulum: Optional new name
            tahun_berakhir: Optional end year
            deskripsi: Optional description
            nomor_sk: Optional SK number
            tanggal_sk: Optional SK date

        Returns:
            Kurikulum: Updated curriculum

        Raises:
            NotFoundException: If curriculum not found
            InvalidOperationException: If curriculum cannot be modified
        """
        kurikulum = self.kurikulum_repo.get_by_id_or_fail(id_kurikulum)

        # Check if can be modified (only DRAFT and REVIEW status)
        if kurikulum.status not in [KurikulumStatusModel.DRAFT, KurikulumStatusModel.REVIEW]:
            raise InvalidOperationException(
                f"Kurikulum dengan status '{kurikulum.status}' tidak dapat dimodifikasi"
            )

        # Update fields
        update_data = {}
        if nama_kurikulum is not None:
            update_data["nama_kurikulum"] = nama_kurikulum
        if tahun_berakhir is not None:
            update_data["tahun_berakhir"] = tahun_berakhir
        if deskripsi is not None:
            update_data["deskripsi"] = deskripsi
        if nomor_sk is not None:
            update_data["nomor_sk"] = nomor_sk
        if tanggal_sk is not None:
            update_data["tanggal_sk"] = tanggal_sk

        updated = self.kurikulum_repo.update(kurikulum, **update_data)
        self.session.commit()
        self.session.refresh(updated)

        return updated

    def activate_kurikulum(
        self,
        id_kurikulum: int,
        nomor_sk: str,
        tanggal_sk: date,
        set_as_primary: bool = False,
    ) -> Kurikulum:
        """
        Activate curriculum.

        Args:
            id_kurikulum: Curriculum ID
            nomor_sk: SK number for activation
            tanggal_sk: SK date
            set_as_primary: Whether to set as primary curriculum

        Returns:
            Kurikulum: Activated curriculum

        Raises:
            NotFoundException: If curriculum not found
            InvalidOperationException: If curriculum cannot be activated
        """
        kurikulum = self.kurikulum_repo.get_by_id_or_fail(id_kurikulum)

        # Check if can be activated (only APPROVED status)
        if kurikulum.status != KurikulumStatusModel.APPROVED:
            raise InvalidOperationException(
                f"Kurikulum dengan status '{kurikulum.status}' tidak dapat diaktifkan. "
                "Status harus APPROVED."
            )

        # If set_as_primary, unset other primary curricula
        if set_as_primary:
            self._unset_primary_curricula(kurikulum.id_prodi)

        # Update to active
        updated = self.kurikulum_repo.update(
            kurikulum,
            status=KurikulumStatusModel.AKTIF,
            nomor_sk=nomor_sk,
            tanggal_sk=tanggal_sk,
            is_primary=set_as_primary,
        )

        self.session.commit()
        self.session.refresh(updated)

        return updated

    def deactivate_kurikulum(self, id_kurikulum: int) -> Kurikulum:
        """
        Deactivate curriculum.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            Kurikulum: Deactivated curriculum

        Raises:
            NotFoundException: If curriculum not found
        """
        kurikulum = self.kurikulum_repo.get_by_id_or_fail(id_kurikulum)

        if kurikulum.status == KurikulumStatusModel.AKTIF:
            updated = self.kurikulum_repo.update(
                kurikulum,
                status=KurikulumStatusModel.NON_AKTIF
            )
            self.session.commit()
            self.session.refresh(updated)
            return updated

        return kurikulum

    def approve_kurikulum(self, id_kurikulum: int) -> Kurikulum:
        """
        Approve curriculum (from REVIEW to APPROVED).

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            Kurikulum: Approved curriculum

        Raises:
            NotFoundException: If curriculum not found
            InvalidOperationException: If curriculum not in REVIEW status
        """
        kurikulum = self.kurikulum_repo.get_by_id_or_fail(id_kurikulum)

        if kurikulum.status != KurikulumStatusModel.REVIEW:
            raise InvalidOperationException(
                f"Kurikulum dengan status '{kurikulum.status}' tidak dapat disetujui. "
                "Status harus REVIEW."
            )

        updated = self.kurikulum_repo.update(
            kurikulum,
            status=KurikulumStatusModel.APPROVED
        )
        self.session.commit()
        self.session.refresh(updated)

        return updated

    def submit_for_review(self, id_kurikulum: int) -> Kurikulum:
        """
        Submit curriculum for review (from DRAFT to REVIEW).

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            Kurikulum: Submitted curriculum

        Raises:
            NotFoundException: If curriculum not found
            InvalidOperationException: If curriculum not in DRAFT status
        """
        kurikulum = self.kurikulum_repo.get_by_id_or_fail(id_kurikulum)

        if kurikulum.status != KurikulumStatusModel.DRAFT:
            raise InvalidOperationException(
                f"Kurikulum dengan status '{kurikulum.status}' tidak dapat diajukan review. "
                "Status harus DRAFT."
            )

        updated = self.kurikulum_repo.update(
            kurikulum,
            status=KurikulumStatusModel.REVIEW
        )
        self.session.commit()
        self.session.refresh(updated)

        return updated

    def delete_kurikulum(self, id_kurikulum: int) -> None:
        """
        Delete curriculum (only if in DRAFT status).

        Args:
            id_kurikulum: Curriculum ID

        Raises:
            NotFoundException: If curriculum not found
            InvalidOperationException: If curriculum cannot be deleted
        """
        kurikulum = self.kurikulum_repo.get_by_id_or_fail(id_kurikulum)

        # Only allow deletion of DRAFT curricula
        if kurikulum.status != KurikulumStatusModel.DRAFT:
            raise InvalidOperationException(
                f"Kurikulum dengan status '{kurikulum.status}' tidak dapat dihapus. "
                "Hanya kurikulum DRAFT yang dapat dihapus."
            )

        self.kurikulum_repo.delete(kurikulum)
        self.session.commit()

    def get_active_curricula(self, id_prodi: str) -> List[Kurikulum]:
        """
        Get all active curricula for a program.

        Args:
            id_prodi: Program study ID

        Returns:
            List[Kurikulum]: List of active curricula
        """
        return self.kurikulum_repo.get_active_curricula(id_prodi)

    def get_primary_curriculum(self, id_prodi: str) -> Optional[Kurikulum]:
        """
        Get primary curriculum for a program.

        Args:
            id_prodi: Program study ID

        Returns:
            Optional[Kurikulum]: Primary curriculum if exists
        """
        return self.kurikulum_repo.get_primary_curriculum(id_prodi)

    def _unset_primary_curricula(self, id_prodi: str) -> None:
        """
        Unset all primary curricula for a program (internal helper).

        Args:
            id_prodi: Program study ID
        """
        active_curricula = self.kurikulum_repo.get_by_criteria(
            id_prodi=id_prodi,
            is_primary=True
        )

        for kurikulum in active_curricula:
            self.kurikulum_repo.update(kurikulum, is_primary=False)
