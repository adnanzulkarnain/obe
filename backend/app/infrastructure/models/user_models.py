"""
User Authentication and Authorization Models

SQLAlchemy models for user management, roles, and permissions.
Following Clean Code: Clear naming, Single Responsibility, Type hints.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from app.infrastructure.database import Base


class UserType(str, enum.Enum):
    """Enumeration for user types."""

    DOSEN = "dosen"
    MAHASISWA = "mahasiswa"
    ADMIN = "admin"
    KAPRODI = "kaprodi"


class User(Base):
    """
    User authentication model.

    Represents system users with authentication credentials.
    Links to specific roles (Dosen, Mahasiswa, etc.) via ref_id.
    """

    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(SQLEnum(UserType), nullable=False)
    ref_id = Column(String(20))  # References id_dosen or nim
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(username='{self.username}', type='{self.user_type}')>"

    def has_role(self, role_name: str) -> bool:
        """
        Check if user has a specific role.

        Args:
            role_name: Name of the role to check

        Returns:
            bool: True if user has the role, False otherwise
        """
        return any(user_role.role.role_name == role_name for user_role in self.roles)


class Role(Base):
    """
    Role model for authorization.

    Defines different roles in the system (admin, kaprodi, dosen, etc.).
    """

    __tablename__ = "roles"

    id_role = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user_roles = relationship("UserRole", back_populates="role")

    def __repr__(self) -> str:
        return f"<Role(name='{self.role_name}')>"


class UserRole(Base):
    """
    Many-to-many relationship between Users and Roles.

    A user can have multiple roles, and a role can be assigned to multiple users.
    """

    __tablename__ = "user_roles"

    id_user = Column(
        Integer,
        ForeignKey("users.id_user", ondelete="CASCADE"),
        primary_key=True
    )
    id_role = Column(
        Integer,
        ForeignKey("roles.id_role", ondelete="CASCADE"),
        primary_key=True
    )
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.id_user}, role_id={self.id_role})>"
