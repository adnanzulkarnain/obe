"""
MataKuliah Service

Business logic for course (Mata Kuliah) management.
Following Clean Code: Business rule enforcement, Clear naming.
"""

from typing import List, Dict
from sqlalchemy.orm import Session

from app.infrastructure.repositories.matakuliah_repository import MataKuliahRepository
from app.infrastructure.models.kurikulum_models import MataKuliah, JenisMK
from app.presentation.schemas.kurikulum_schemas import (
    MataKuliahCreate,
    MataKuliahUpdate
)
from app.domain.exceptions import (
    EntityNotFoundException,
    DuplicateEntityException,
    InvalidOperationException
)


class MataKuliahService:
    """
    Handles course management operations.

    Responsibilities:
    - Course CRUD operations
    - Course statistics and organization
    - Business rule enforcement (BR-K02, BR-K03)
    """

    def __init__(self, session: Session):
        """
        Initialize MataKuliah service.

        Args:
            session: Database session for data access
        """
        self.session = session
        self.mk_repo = MataKuliahRepository(session)

    def create_matakuliah(self, mk_data: MataKuliahCreate) -> MataKuliah:
        """
        Create a new course.

        Business Rule BR-K02: Same kode_mk can exist in different curricula.

        Args:
            mk_data: Course creation data

        Returns:
            MataKuliah: Newly created course

        Raises:
            DuplicateEntityException: If course already exists in this curriculum
        """
        # Check for duplicate within curriculum
        # BR-K02: Same code can exist in different curricula
        if self.mk_repo.check_duplicate_code(
            mk_data.kode_mk,
            mk_data.id_kurikulum
        ):
            raise DuplicateEntityException(
                "MataKuliah",
                "kode_mk",
                f"{mk_data.kode_mk} (kurikulum: {mk_data.id_kurikulum})"
            )

        # Create course
        mk = self.mk_repo.create(
            kode_mk=mk_data.kode_mk,
            id_kurikulum=mk_data.id_kurikulum,
            nama_mk=mk_data.nama_mk,
            nama_mk_eng=mk_data.nama_mk_eng,
            sks=mk_data.sks,
            semester=mk_data.semester,
            rumpun=mk_data.rumpun,
            jenis_mk=mk_data.jenis_mk,
            is_active=True
        )

        return mk

    def get_matakuliah_by_composite_key(
        self,
        kode_mk: str,
        id_kurikulum: int
    ) -> MataKuliah:
        """
        Get course by composite primary key.

        Args:
            kode_mk: Course code
            id_kurikulum: Curriculum ID

        Returns:
            MataKuliah: Course instance

        Raises:
            EntityNotFoundException: If course not found
        """
        mk = self.mk_repo.get_by_composite_key(kode_mk, id_kurikulum)
        if not mk:
            raise EntityNotFoundException(
                "MataKuliah",
                f"{kode_mk} (kurikulum: {id_kurikulum})"
            )
        return mk

    def get_matakuliah_by_kurikulum(
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
            List[MataKuliah]: List of courses ordered by semester
        """
        return self.mk_repo.get_by_kurikulum(id_kurikulum, active_only)

    def get_matakuliah_by_semester(
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
        return self.mk_repo.get_by_semester(id_kurikulum, semester)

    def get_matakuliah_by_jenis(
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
        return self.mk_repo.get_by_jenis(id_kurikulum, jenis_mk)

    def calculate_total_sks(self, id_kurikulum: int) -> int:
        """
        Calculate total SKS in a curriculum.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            int: Total credit hours
        """
        return self.mk_repo.calculate_total_sks(id_kurikulum)

    def get_statistics_by_semester(self, id_kurikulum: int) -> Dict:
        """
        Get course statistics grouped by semester.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            dict: Statistics with count and total_sks per semester
        """
        return self.mk_repo.get_statistics_by_semester(id_kurikulum)

    def update_matakuliah(
        self,
        kode_mk: str,
        id_kurikulum: int,
        mk_data: MataKuliahUpdate
    ) -> MataKuliah:
        """
        Update course information.

        Note: kode_mk and id_kurikulum cannot be changed (composite PK).

        Args:
            kode_mk: Course code
            id_kurikulum: Curriculum ID
            mk_data: Updated course data

        Returns:
            MataKuliah: Updated course

        Raises:
            EntityNotFoundException: If course not found
        """
        mk = self.get_matakuliah_by_composite_key(kode_mk, id_kurikulum)

        # Update only provided fields
        update_dict = mk_data.model_dump(exclude_unset=True)
        return self.mk_repo.update(mk, **update_dict)

    def deactivate_matakuliah(
        self,
        kode_mk: str,
        id_kurikulum: int
    ) -> MataKuliah:
        """
        Deactivate a course (soft delete).

        Business Rule BR-K03: MK cannot be hard deleted.

        Args:
            kode_mk: Course code
            id_kurikulum: Curriculum ID

        Returns:
            MataKuliah: Deactivated course

        Raises:
            EntityNotFoundException: If course not found
        """
        return self.mk_repo.soft_delete_by_composite_key(kode_mk, id_kurikulum)

    def activate_matakuliah(
        self,
        kode_mk: str,
        id_kurikulum: int
    ) -> MataKuliah:
        """
        Re-activate a previously deactivated course.

        Args:
            kode_mk: Course code
            id_kurikulum: Curriculum ID

        Returns:
            MataKuliah: Activated course

        Raises:
            EntityNotFoundException: If course not found
        """
        mk = self.get_matakuliah_by_composite_key(kode_mk, id_kurikulum)
        return self.mk_repo.update(mk, is_active=True)

    def get_curriculum_structure(self, id_kurikulum: int) -> Dict:
        """
        Get complete curriculum structure organized by semester.

        Useful for displaying curriculum roadmap.

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            dict: Curriculum structure with courses grouped by semester
        """
        all_mk = self.get_matakuliah_by_kurikulum(id_kurikulum)

        # Group by semester
        structure = {}
        for mk in all_mk:
            semester = mk.semester
            if semester not in structure:
                structure[semester] = {
                    'courses': [],
                    'total_sks': 0,
                    'wajib_count': 0,
                    'pilihan_count': 0
                }

            structure[semester]['courses'].append(mk)
            structure[semester]['total_sks'] += mk.sks

            if mk.jenis_mk == JenisMK.WAJIB:
                structure[semester]['wajib_count'] += 1
            elif mk.jenis_mk == JenisMK.PILIHAN:
                structure[semester]['pilihan_count'] += 1

        return structure

    def validate_curriculum_completeness(self, id_kurikulum: int) -> Dict:
        """
        Validate if curriculum has complete structure.

        Checks:
        - Total SKS meets minimum requirements (usually 144 for S1)
        - All semesters have courses
        - Balance of wajib vs pilihan courses

        Args:
            id_kurikulum: Curriculum ID

        Returns:
            dict: Validation results with warnings/errors
        """
        total_sks = self.calculate_total_sks(id_kurikulum)
        stats = self.get_statistics_by_semester(id_kurikulum)
        all_mk = self.get_matakuliah_by_kurikulum(id_kurikulum)

        # Count by type
        wajib_count = len([mk for mk in all_mk if mk.jenis_mk == JenisMK.WAJIB])
        pilihan_count = len([mk for mk in all_mk if mk.jenis_mk == JenisMK.PILIHAN])

        warnings = []
        errors = []

        # Validate minimum SKS (144 for S1)
        if total_sks < 144:
            errors.append(f"Total SKS ({total_sks}) kurang dari minimum 144")

        # Check empty semesters (1-8 for regular program)
        for sem in range(1, 9):
            if sem not in stats or stats[sem]['count'] == 0:
                warnings.append(f"Semester {sem} tidak memiliki mata kuliah")

        # Check if has both wajib and pilihan
        if wajib_count == 0:
            errors.append("Tidak ada mata kuliah wajib")
        if pilihan_count == 0:
            warnings.append("Tidak ada mata kuliah pilihan")

        return {
            'is_valid': len(errors) == 0,
            'total_sks': total_sks,
            'total_courses': len(all_mk),
            'wajib_count': wajib_count,
            'pilihan_count': pilihan_count,
            'errors': errors,
            'warnings': warnings
        }
