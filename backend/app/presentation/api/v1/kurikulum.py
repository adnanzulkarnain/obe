"""
Kurikulum API Endpoints

Handles curriculum management operations.
Following Clean Code: RESTful design, Clear documentation, Type safety.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path, status

from app.application.services.kurikulum_service import KurikulumService
from app.infrastructure.models.kurikulum_models import KurikulumStatus, Kurikulum
from app.infrastructure.models.user_models import User
from app.presentation.schemas.kurikulum_schemas import (
    KurikulumCreate,
    KurikulumUpdate,
    KurikulumResponse,
    KurikulumWithStats,
    KurikulumActivateRequest
)
from app.presentation.schemas.base_schemas import (
    SuccessResponse,
    StatusResponse,
    PaginatedResponse,
    PaginationParams,
    PaginationMeta
)
from app.presentation.dependencies import (
    get_kurikulum_service,
    get_current_active_user,
    require_kaprodi_user
)


router = APIRouter()


@router.post(
    "",
    response_model=SuccessResponse[KurikulumResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create new curriculum",
    description="Create a new curriculum for a program study. Requires kaprodi or admin role."
)
def create_kurikulum(
    kurikulum_data: KurikulumCreate,
    kurikulum_service: KurikulumService = Depends(get_kurikulum_service),
    current_user: User = Depends(require_kaprodi_user)
):
    """
    Create a new curriculum.

    **Required role**: kaprodi or admin

    **Business Rules**:
    - Curriculum code must be unique within the program
    - Initial status will be 'draft'
    - tahun_berakhir must be after tahun_berlaku if provided

    Returns the created curriculum.
    """
    kurikulum = kurikulum_service.create_kurikulum(kurikulum_data)

    return SuccessResponse(
        success=True,
        message="Kurikulum berhasil dibuat",
        data=KurikulumResponse.model_validate(kurikulum)
    )


@router.get(
    "",
    response_model=SuccessResponse[List[KurikulumResponse]],
    summary="Get all curricula",
    description="Get list of all curricula with optional filtering."
)
def get_all_kurikulum(
    id_prodi: Optional[str] = Query(None, description="Filter by program study ID"),
    status: Optional[KurikulumStatus] = Query(None, description="Filter by status"),
    kurikulum_service: KurikulumService = Depends(get_kurikulum_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all curricula with optional filtering.

    **Filters**:
    - **id_prodi**: Filter by program study
    - **status**: Filter by curriculum status

    Returns list of curricula.
    """
    curricula = kurikulum_service.get_all_kurikulum(
        id_prodi=id_prodi,
        status=status
    )

    return SuccessResponse(
        success=True,
        message=f"Ditemukan {len(curricula)} kurikulum",
        data=[KurikulumResponse.model_validate(k) for k in curricula]
    )


@router.get(
    "/{id_kurikulum}",
    response_model=SuccessResponse[KurikulumResponse],
    summary="Get curriculum by ID",
    description="Get detailed information of a specific curriculum."
)
def get_kurikulum(
    id_kurikulum: int = Path(..., description="Curriculum ID"),
    kurikulum_service: KurikulumService = Depends(get_kurikulum_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get curriculum by ID.

    Returns curriculum details.
    """
    kurikulum = kurikulum_service.get_kurikulum_by_id(id_kurikulum)

    return SuccessResponse(
        success=True,
        message="Kurikulum berhasil diambil",
        data=KurikulumResponse.model_validate(kurikulum)
    )


@router.get(
    "/{id_kurikulum}/statistics",
    response_model=SuccessResponse[KurikulumWithStats],
    summary="Get curriculum with statistics",
    description="Get curriculum with statistics (CPL count, MK count, student count)."
)
def get_kurikulum_statistics(
    id_kurikulum: int = Path(..., description="Curriculum ID"),
    kurikulum_service: KurikulumService = Depends(get_kurikulum_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get curriculum with statistics.

    Returns curriculum with:
    - Total CPL
    - Total MataKuliah
    - Total Mahasiswa

    Useful for dashboard and overview.
    """
    data = kurikulum_service.get_kurikulum_with_statistics(id_kurikulum)

    kurikulum = data['kurikulum']
    stats = data['statistics']

    response_data = KurikulumWithStats(
        **kurikulum.__dict__,
        total_cpl=stats['total_cpl'],
        total_matakuliah=stats['total_matakuliah'],
        total_mahasiswa=stats['total_mahasiswa']
    )

    return SuccessResponse(
        success=True,
        message="Statistik kurikulum berhasil diambil",
        data=response_data
    )


@router.get(
    "/prodi/{id_prodi}/active",
    response_model=SuccessResponse[List[KurikulumResponse]],
    summary="Get active curricula for a program",
    description="Get all active curricula for a program study."
)
def get_active_kurikulum(
    id_prodi: str = Path(..., description="Program study ID"),
    kurikulum_service: KurikulumService = Depends(get_kurikulum_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get active curricula for a program.

    **Business Rule BR-K05**: Multiple active curricula can run in parallel.

    Returns list of active curricula.
    """
    curricula = kurikulum_service.get_active_kurikulum(id_prodi)

    return SuccessResponse(
        success=True,
        message=f"Ditemukan {len(curricula)} kurikulum aktif",
        data=[KurikulumResponse.model_validate(k) for k in curricula]
    )


@router.get(
    "/prodi/{id_prodi}/primary",
    response_model=SuccessResponse[Optional[KurikulumResponse]],
    summary="Get primary curriculum",
    description="Get the primary curriculum for a program study."
)
def get_primary_kurikulum(
    id_prodi: str = Path(..., description="Program study ID"),
    kurikulum_service: KurikulumService = Depends(get_kurikulum_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get primary curriculum for a program.

    **Business Rule BR-K08**: Only 1 primary curriculum per program.

    Returns primary curriculum or null if not set.
    """
    kurikulum = kurikulum_service.get_primary_kurikulum(id_prodi)

    data = KurikulumResponse.model_validate(kurikulum) if kurikulum else None

    return SuccessResponse(
        success=True,
        message="Kurikulum primary berhasil diambil" if kurikulum else "Tidak ada kurikulum primary",
        data=data
    )


@router.put(
    "/{id_kurikulum}",
    response_model=SuccessResponse[KurikulumResponse],
    summary="Update curriculum",
    description="Update curriculum information. Only allowed for draft/review status."
)
def update_kurikulum(
    id_kurikulum: int = Path(..., description="Curriculum ID"),
    kurikulum_data: KurikulumUpdate = ...,
    kurikulum_service: KurikulumService = Depends(get_kurikulum_service),
    current_user: User = Depends(require_kaprodi_user)
):
    """
    Update curriculum information.

    **Required role**: kaprodi or admin

    **Restrictions**:
    - Can only update if status is 'draft' or 'review'
    - Cannot change kode_kurikulum or id_prodi

    Returns updated curriculum.
    """
    kurikulum = kurikulum_service.update_kurikulum(id_kurikulum, kurikulum_data)

    return SuccessResponse(
        success=True,
        message="Kurikulum berhasil diupdate",
        data=KurikulumResponse.model_validate(kurikulum)
    )


@router.post(
    "/{id_kurikulum}/submit",
    response_model=SuccessResponse[KurikulumResponse],
    summary="Submit curriculum for review",
    description="Change curriculum status from draft to review."
)
def submit_for_review(
    id_kurikulum: int = Path(..., description="Curriculum ID"),
    kurikulum_service: KurikulumService = Depends(get_kurikulum_service),
    current_user: User = Depends(require_kaprodi_user)
):
    """
    Submit curriculum for review.

    **Required role**: kaprodi or admin

    **Status transition**: draft → review

    Returns updated curriculum.
    """
    kurikulum = kurikulum_service.submit_for_review(id_kurikulum)

    return SuccessResponse(
        success=True,
        message="Kurikulum berhasil disubmit untuk review",
        data=KurikulumResponse.model_validate(kurikulum)
    )


@router.post(
    "/{id_kurikulum}/approve",
    response_model=SuccessResponse[KurikulumResponse],
    summary="Approve curriculum",
    description="Approve curriculum after review."
)
def approve_kurikulum(
    id_kurikulum: int = Path(..., description="Curriculum ID"),
    kurikulum_service: KurikulumService = Depends(get_kurikulum_service),
    current_user: User = Depends(require_kaprodi_user)
):
    """
    Approve curriculum.

    **Required role**: kaprodi or admin

    **Status transition**: review → approved

    Returns approved curriculum.
    """
    kurikulum = kurikulum_service.approve_kurikulum(id_kurikulum)

    return SuccessResponse(
        success=True,
        message="Kurikulum berhasil diapprove",
        data=KurikulumResponse.model_validate(kurikulum)
    )


@router.post(
    "/{id_kurikulum}/activate",
    response_model=SuccessResponse[KurikulumResponse],
    summary="Activate curriculum",
    description="Activate curriculum for use by students."
)
def activate_kurikulum(
    id_kurikulum: int = Path(..., description="Curriculum ID"),
    request_data: KurikulumActivateRequest = ...,
    kurikulum_service: KurikulumService = Depends(get_kurikulum_service),
    current_user: User = Depends(require_kaprodi_user)
):
    """
    Activate curriculum.

    **Required role**: kaprodi or admin

    **Status transition**: approved → aktif

    **Business Rule BR-K08**: If set_as_primary=true, removes primary flag from other curricula.

    Returns activated curriculum.
    """
    kurikulum = kurikulum_service.activate_kurikulum(
        id_kurikulum,
        request_data.set_as_primary
    )

    return SuccessResponse(
        success=True,
        message="Kurikulum berhasil diaktifkan",
        data=KurikulumResponse.model_validate(kurikulum)
    )


@router.post(
    "/{id_kurikulum}/deactivate",
    response_model=SuccessResponse[KurikulumResponse],
    summary="Deactivate curriculum",
    description="Deactivate curriculum (no new students, existing students continue)."
)
def deactivate_kurikulum(
    id_kurikulum: int = Path(..., description="Curriculum ID"),
    kurikulum_service: KurikulumService = Depends(get_kurikulum_service),
    current_user: User = Depends(require_kaprodi_user)
):
    """
    Deactivate curriculum.

    **Required role**: kaprodi or admin

    **Status transition**: aktif → non-aktif

    Curriculum doesn't accept new students but existing students can continue.

    Returns deactivated curriculum.
    """
    kurikulum = kurikulum_service.deactivate_kurikulum(id_kurikulum)

    return SuccessResponse(
        success=True,
        message="Kurikulum berhasil dinonaktifkan",
        data=KurikulumResponse.model_validate(kurikulum)
    )


@router.post(
    "/{id_kurikulum}/archive",
    response_model=SuccessResponse[KurikulumResponse],
    summary="Archive curriculum",
    description="Archive curriculum (only if no active students)."
)
def archive_kurikulum(
    id_kurikulum: int = Path(..., description="Curriculum ID"),
    kurikulum_service: KurikulumService = Depends(get_kurikulum_service),
    current_user: User = Depends(require_kaprodi_user)
):
    """
    Archive curriculum.

    **Required role**: kaprodi or admin

    **Restrictions**: Can only archive if no active students are using it.

    Returns archived curriculum.
    """
    kurikulum = kurikulum_service.archive_kurikulum(id_kurikulum)

    return SuccessResponse(
        success=True,
        message="Kurikulum berhasil diarsipkan",
        data=KurikulumResponse.model_validate(kurikulum)
    )
