from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(String(20), CheckConstraint("user_type IN ('dosen','mahasiswa','admin','kaprodi')"), nullable=False)
    ref_id = Column(String(20))  # id_dosen or nim
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    roles = relationship("UserRole", back_populates="user")


class Role(Base):
    __tablename__ = "roles"

    id_role = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(String)

    # Relationships
    users = relationship("UserRole", back_populates="role")


class UserRole(Base):
    __tablename__ = "user_roles"

    id_user = Column(Integer, ForeignKey("users.id_user"), primary_key=True)
    id_role = Column(Integer, ForeignKey("roles.id_role"), primary_key=True)

    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")
