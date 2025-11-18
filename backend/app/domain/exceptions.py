"""
Domain Exceptions

Custom exceptions for business logic errors.
Following Clean Code: Meaningful names, Clear error messages.
"""


class DomainException(Exception):
    """Base exception for all domain-level errors."""

    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


class EntityNotFoundException(DomainException):
    """Raised when an entity cannot be found."""

    def __init__(self, entity_name: str, entity_id: str):
        message = f"{entity_name} dengan ID '{entity_id}' tidak ditemukan"
        super().__init__(message, "ENTITY_NOT_FOUND")


class DuplicateEntityException(DomainException):
    """Raised when trying to create a duplicate entity."""

    def __init__(self, entity_name: str, field: str, value: str):
        message = f"{entity_name} dengan {field} '{value}' sudah ada"
        super().__init__(message, "DUPLICATE_ENTITY")


class InvalidOperationException(DomainException):
    """Raised when an operation violates business rules."""

    def __init__(self, message: str):
        super().__init__(message, "INVALID_OPERATION")


class AuthenticationException(DomainException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Autentikasi gagal"):
        super().__init__(message, "AUTHENTICATION_FAILED")


class AuthorizationException(DomainException):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Anda tidak memiliki akses"):
        super().__init__(message, "AUTHORIZATION_FAILED")


class ValidationException(DomainException):
    """Raised when data validation fails."""

    def __init__(self, field: str, message: str):
        full_message = f"Validasi gagal pada field '{field}': {message}"
        super().__init__(full_message, "VALIDATION_ERROR")


class CurriculumImmutableException(InvalidOperationException):
    """Raised when trying to modify immutable curriculum assignment."""

    def __init__(self):
        super().__init__(
            "Kurikulum mahasiswa tidak dapat diubah (IMMUTABLE). "
            "Ini adalah business rule BR-K01."
        )


class EnrollmentCurriculumMismatchException(InvalidOperationException):
    """Raised when student tries to enroll in wrong curriculum."""

    def __init__(self, student_curriculum: str, class_curriculum: str):
        super().__init__(
            f"Mahasiswa hanya dapat mengambil kelas dari kurikulumnya. "
            f"Kurikulum mahasiswa: {student_curriculum}, "
            f"Kurikulum kelas: {class_curriculum}. "
            f"Ini adalah business rule BR-K04."
        )


# Aliases for convenience
NotFoundException = EntityNotFoundException
DuplicateException = DuplicateEntityException
