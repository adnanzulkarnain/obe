"""
CPL Service

Business logic for CPL (Capaian Pembelajaran Lulusan) management.
Following Clean Code: Business logic encapsulation, Type safety.
"""

from typing import List, Dict
from sqlalchemy.orm import Session

from app.infrastructure.repositories.cpl_repository import CPLRepository
from app.infrastructure.models.kurikulum_models import CPL, CPLKategori
from app.presentation.schemas.kurikulum_schemas import CPLCreate, CPLUpdate
from app.domain.exceptions import (
    EntityNotFoundException,
    DuplicateEntityException
)


class CPLService:
    """
    Handles CPL management operations.

    Responsibilities:
    - CPL CRUD operations
    - CPL organization by category
    - CPL validation and business rules
    """

    def __init__(self, session: Session):
        """
        Initialize CPL service.

        Args:
            session: Database session for data access
        """
        self.session = session
        self.cpl_repo = CPLRepository(session)

    def create_cpl(self, cpl_data: CPLCreate) -> CPL:
        """
        Create a new CPL.

        Business Rule BR-K07: CPL belongs to curriculum.

        Args:
            cpl_data: CPL creation data

        Returns:
            CPL: Newly created CPL

        Raises:
            DuplicateEntityException: If CPL code already exists in curriculum
        """
        # Check for duplicate code within curriculum
        if self.cpl_repo.check_duplicate_code(
            cpl_data.id_kurikulum,
            cpl_data.kode_cpl
        ):
            raise DuplicateEntityException(
                "CPL",
                "kode_cpl",
                cpl_data.kode_cpl
            )

        # Auto-assign urutan if not provided
        urutan = cpl_data.urutan
        if urutan is None:
            urutan = self.cpl_repo.get_next_urutan(cpl_data.id_kurikulum)

        # Create CPL
        cpl = self.cpl_repo.create(
            id_kurikulum=cpl_data.id_kurikulum,
            kode_cpl=cpl_data.kode_cpl,
            deskripsi=cpl_data.deskripsi,
            kategori=cpl_data.kategori,
            urutan=urutan,
            is_active=True
        )

        return cpl

    def get_cpl_by_id(self, id_cpl: int) -> CPL:
        """
        Get CPL by ID.

        Args:
            id_cpl: CPL ID

        Returns:
            CPL: CPL instance

        Raises:
            EntityNotFoundException: If CPL not found
        """
        return self.cpl_repo.get_by_id_or_fail(id_cpl)

    def get_cpl_by_kurikulum(
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
            List[CPL]: List of CPL ordered by urutan
        """
        return self.cpl_repo.get_by_kurikulum(id_kurikulum, active_only)

    def get_cpl_by_kategori(
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
        return self.cpl_repo.get_by_kategori(id_kurikulum, kategori)

    def get_cpl_grouped_by_kategori(self, id_kurikulum: int) -> Dict[CPLKategori, List[CPL]]:
        """
        Get all CPL grouped by category.

        Useful for displaying CPL organized by kategori (sikap, pengetahuan, etc).

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            Dict[CPLKategori, List[CPL]]: CPL grouped by category
        """
        all_cpl = self.get_cpl_by_kurikulum(id_kurikulum)

        grouped = {kategori: [] for kategori in CPLKategori}

        for cpl in all_cpl:
            grouped[cpl.kategori].append(cpl)

        return grouped

    def count_cpl_by_kategori(self, id_kurikulum: int) -> Dict[str, int]:
        """
        Count CPL by category.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            Dict[str, int]: Count by category
        """
        return self.cpl_repo.count_by_kategori(id_kurikulum)

    def update_cpl(self, id_cpl: int, cpl_data: CPLUpdate) -> CPL:
        """
        Update CPL information.

        Args:
            id_cpl: CPL ID
            cpl_data: Updated CPL data

        Returns:
            CPL: Updated CPL

        Raises:
            EntityNotFoundException: If CPL not found
        """
        cpl = self.get_cpl_by_id(id_cpl)

        # Update only provided fields
        update_dict = cpl_data.model_dump(exclude_unset=True)
        return self.cpl_repo.update(cpl, **update_dict)

    def deactivate_cpl(self, id_cpl: int) -> CPL:
        """
        Deactivate a CPL (soft delete).

        Args:
            id_cpl: CPL ID

        Returns:
            CPL: Deactivated CPL

        Raises:
            EntityNotFoundException: If CPL not found
        """
        cpl = self.get_cpl_by_id(id_cpl)
        return self.cpl_repo.soft_delete(cpl)

    def activate_cpl(self, id_cpl: int) -> CPL:
        """
        Re-activate a previously deactivated CPL.

        Args:
            id_cpl: CPL ID

        Returns:
            CPL: Activated CPL

        Raises:
            EntityNotFoundException: If CPL not found
        """
        cpl = self.get_cpl_by_id(id_cpl)
        return self.cpl_repo.update(cpl, is_active=True)

    def reorder_cpl(self, id_kurikulum: int, cpl_order: List[int]) -> List[CPL]:
        """
        Reorder CPL by providing new urutan.

        Args:
            id_kurikulum: Curriculum ID
            cpl_order: List of CPL IDs in desired order

        Returns:
            List[CPL]: Reordered CPL list

        Raises:
            EntityNotFoundException: If any CPL not found
        """
        updated_cpl = []

        for urutan, id_cpl in enumerate(cpl_order, start=1):
            cpl = self.get_cpl_by_id(id_cpl)

            # Verify CPL belongs to the curriculum
            if cpl.id_kurikulum != id_kurikulum:
                raise EntityNotFoundException("CPL", str(id_cpl))

            updated = self.cpl_repo.update(cpl, urutan=urutan)
            updated_cpl.append(updated)

        return updated_cpl
