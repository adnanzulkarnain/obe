from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.core.database import get_db
from app.models.kurikulum import Kurikulum
from app.models.user import User
from app.schemas.kurikulum import (
    KurikulumCreate,
    KurikulumUpdate,
    KurikulumResponse,
    KurikulumActivate,
    KurikulumApprove
)
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[KurikulumResponse])
async def get_all_kurikulum(
    id_prodi: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all kurikulum with optional filters"""
    query = db.query(Kurikulum)

    if id_prodi:
        query = query.filter(Kurikulum.id_prodi == id_prodi)

    if status:
        query = query.filter(Kurikulum.status == status)

    return query.all()


@router.get("/{id_kurikulum}", response_model=KurikulumResponse)
async def get_kurikulum(
    id_kurikulum: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get kurikulum by ID"""
    kurikulum = db.query(Kurikulum).filter(Kurikulum.id_kurikulum == id_kurikulum).first()

    if not kurikulum:
        raise HTTPException(status_code=404, detail="Kurikulum not found")

    return kurikulum


@router.post("/", response_model=KurikulumResponse, status_code=status.HTTP_201_CREATED)
async def create_kurikulum(
    kurikulum_data: KurikulumCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new kurikulum"""
    # Check if user is kaprodi or admin
    if current_user.user_type not in ['kaprodi', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check for duplicate kode_kurikulum in same prodi
    existing = db.query(Kurikulum).filter(
        Kurikulum.id_prodi == kurikulum_data.id_prodi,
        Kurikulum.kode_kurikulum == kurikulum_data.kode_kurikulum
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Kode kurikulum already exists in this prodi")

    # Create kurikulum
    db_kurikulum = Kurikulum(
        **kurikulum_data.model_dump(),
        status='draft'
    )

    db.add(db_kurikulum)
    db.commit()
    db.refresh(db_kurikulum)

    return db_kurikulum


@router.put("/{id_kurikulum}", response_model=KurikulumResponse)
async def update_kurikulum(
    id_kurikulum: int,
    kurikulum_data: KurikulumUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update kurikulum"""
    if current_user.user_type not in ['kaprodi', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    kurikulum = db.query(Kurikulum).filter(Kurikulum.id_kurikulum == id_kurikulum).first()

    if not kurikulum:
        raise HTTPException(status_code=404, detail="Kurikulum not found")

    # Only allow update if status is draft or review
    if kurikulum.status not in ['draft', 'review']:
        raise HTTPException(status_code=400, detail="Cannot update kurikulum with current status")

    # Update fields
    for field, value in kurikulum_data.model_dump(exclude_unset=True).items():
        setattr(kurikulum, field, value)

    db.commit()
    db.refresh(kurikulum)

    return kurikulum


@router.post("/{id_kurikulum}/approve", response_model=KurikulumResponse)
async def approve_kurikulum(
    id_kurikulum: int,
    approval_data: KurikulumApprove,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve kurikulum"""
    if current_user.user_type not in ['kaprodi', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    kurikulum = db.query(Kurikulum).filter(Kurikulum.id_kurikulum == id_kurikulum).first()

    if not kurikulum:
        raise HTTPException(status_code=404, detail="Kurikulum not found")

    if kurikulum.status not in ['review', 'draft']:
        raise HTTPException(status_code=400, detail="Kurikulum cannot be approved with current status")

    # Update status and SK info
    kurikulum.status = 'approved'
    kurikulum.nomor_sk = approval_data.nomor_sk
    kurikulum.tanggal_sk = approval_data.tanggal_sk

    db.commit()
    db.refresh(kurikulum)

    return kurikulum


@router.post("/{id_kurikulum}/activate", response_model=KurikulumResponse)
async def activate_kurikulum(
    id_kurikulum: int,
    activate_data: KurikulumActivate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activate kurikulum"""
    if current_user.user_type not in ['kaprodi', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    kurikulum = db.query(Kurikulum).filter(Kurikulum.id_kurikulum == id_kurikulum).first()

    if not kurikulum:
        raise HTTPException(status_code=404, detail="Kurikulum not found")

    if kurikulum.status != 'approved':
        raise HTTPException(status_code=400, detail="Kurikulum must be approved before activation")

    # If setting as primary, remove primary flag from others
    if activate_data.set_as_primary:
        db.query(Kurikulum).filter(
            Kurikulum.id_prodi == kurikulum.id_prodi,
            Kurikulum.is_primary == True
        ).update({"is_primary": False})

    # Activate kurikulum
    kurikulum.status = 'aktif'
    kurikulum.is_primary = activate_data.set_as_primary

    db.commit()
    db.refresh(kurikulum)

    return kurikulum


@router.post("/{id_kurikulum}/deactivate", response_model=KurikulumResponse)
async def deactivate_kurikulum(
    id_kurikulum: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate kurikulum"""
    if current_user.user_type not in ['kaprodi', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    kurikulum = db.query(Kurikulum).filter(Kurikulum.id_kurikulum == id_kurikulum).first()

    if not kurikulum:
        raise HTTPException(status_code=404, detail="Kurikulum not found")

    if kurikulum.status != 'aktif':
        raise HTTPException(status_code=400, detail="Only active kurikulum can be deactivated")

    kurikulum.status = 'non-aktif'
    kurikulum.is_primary = False

    db.commit()
    db.refresh(kurikulum)

    return kurikulum
