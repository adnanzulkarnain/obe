# OBE System Backend API

Backend API untuk Sistem Informasi Kurikulum OBE (Outcome-Based Education).

## 🏗️ Arsitektur

Project ini menggunakan **Clean Architecture** dengan layer separation:

```
backend/
├── app/
│   ├── core/                   # Configuration & Security
│   ├── domain/                 # Business Entities & Rules
│   ├── infrastructure/         # Database & External Services
│   ├── application/            # Business Logic Services
│   └── presentation/           # API Endpoints & Schemas
└── tests/                      # Unit & Integration Tests
```

### Prinsip Clean Code yang Diterapkan

1. **Single Responsibility Principle**: Setiap class/function punya satu tanggung jawab
2. **Dependency Inversion**: High-level modules tidak bergantung pada low-level modules
3. **Clear Naming**: Nama variabel/function yang deskriptif dan bermakna
4. **Type Hints**: Penggunaan Python type hints untuk type safety
5. **DRY (Don't Repeat Yourself)**: Tidak ada duplikasi kode
6. **Small Functions**: Function pendek dan fokus
7. **Error Handling**: Exception handling yang explicit dan informative
8. **Documentation**: Docstrings yang jelas untuk semua public functions/classes

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip atau poetry

### Installation

1. Clone repository:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup environment variables:
```bash
cp .env.example .env
# Edit .env dengan konfigurasi Anda
```

5. Setup database:
```bash
# Create database
createdb obe_system

# Run schema
psql -d obe_system -f ../OBE-Database-Schema-v3-WITH-KURIKULUM.sql
```

### Running the Application

Development mode with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Production mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Setelah aplikasi berjalan, akses dokumentasi:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📚 Tech Stack

- **Framework**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL 14+
- **Authentication**: JWT (python-jose)
- **Validation**: Pydantic 2.0+
- **Testing**: Pytest
- **Code Quality**: Black, Flake8, Mypy

## 🧪 Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_kurikulum.py -v
```

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- Input validation (Pydantic)

## 📖 API Endpoints (Planned)

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/profile` - Get current user profile

### Kurikulum Management
- `GET /api/v1/kurikulum` - List all curricula
- `POST /api/v1/kurikulum` - Create new curriculum
- `GET /api/v1/kurikulum/{id}` - Get curriculum detail
- `PUT /api/v1/kurikulum/{id}` - Update curriculum
- `POST /api/v1/kurikulum/{id}/activate` - Activate curriculum
- `GET /api/v1/kurikulum/compare` - Compare curricula

### CPL Management
- `GET /api/v1/kurikulum/{id}/cpl` - List CPL for curriculum
- `POST /api/v1/kurikulum/{id}/cpl` - Create CPL
- `PUT /api/v1/cpl/{id}` - Update CPL
- `DELETE /api/v1/cpl/{id}` - Deactivate CPL

### Mata Kuliah Management
- `GET /api/v1/kurikulum/{id}/matakuliah` - List courses
- `POST /api/v1/kurikulum/{id}/matakuliah` - Create course
- `PUT /api/v1/matakuliah/{code}/{curriculum_id}` - Update course

## 🏃 Development

### Code Style

Format code with Black:
```bash
black app/
```

Lint code:
```bash
flake8 app/
```

Type checking:
```bash
mypy app/
```

### Database Migrations

Using Alembic (upcoming):
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📝 Business Rules Enforced

| Rule ID | Description | Implementation |
|---------|-------------|----------------|
| BR-K01 | Student curriculum is immutable | SQLAlchemy event listener |
| BR-K02 | Same MK code can exist in different curricula | Composite primary key |
| BR-K03 | MK cannot be hard deleted | SQLAlchemy before_delete event |
| BR-K04 | Student can only enroll in their curriculum | Validation in service layer |
| BR-K05 | Support multiple parallel curricula | Database design |
| BR-K06 | MK mapping between curricula | PemetaanMKKurikulum table |
| BR-K07 | CPL belongs to curriculum | Foreign key to kurikulum |

## 🤝 Contributing

1. Follow Clean Code principles
2. Write unit tests for new features
3. Update documentation
4. Format code with Black
5. Ensure all tests pass

## 📄 License

Copyright © 2025 OBE System Development Team
