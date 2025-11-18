from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models.mahasiswa import Mahasiswa
from app.models.kurikulum import Kurikulum
from app.models.user import User
from app.api.auth import get_current_user


# Schemas
class MahasiswaBase(BaseModel):
    nama: str = Field(..., max_length=100)
    email: EmailStr
    angkatan: str = Field(..., max_length=10)


class MahasiswaCreate(MahasiswaBase):
    nim: str = Field(..., max_length=20)
    id_prodi: str = Field(..., max_length=20)
    id_kurikulum: int


class MahasiswaUpdate(BaseModel):
    nama: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    status: Optional[str] = Field(None, pattern="^(aktif|cuti|lulus|DO)$")


class MahasiswaResponse(MahasiswaBase):
    nim: str
    id_prodi: str
    id_kurikulum: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


router = APIRouter()


@router.get("/", response_model=List[MahasiswaResponse])
async def get_all_mahasiswa(
    id_prodi: str = None,
    id_kurikulum: int = None,
    angkatan: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all mahasiswa with optional filters"""
    query = db.query(Mahasiswa)

    if id_prodi:
        query = query.filter(Mahasiswa.id_prodi == id_prodi)

    if id_kurikulum:
        query = query.filter(Mahasiswa.id_kurikulum == id_kurikulum)

    if angkatan:
        query = query.filter(Mahasiswa.angkatan == angkatan)

    if status:
        query = query.filter(Mahasiswa.status == status)

    return query.all()


@router.get("/{nim}", response_model=MahasiswaResponse)
async def get_mahasiswa(
    nim: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get mahasiswa by NIM"""
    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.nim == nim).first()

    if not mahasiswa:
        raise HTTPException(status_code=404, detail="Mahasiswa not found")

    return mahasiswa


@router.post("/", response_model=MahasiswaResponse, status_code=status.HTTP_201_CREATED)
async def create_mahasiswa(
    mahasiswa_data: MahasiswaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new mahasiswa"""
    if current_user.user_type not in ['admin', 'kaprodi']:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if NIM already exists
    if db.query(Mahasiswa).filter(Mahasiswa.nim == mahasiswa_data.nim).first():
        raise HTTPException(status_code=400, detail="NIM already exists")

    # Check if kurikulum exists and is active
    kurikulum = db.query(Kurikulum).filter(Kurikulum.id_kurikulum == mahasiswa_data.id_kurikulum).first()
    if not kurikulum:
        raise HTTPException(status_code=404, detail="Kurikulum not found")

    if kurikulum.status not in ['aktif', 'approved']:
        raise HTTPException(status_code=400, detail="Kurikulum must be active")

    # Create mahasiswa
    db_mahasiswa = Mahasiswa(
        **mahasiswa_data.model_dump(),
        status='aktif'
    )

    db.add(db_mahasiswa)
    db.commit()
    db.refresh(db_mahasiswa)

    return db_mahasiswa


@router.put("/{nim}", response_model=MahasiswaResponse)
async def update_mahasiswa(
    nim: str,
    mahasiswa_data: MahasiswaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update mahasiswa (curriculum cannot be changed)"""
    if current_user.user_type not in ['admin', 'kaprodi']:
        raise HTTPException(status_code=403, detail="Not authorized")

    mahasiswa = db.query(Mahasiswa).filter(Mahasiswa.nim == nim).first()

    if not mahasiswa:
        raise HTTPException(status_code=404, detail="Mahasiswa not found")

    # Update fields (excluding id_kurikulum which is immutable)
    for field, value in mahasiswa_data.model_dump(exclude_unset=True).items():
        setattr(mahasiswa, field, value)

    db.commit()
    db.refresh(mahasiswa)

    return mahasiswa
