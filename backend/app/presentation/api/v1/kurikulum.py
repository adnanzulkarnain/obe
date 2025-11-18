"""
Kurikulum API Router

REST API endpoints for curriculum management.
Following Clean Code: Clear naming, single responsibility, proper HTTP methods.
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.infrastructure.database import DatabaseManager
from app.application.use_cases import KurikulumUseCases
from app.presentation.schemas import (
    KurikulumCreateRequest,
    KurikulumUpdateRequest,
    KurikulumActivateRequest,
    KurikulumResponse,
    KurikulumListResponse,
    MessageResponse,
    KurikulumStatusEnum,
)
from app.domain.entities import KurikulumStatus

# Create router
router = APIRouter()


def get_db() -> Session:
    """
    Dependency for database session.

    Yields:
        Session: Database session
    """
    return DatabaseManager.get_session()


def get_kurikulum_use_cases(
    db: Session = Depends(get_db)
) -> KurikulumUseCases:
    """
    Dependency for Kurikulum use cases.

    Args:
        db: Database session

    Returns:
        KurikulumUseCases: Use cases instance
    """
    return KurikulumUseCases(db)


@router.post(
    "/",
    response_model=KurikulumResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new curriculum",
    description="Create a new curriculum for a study program"
)
def create_kurikulum(
    request: KurikulumCreateRequest,
    use_cases: KurikulumUseCases = Depends(get_kurikulum_use_cases)
) -> KurikulumResponse:
    """
    Create new curriculum.

    Args:
        request: Curriculum creation request
        use_cases: Kurikulum use cases

    Returns:
        KurikulumResponse: Created curriculum
    """
    kurikulum = use_cases.create_kurikulum(
        id_prodi=request.id_prodi,
        kode_kurikulum=request.kode_kurikulum,
        nama_kurikulum=request.nama_kurikulum,
        tahun_berlaku=request.tahun_berlaku,
        tahun_berakhir=request.tahun_berakhir,
        deskripsi=request.deskripsi,
        is_primary=request.is_primary,
    )

    return KurikulumResponse.model_validate(kurikulum)


@router.get(
    "/",
    response_model=KurikulumListResponse,
    summary="List curricula",
    description="Get list of curricula with optional filters"
)
def list_kurikulum(
    id_prodi: Optional[str] = Query(None, description="Filter by program study ID"),
    status_filter: Optional[KurikulumStatusEnum] = Query(None, alias="status", description="Filter by status"),
    use_cases: KurikulumUseCases = Depends(get_kurikulum_use_cases)
) -> KurikulumListResponse:
    """
    List curricula with optional filters.

    Args:
        id_prodi: Optional program study ID filter
        status_filter: Optional status filter
        use_cases: Kurikulum use cases

    Returns:
        KurikulumListResponse: List of curricula
    """
    # Convert enum to domain status if provided
    domain_status = None
    if status_filter:
        domain_status = KurikulumStatus(status_filter.value)

    curricula = use_cases.list_kurikulum(
        id_prodi=id_prodi,
        status=domain_status
    )

    return KurikulumListResponse(
        total=len(curricula),
        data=[KurikulumResponse.model_validate(k) for k in curricula]
    )


@router.get(
    "/{id_kurikulum}",
    response_model=KurikulumResponse,
    summary="Get curriculum by ID",
    description="Get detailed curriculum information including statistics"
)
def get_kurikulum(
    id_kurikulum: int,
    include_statistics: bool = Query(False, description="Include statistics (CPL, MK, student counts)"),
    use_cases: KurikulumUseCases = Depends(get_kurikulum_use_cases)
) -> KurikulumResponse:
    """
    Get curriculum by ID.

    Args:
        id_kurikulum: Curriculum ID
        include_statistics: Whether to include statistics
        use_cases: Kurikulum use cases

    Returns:
        KurikulumResponse: Curriculum details
    """
    if include_statistics:
        result = use_cases.get_kurikulum_with_statistics(id_kurikulum)
        kurikulum = result["kurikulum"]
        response = KurikulumResponse.model_validate(kurikulum)
        response.statistics = result["statistics"]
        return response
    else:
        kurikulum = use_cases.get_kurikulum_by_id(id_kurikulum)
        return KurikulumResponse.model_validate(kurikulum)


@router.put(
    "/{id_kurikulum}",
    response_model=KurikulumResponse,
    summary="Update curriculum",
    description="Update curriculum information (only for DRAFT and REVIEW status)"
)
def update_kurikulum(
    id_kurikulum: int,
    request: KurikulumUpdateRequest,
    use_cases: KurikulumUseCases = Depends(get_kurikulum_use_cases)
) -> KurikulumResponse:
    """
    Update curriculum.

    Args:
        id_kurikulum: Curriculum ID
        request: Update request
        use_cases: Kurikulum use cases

    Returns:
        KurikulumResponse: Updated curriculum
    """
    kurikulum = use_cases.update_kurikulum(
        id_kurikulum=id_kurikulum,
        nama_kurikulum=request.nama_kurikulum,
        tahun_berakhir=request.tahun_berakhir,
        deskripsi=request.deskripsi,
        nomor_sk=request.nomor_sk,
        tanggal_sk=request.tanggal_sk,
    )

    return KurikulumResponse.model_validate(kurikulum)


@router.delete(
    "/{id_kurikulum}",
    response_model=MessageResponse,
    summary="Delete curriculum",
    description="Delete curriculum (only DRAFT status can be deleted)"
)
def delete_kurikulum(
    id_kurikulum: int,
    use_cases: KurikulumUseCases = Depends(get_kurikulum_use_cases)
) -> MessageResponse:
    """
    Delete curriculum.

    Args:
        id_kurikulum: Curriculum ID
        use_cases: Kurikulum use cases

    Returns:
        MessageResponse: Success message
    """
    use_cases.delete_kurikulum(id_kurikulum)

    return MessageResponse(
        success=True,
        message=f"Kurikulum dengan ID {id_kurikulum} berhasil dihapus"
    )


@router.post(
    "/{id_kurikulum}/submit-review",
    response_model=KurikulumResponse,
    summary="Submit curriculum for review",
    description="Submit curriculum for review (DRAFT → REVIEW)"
)
def submit_for_review(
    id_kurikulum: int,
    use_cases: KurikulumUseCases = Depends(get_kurikulum_use_cases)
) -> KurikulumResponse:
    """
    Submit curriculum for review.

    Args:
        id_kurikulum: Curriculum ID
        use_cases: Kurikulum use cases

    Returns:
        KurikulumResponse: Updated curriculum
    """
    kurikulum = use_cases.submit_for_review(id_kurikulum)
    return KurikulumResponse.model_validate(kurikulum)


@router.post(
    "/{id_kurikulum}/approve",
    response_model=KurikulumResponse,
    summary="Approve curriculum",
    description="Approve curriculum (REVIEW → APPROVED)"
)
def approve_kurikulum(
    id_kurikulum: int,
    use_cases: KurikulumUseCases = Depends(get_kurikulum_use_cases)
) -> KurikulumResponse:
    """
    Approve curriculum.

    Args:
        id_kurikulum: Curriculum ID
        use_cases: Kurikulum use cases

    Returns:
        KurikulumResponse: Approved curriculum
    """
    kurikulum = use_cases.approve_kurikulum(id_kurikulum)
    return KurikulumResponse.model_validate(kurikulum)


@router.post(
    "/{id_kurikulum}/activate",
    response_model=KurikulumResponse,
    summary="Activate curriculum",
    description="Activate curriculum (APPROVED → AKTIF)"
)
def activate_kurikulum(
    id_kurikulum: int,
    request: KurikulumActivateRequest,
    use_cases: KurikulumUseCases = Depends(get_kurikulum_use_cases)
) -> KurikulumResponse:
    """
    Activate curriculum.

    Args:
        id_kurikulum: Curriculum ID
        request: Activation request with SK information
        use_cases: Kurikulum use cases

    Returns:
        KurikulumResponse: Activated curriculum
    """
    kurikulum = use_cases.activate_kurikulum(
        id_kurikulum=id_kurikulum,
        nomor_sk=request.nomor_sk,
        tanggal_sk=request.tanggal_sk,
        set_as_primary=request.set_as_primary,
    )

    return KurikulumResponse.model_validate(kurikulum)


@router.post(
    "/{id_kurikulum}/deactivate",
    response_model=KurikulumResponse,
    summary="Deactivate curriculum",
    description="Deactivate active curriculum (AKTIF → NON_AKTIF)"
)
def deactivate_kurikulum(
    id_kurikulum: int,
    use_cases: KurikulumUseCases = Depends(get_kurikulum_use_cases)
) -> KurikulumResponse:
    """
    Deactivate curriculum.

    Args:
        id_kurikulum: Curriculum ID
        use_cases: Kurikulum use cases

    Returns:
        KurikulumResponse: Deactivated curriculum
    """
    kurikulum = use_cases.deactivate_kurikulum(id_kurikulum)
    return KurikulumResponse.model_validate(kurikulum)


@router.get(
    "/prodi/{id_prodi}/active",
    response_model=KurikulumListResponse,
    summary="Get active curricula for program",
    description="Get all active curricula for a study program"
)
def get_active_curricula(
    id_prodi: str,
    use_cases: KurikulumUseCases = Depends(get_kurikulum_use_cases)
) -> KurikulumListResponse:
    """
    Get active curricula for a program.

    Args:
        id_prodi: Program study ID
        use_cases: Kurikulum use cases

    Returns:
        KurikulumListResponse: List of active curricula
    """
    curricula = use_cases.get_active_curricula(id_prodi)

    return KurikulumListResponse(
        total=len(curricula),
        data=[KurikulumResponse.model_validate(k) for k in curricula]
    )


@router.get(
    "/prodi/{id_prodi}/primary",
    response_model=KurikulumResponse,
    summary="Get primary curriculum for program",
    description="Get the primary curriculum for a study program"
)
def get_primary_curriculum(
    id_prodi: str,
    use_cases: KurikulumUseCases = Depends(get_kurikulum_use_cases)
) -> KurikulumResponse:
    """
    Get primary curriculum for a program.

    Args:
        id_prodi: Program study ID
        use_cases: Kurikulum use cases

    Returns:
        KurikulumResponse: Primary curriculum
    """
    from app.domain.exceptions import NotFoundException

    kurikulum = use_cases.get_primary_curriculum(id_prodi)

    if not kurikulum:
        raise NotFoundException(
            f"Tidak ada kurikulum primary untuk prodi '{id_prodi}'"
        )

    return KurikulumResponse.model_validate(kurikulum)
