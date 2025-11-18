from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class KurikulumBase(BaseModel):
    kode_kurikulum: str = Field(..., max_length=20)
    nama_kurikulum: str = Field(..., max_length=200)
    tahun_berlaku: int
    tahun_berakhir: Optional[int] = None
    deskripsi: Optional[str] = None
    nomor_sk: Optional[str] = Field(None, max_length=100)
    tanggal_sk: Optional[date] = None


class KurikulumCreate(KurikulumBase):
    id_prodi: str = Field(..., max_length=20)


class KurikulumUpdate(BaseModel):
    nama_kurikulum: Optional[str] = Field(None, max_length=200)
    tahun_berakhir: Optional[int] = None
    deskripsi: Optional[str] = None
    nomor_sk: Optional[str] = Field(None, max_length=100)
    tanggal_sk: Optional[date] = None


class KurikulumResponse(KurikulumBase):
    id_kurikulum: int
    id_prodi: str
    status: str
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KurikulumActivate(BaseModel):
    set_as_primary: bool = False


class KurikulumApprove(BaseModel):
    nomor_sk: str = Field(..., max_length=100)
    tanggal_sk: date
    approved_by: str
