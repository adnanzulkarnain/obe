"""
Authentication API Endpoints

Handles user authentication and registration.
Following Clean Code: RESTful design, Clear error handling.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_database_session
from app.application.services.auth_service import AuthenticationService
from app.presentation.schemas.user_schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordChange
)
from app.presentation.schemas.base_schemas import SuccessResponse, StatusResponse
from app.presentation.dependencies import (
    get_auth_service,
    get_current_active_user
)
from app.infrastructure.models.user_models import User
from app.domain.exceptions import DomainException


router = APIRouter()


@router.post(
    "/register",
    response_model=SuccessResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with username, email, and password."
)
def register_user(
    user_data: UserCreate,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Register a new user.

    - **username**: Unique username (alphanumeric, 3-50 characters)
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars, uppercase, lowercase, number)
    - **user_type**: Type of user (dosen, mahasiswa, admin, kaprodi)
    - **ref_id**: Reference ID (id_dosen or nim)

    Returns created user information (password excluded).
    """
    user = auth_service.register_user(user_data)

    return SuccessResponse(
        success=True,
        message="Registrasi berhasil",
        data=UserResponse.from_orm_with_roles(user)
    )


@router.post(
    "/login",
    response_model=SuccessResponse[TokenResponse],
    summary="User login",
    description="Authenticate user with username/email and password, returns JWT tokens."
)
def login(
    login_data: LoginRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Authenticate user and generate tokens.

    - **username_or_email**: Username or email address
    - **password**: User password

    Returns:
    - **access_token**: JWT access token (expires in 2 hours)
    - **refresh_token**: JWT refresh token (expires in 7 days)
    - **token_type**: "bearer"
    - **expires_in**: Token expiration time in seconds
    """
    # Authenticate user
    user = auth_service.authenticate_user(login_data)

    # Generate tokens
    tokens = auth_service.generate_tokens(user)

    return SuccessResponse(
        success=True,
        message="Login berhasil",
        data=tokens
    )


@router.post(
    "/refresh",
    response_model=SuccessResponse[TokenResponse],
    summary="Refresh access token",
    description="Get new access token using refresh token."
)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Refresh access token.

    Use this endpoint when your access token expires.
    Provide your refresh token to get a new access token.

    - **refresh_token**: Valid refresh token

    Returns new access and refresh tokens.
    """
    tokens = auth_service.refresh_access_token(refresh_data.refresh_token)

    return SuccessResponse(
        success=True,
        message="Token berhasil diperbarui",
        data=tokens
    )


@router.get(
    "/profile",
    response_model=SuccessResponse[UserResponse],
    summary="Get current user profile",
    description="Get authenticated user's profile information."
)
def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile.

    Requires authentication (Bearer token in Authorization header).

    Returns user information including roles.
    """
    return SuccessResponse(
        success=True,
        message="Profil berhasil diambil",
        data=UserResponse.from_orm_with_roles(current_user)
    )


@router.post(
    "/change-password",
    response_model=StatusResponse,
    summary="Change password",
    description="Change authenticated user's password."
)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthenticationService = Depends(get_auth_service)
):
    """
    Change user password.

    Requires authentication.

    - **old_password**: Current password
    - **new_password**: New password (min 8 chars, strong password rules)

    Returns success status.
    """
    auth_service.change_password(
        user=current_user,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )

    return StatusResponse(
        success=True,
        message="Password berhasil diubah"
    )


@router.post(
    "/logout",
    response_model=StatusResponse,
    summary="Logout (client-side only)",
    description="Logout endpoint (client should discard tokens)."
)
def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout user.

    Note: With JWT tokens, logout is handled client-side by discarding the tokens.
    This endpoint is provided for consistency and can be extended with token
    blacklisting if needed.

    Returns success status.
    """
    return StatusResponse(
        success=True,
        message="Logout berhasil. Silakan hapus token dari client."
    )
