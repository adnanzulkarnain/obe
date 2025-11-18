# OBE System - Implementation Documentation

**Version:** 3.0.0
**Date:** November 18, 2025
**Status:** Development Ready

---

## 🎯 Overview

Sistem Informasi Kurikulum OBE (Outcome-Based Education) adalah platform digital komprehensif untuk mendukung implementasi OBE di perguruan tinggi dengan fitur utama **Multi-Curriculum Management**.

### Key Features

- ✅ **Multi-Curriculum Support** - Kelola beberapa kurikulum secara paralel
- ✅ **CPL & CPMK Management** - Definisi dan pemetaan capaian pembelajaran
- ✅ **RPS Digital** - Pembuatan dan approval RPS elektronik
- ✅ **Sistem Penilaian Otomatis** - Perhitungan ketercapaian CPMK & CPL
- ✅ **RESTful API** - Modern API architecture dengan FastAPI
- ✅ **Docker Support** - Easy deployment dengan Docker Compose

---

## 🏗️ Architecture

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend** | FastAPI | 0.115.0 |
| **Database** | PostgreSQL | 15+ |
| **Cache** | Redis | 7+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Auth** | JWT + OAuth2 | - |
| **Containerization** | Docker | - |

### Project Structure

```
obe/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   ├── auth.py
│   │   │   ├── kurikulum.py
│   │   │   ├── cpl.py
│   │   │   ├── mahasiswa.py
│   │   │   └── dosen.py
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── kurikulum.py
│   │   │   ├── cpl.py
│   │   │   ├── cpmk.py
│   │   │   ├── matakuliah.py
│   │   │   ├── rps.py
│   │   │   ├── kelas.py
│   │   │   ├── mahasiswa.py
│   │   │   ├── dosen.py
│   │   │   └── penilaian.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── auth.py
│   │   │   └── kurikulum.py
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   └── main.py            # FastAPI application
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                   # NextJS Frontend (to be implemented)
├── config/                     # Configuration files
├── docker-compose.yml         # Docker Compose configuration
├── OBE-Database-Schema-v3-WITH-KURIKULUM.sql
├── OBE-System-Specification-Document.md
├── Implementation-Guide-Quick-Reference.md
├── Use-Cases-Kurikulum-Management.md
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd obe
   ```

2. **Setup environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Initialize database**

   The database will be automatically initialized with the schema from `OBE-Database-Schema-v3-WITH-KURIKULUM.sql`.

5. **Access the application**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

### Manual Setup (Without Docker)

1. **Install PostgreSQL and Redis**

2. **Create database**
   ```bash
   createdb obe_system
   psql -d obe_system -f OBE-Database-Schema-v3-WITH-KURIKULUM.sql
   ```

3. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## 📚 API Documentation

### Authentication Endpoints

#### POST /api/v1/auth/login
Login to get access token

**Request:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_type": "admin",
  "username": "admin"
}
```

#### POST /api/v1/auth/register
Register new user

**Request:**
```json
{
  "username": "dosen001",
  "email": "dosen@example.com",
  "password": "password123",
  "user_type": "dosen",
  "ref_id": "D001"
}
```

#### GET /api/v1/auth/me
Get current user info (requires authentication)

### Kurikulum Endpoints

#### GET /api/v1/kurikulum
Get all kurikulum

**Query Parameters:**
- `id_prodi` (optional): Filter by prodi
- `status` (optional): Filter by status

#### POST /api/v1/kurikulum
Create new kurikulum (Kaprodi/Admin only)

**Request:**
```json
{
  "id_prodi": "TIF",
  "kode_kurikulum": "K2024",
  "nama_kurikulum": "Kurikulum OBE 2024",
  "tahun_berlaku": 2024,
  "deskripsi": "Kurikulum berbasis OBE"
}
```

#### GET /api/v1/kurikulum/{id_kurikulum}
Get kurikulum by ID

#### POST /api/v1/kurikulum/{id_kurikulum}/approve
Approve kurikulum

**Request:**
```json
{
  "nomor_sk": "SK/001/2024",
  "tanggal_sk": "2024-01-15",
  "approved_by": "KAPRODI001"
}
```

#### POST /api/v1/kurikulum/{id_kurikulum}/activate
Activate kurikulum

**Request:**
```json
{
  "set_as_primary": true
}
```

### CPL Endpoints

#### GET /api/v1/cpl
Get all CPL

**Query Parameters:**
- `id_kurikulum` (optional): Filter by kurikulum
- `kategori` (optional): Filter by kategori
- `is_active` (optional): Filter by active status

#### POST /api/v1/cpl
Create new CPL

**Request:**
```json
{
  "id_kurikulum": 1,
  "kode_cpl": "CPL-1",
  "deskripsi": "Mampu mengaplikasikan pemikiran logis...",
  "kategori": "keterampilan_khusus",
  "urutan": 1
}
```

### Mahasiswa Endpoints

#### GET /api/v1/mahasiswa
Get all mahasiswa

**Query Parameters:**
- `id_prodi`: Filter by prodi
- `id_kurikulum`: Filter by kurikulum
- `angkatan`: Filter by angkatan
- `status`: Filter by status

#### POST /api/v1/mahasiswa
Create new mahasiswa

**Request:**
```json
{
  "nim": "2024001",
  "nama": "John Doe",
  "email": "john@example.com",
  "id_prodi": "TIF",
  "id_kurikulum": 1,
  "angkatan": "2024"
}
```

**Note:** Once a student is assigned to a kurikulum, it **cannot be changed** (immutable as per BR-K01).

---

## 🔐 Security

### Authentication Flow

1. User login with username/password
2. Backend validates credentials
3. Generate JWT access token (2 hours expiry)
4. Generate JWT refresh token (7 days expiry)
5. Client stores tokens
6. Client sends access token in Authorization header for protected endpoints
7. When access token expires, use refresh token to get new tokens

### Authorization

Role-based access control (RBAC):
- **Admin**: Full access to all endpoints
- **Kaprodi**: Manage kurikulum, CPL, approve RPS, manage users
- **Dosen**: Create RPS, manage CPMK, input nilai
- **Mahasiswa**: View only access

---

## 🗄️ Database Schema

The system uses PostgreSQL with the following core tables:

### Core Entities

1. **kurikulum** - Multiple curricula per prodi
2. **cpl** - Learning outcomes tied to kurikulum
3. **matakuliah** - Courses with composite key (kode_mk, id_kurikulum)
4. **rps** - Course syllabi
5. **cpmk** - Course learning outcomes
6. **kelas** - Class instances
7. **enrollment** - Student enrollments
8. **mahasiswa** - Students (immutable curriculum assignment)
9. **dosen** - Lecturers
10. **penilaian** - Assessment components

### Business Rules Enforced

| Rule ID | Description | Implementation |
|---------|-------------|----------------|
| BR-K01 | Student curriculum is immutable | Trigger prevents UPDATE on id_kurikulum |
| BR-K02 | Same MK code can exist in different curricula | Composite PK: (kode_mk, id_kurikulum) |
| BR-K03 | MK cannot be hard deleted | Soft delete only (is_active flag) |
| BR-K04 | Student can only enroll in their curriculum | Validation in enrollment endpoint |
| BR-K05 | Support parallel curricula | Multiple active curricula allowed |

For complete schema, see: `OBE-Database-Schema-v3-WITH-KURIKULUM.sql`

---

## 🧪 Testing

### Manual API Testing

Use the interactive API documentation at http://localhost:8000/docs

**Test Flow:**

1. **Register a user**
   - POST /api/v1/auth/register
   - Create admin, kaprodi, dosen, mahasiswa users

2. **Login**
   - POST /api/v1/auth/login
   - Get access token

3. **Create Kurikulum**
   - POST /api/v1/kurikulum
   - Use admin/kaprodi token

4. **Add CPL**
   - POST /api/v1/cpl
   - Associate with kurikulum

5. **Add Mahasiswa**
   - POST /api/v1/mahasiswa
   - Assign to kurikulum (immutable!)

### Automated Testing

```bash
# Install pytest
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

---

## 📦 Deployment

### Production Deployment with Docker

1. **Configure production environment**
   ```bash
   cp backend/.env.example backend/.env.production
   # Set production values:
   # - Strong SECRET_KEY
   # - Production database credentials
   # - DEBUG=False
   ```

2. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.yml up -d --build
   ```

3. **Setup reverse proxy (nginx)**
   ```nginx
   server {
       listen 80;
       server_name api.obe-system.ac.id;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Setup SSL with Let's Encrypt**
   ```bash
   certbot --nginx -d api.obe-system.ac.id
   ```

### Database Backup

```bash
# Backup
docker exec obe_postgres pg_dump -U obe_user obe_system > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i obe_postgres psql -U obe_user obe_system < backup_20241118.sql
```

---

## 🔧 Development

### Adding New Endpoints

1. **Create model** in `backend/app/models/`
2. **Create schema** in `backend/app/schemas/`
3. **Create API route** in `backend/app/api/`
4. **Register router** in `backend/app/main.py`

**Example:**
```python
# In backend/app/api/my_feature.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_items():
    return {"items": []}

# In backend/app/main.py
from app.api import my_feature
app.include_router(my_feature.router, prefix="/api/v1/my-feature", tags=["My Feature"])
```

### Database Migrations

```bash
# Install alembic
pip install alembic

# Initialize migrations
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migration
alembic upgrade head
```

---

## 📖 Reference Documents

- **System Specification:** `OBE-System-Specification-Document.md`
- **Database Schema:** `OBE-Database-Schema-v3-WITH-KURIKULUM.sql`
- **Implementation Guide:** `Implementation-Guide-Quick-Reference.md`
- **Use Cases:** `Use-Cases-Kurikulum-Management.md`

---

## 🐛 Troubleshooting

### Issue: Cannot connect to database

**Solution:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs obe_postgres

# Verify connection string in .env
DATABASE_URL=postgresql://obe_user:obe_password@postgres:5432/obe_system
```

### Issue: Unauthorized errors

**Solution:**
- Ensure you're sending the token in Authorization header:
  ```
  Authorization: Bearer <your_access_token>
  ```
- Check if token has expired (2 hours expiry)
- Use refresh token to get new access token

### Issue: Student curriculum cannot be changed

**Expected Behavior:**
This is a business rule (BR-K01). Student's curriculum assignment is immutable to maintain data integrity.

---

## 👥 Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Submit pull request

---

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Check existing documentation
- Review API docs at `/docs`

---

## 📝 License

[Your License Here]

---

**Last Updated:** November 18, 2025
**Version:** 3.0.0
**Status:** Development Ready

**Selamat mengembangkan! 🚀**
