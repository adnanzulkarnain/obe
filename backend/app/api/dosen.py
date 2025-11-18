from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models.dosen import Dosen
from app.models.user import User
from app.api.auth import get_current_user


# Schemas
class DosenBase(BaseModel):
    nama: str = Field(..., max_length=100)
    email: EmailStr
    nidn: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=20)


class DosenCreate(DosenBase):
    id_dosen: str = Field(..., max_length=20)
    id_prodi: str = Field(..., max_length=20)


class DosenUpdate(BaseModel):
    nama: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, pattern="^(aktif|cuti|pensiun)$")


class DosenResponse(DosenBase):
    id_dosen: str
    id_prodi: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


router = APIRouter()


@router.get("/", response_model=List[DosenResponse])
async def get_all_dosen(
    id_prodi: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all dosen with optional filters"""
    query = db.query(Dosen)

    if id_prodi:
        query = query.filter(Dosen.id_prodi == id_prodi)

    if status:
        query = query.filter(Dosen.status == status)

    return query.all()


@router.get("/{id_dosen}", response_model=DosenResponse)
async def get_dosen(
    id_dosen: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dosen by ID"""
    dosen = db.query(Dosen).filter(Dosen.id_dosen == id_dosen).first()

    if not dosen:
        raise HTTPException(status_code=404, detail="Dosen not found")

    return dosen


@router.post("/", response_model=DosenResponse, status_code=status.HTTP_201_CREATED)
async def create_dosen(
    dosen_data: DosenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new dosen"""
    if current_user.user_type not in ['admin']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if ID already exists
    if db.query(Dosen).filter(Dosen.id_dosen == dosen_data.id_dosen).first():
        raise HTTPException(status_code=400, detail="ID Dosen already exists")

    # Check if NIDN already exists
    if dosen_data.nidn and db.query(Dosen).filter(Dosen.nidn == dosen_data.nidn).first():
        raise HTTPException(status_code=400, detail="NIDN already exists")

    # Create dosen
    db_dosen = Dosen(
        **dosen_data.model_dump(),
        status='aktif'
    )

    db.add(db_dosen)
    db.commit()
    db.refresh(db_dosen)

    return db_dosen


@router.put("/{id_dosen}", response_model=DosenResponse)
async def update_dosen(
    id_dosen: str,
    dosen_data: DosenUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update dosen"""
    if current_user.user_type not in ['admin', 'kaprodi']:
        raise HTTPException(status_code=403, detail="Not authorized")

    dosen = db.query(Dosen).filter(Dosen.id_dosen == id_dosen).first()

    if not dosen:
        raise HTTPException(status_code=404, detail="Dosen not found")

    # Update fields
    for field, value in dosen_data.model_dump(exclude_unset=True).items():
        setattr(dosen, field, value)

    db.commit()
    db.refresh(dosen)

    return dosen
