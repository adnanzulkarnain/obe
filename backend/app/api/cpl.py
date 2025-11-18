from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.cpl import CPL
from app.models.kurikulum import Kurikulum
from app.models.user import User
from app.api.auth import get_current_user
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Schemas
class CPLBase(BaseModel):
    kode_cpl: str = Field(..., max_length=20)
    deskripsi: str
    kategori: str = Field(..., pattern="^(sikap|pengetahuan|keterampilan_umum|keterampilan_khusus)$")
    urutan: Optional[int] = None


class CPLCreate(CPLBase):
    id_kurikulum: int


class CPLUpdate(BaseModel):
    deskripsi: Optional[str] = None
    kategori: Optional[str] = Field(None, pattern="^(sikap|pengetahuan|keterampilan_umum|keterampilan_khusus)$")
    urutan: Optional[int] = None
    is_active: Optional[bool] = None


class CPLResponse(CPLBase):
    id_cpl: int
    id_kurikulum: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


router = APIRouter()


@router.get("/", response_model=List[CPLResponse])
async def get_all_cpl(
    id_kurikulum: int = None,
    kategori: str = None,
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all CPL with optional filters"""
    query = db.query(CPL)

    if id_kurikulum:
        query = query.filter(CPL.id_kurikulum == id_kurikulum)

    if kategori:
        query = query.filter(CPL.kategori == kategori)

    if is_active is not None:
        query = query.filter(CPL.is_active == is_active)

    return query.order_by(CPL.urutan).all()


@router.get("/{id_cpl}", response_model=CPLResponse)
async def get_cpl(
    id_cpl: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get CPL by ID"""
    cpl = db.query(CPL).filter(CPL.id_cpl == id_cpl).first()

    if not cpl:
        raise HTTPException(status_code=404, detail="CPL not found")

    return cpl


@router.post("/", response_model=CPLResponse, status_code=status.HTTP_201_CREATED)
async def create_cpl(
    cpl_data: CPLCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new CPL"""
    if current_user.user_type not in ['kaprodi', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if kurikulum exists
    kurikulum = db.query(Kurikulum).filter(Kurikulum.id_kurikulum == cpl_data.id_kurikulum).first()
    if not kurikulum:
        raise HTTPException(status_code=404, detail="Kurikulum not found")

    # Check for duplicate kode_cpl in same kurikulum
    existing = db.query(CPL).filter(
        CPL.id_kurikulum == cpl_data.id_kurikulum,
        CPL.kode_cpl == cpl_data.kode_cpl
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Kode CPL already exists in this kurikulum")

    # Create CPL
    db_cpl = CPL(**cpl_data.model_dump())
    db.add(db_cpl)
    db.commit()
    db.refresh(db_cpl)

    return db_cpl


@router.put("/{id_cpl}", response_model=CPLResponse)
async def update_cpl(
    id_cpl: int,
    cpl_data: CPLUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update CPL"""
    if current_user.user_type not in ['kaprodi', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    cpl = db.query(CPL).filter(CPL.id_cpl == id_cpl).first()

    if not cpl:
        raise HTTPException(status_code=404, detail="CPL not found")

    # Update fields
    for field, value in cpl_data.model_dump(exclude_unset=True).items():
        setattr(cpl, field, value)

    db.commit()
    db.refresh(cpl)

    return cpl


@router.delete("/{id_cpl}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cpl(
    id_cpl: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete CPL"""
    if current_user.user_type not in ['kaprodi', 'admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    cpl = db.query(CPL).filter(CPL.id_cpl == id_cpl).first()

    if not cpl:
        raise HTTPException(status_code=404, detail="CPL not found")

    # Soft delete
    cpl.is_active = False
    db.commit()

    return None
