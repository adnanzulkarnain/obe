from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, kurikulum, cpl, mahasiswa, dosen

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API untuk Sistem Informasi Kurikulum OBE dengan Multi-Curriculum Support",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(kurikulum.router, prefix="/api/v1/kurikulum", tags=["Kurikulum"])
app.include_router(cpl.router, prefix="/api/v1/cpl", tags=["CPL"])
app.include_router(mahasiswa.router, prefix="/api/v1/mahasiswa", tags=["Mahasiswa"])
app.include_router(dosen.router, prefix="/api/v1/dosen", tags=["Dosen"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OBE System API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
