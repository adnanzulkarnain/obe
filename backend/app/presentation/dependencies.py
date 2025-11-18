"""
FastAPI Dependencies

Dependency injection functions for API endpoints.
Following Clean Code: Dependency Inversion, Reusability.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.infrastructure.database import get_database_session
from app.infrastructure.models.user_models import User
from app.application.services.auth_service import AuthenticationService
from app.application.services.user_service import UserService
from app.application.services.kurikulum_service import KurikulumService
from app.application.services.cpl_service import CPLService
from app.application.services.matakuliah_service import MataKuliahService


# Security scheme for JWT Bearer token
security = HTTPBearer(
    scheme_name="Bearer Authentication",
    description="Enter your JWT access token"
)


# =============================================================================
# SERVICE DEPENDENCIES
# =============================================================================

def get_auth_service(session: Session = Depends(get_database_session)) -> AuthenticationService:
    """
    Get AuthenticationService instance.

    Args:
        session: Database session (injected)

    Returns:
        AuthenticationService: Service instance
    """
    return AuthenticationService(session)


def get_user_service(session: Session = Depends(get_database_session)) -> UserService:
    """
    Get UserService instance.

    Args:
        session: Database session (injected)

    Returns:
        UserService: Service instance
    """
    return UserService(session)


def get_kurikulum_service(session: Session = Depends(get_database_session)) -> KurikulumService:
    """
    Get KurikulumService instance.

    Args:
        session: Database session (injected)

    Returns:
        KurikulumService: Service instance
    """
    return KurikulumService(session)


def get_cpl_service(session: Session = Depends(get_database_session)) -> CPLService:
    """
    Get CPLService instance.

    Args:
        session: Database session (injected)

    Returns:
        CPLService: Service instance
    """
    return CPLService(session)


def get_matakuliah_service(session: Session = Depends(get_database_session)) -> MataKuliahService:
    """
    Get MataKuliahService instance.

    Args:
        session: Database session (injected)

    Returns:
        MataKuliahService: Service instance
    """
    return MataKuliahService(session)


# =============================================================================
# AUTHENTICATION DEPENDENCIES
# =============================================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> User:
    """
    Get current authenticated user from JWT token.

    This is the main dependency for protecting endpoints.
    Use it to require authentication: user: User = Depends(get_current_user)

    Args:
        credentials: HTTP Authorization credentials (Bearer token)
        auth_service: Authentication service (injected)

    Returns:
        User: Authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # Validate token and get user
    user = auth_service.validate_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.

    Additional check to ensure user account is active.

    Args:
        current_user: Current user (injected from get_current_user)

    Returns:
        User: Active user

    Raises:
        HTTPException: If user account is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akun tidak aktif"
        )

    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    auth_service: AuthenticationService = Depends(get_auth_service)
) -> Optional[User]:
    """
    Get current user if token is provided, None otherwise.

    Use this for endpoints that work both with and without authentication.

    Args:
        credentials: HTTP Authorization credentials (optional)
        auth_service: Authentication service (injected)

    Returns:
        Optional[User]: User if authenticated, None otherwise
    """
    if not credentials:
        return None

    token = credentials.credentials
    return auth_service.validate_token(token)


# =============================================================================
# ROLE-BASED ACCESS CONTROL DEPENDENCIES
# =============================================================================

class RequireRole:
    """
    Dependency class for role-based access control.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(RequireRole("admin"))])
    """

    def __init__(self, *required_roles: str):
        """
        Initialize role requirement.

        Args:
            *required_roles: One or more required role names
        """
        self.required_roles = required_roles

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        """
        Check if user has required role.

        Args:
            current_user: Current authenticated user

        Returns:
            User: User if has required role

        Raises:
            HTTPException: If user doesn't have required role
        """
        user_roles = [ur.role.role_name for ur in current_user.roles]

        has_role = any(role in user_roles for role in self.required_roles)

        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Memerlukan salah satu role: {', '.join(self.required_roles)}"
            )

        return current_user


# Convenience dependencies for common roles
require_admin = RequireRole("admin")
require_kaprodi = RequireRole("kaprodi", "admin")
require_dosen = RequireRole("dosen", "kaprodi", "admin")


# =============================================================================
# USER TYPE DEPENDENCIES
# =============================================================================

def require_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Require user to be admin.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Admin user

    Raises:
        HTTPException: If user is not admin
    """
    from app.infrastructure.models.user_models import UserType

    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya admin yang dapat mengakses endpoint ini"
        )

    return current_user


def require_kaprodi_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Require user to be kaprodi or admin.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Kaprodi or admin user

    Raises:
        HTTPException: If user is not kaprodi or admin
    """
    from app.infrastructure.models.user_models import UserType

    if current_user.user_type not in [UserType.KAPRODI, UserType.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya kaprodi atau admin yang dapat mengakses endpoint ini"
        )

    return current_user


def require_dosen_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Require user to be dosen, kaprodi, or admin.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Dosen, kaprodi, or admin user

    Raises:
        HTTPException: If user is not dosen, kaprodi, or admin
    """
    from app.infrastructure.models.user_models import UserType

    if current_user.user_type not in [UserType.DOSEN, UserType.KAPRODI, UserType.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hanya dosen, kaprodi, atau admin yang dapat mengakses endpoint ini"
        )

    return current_user
