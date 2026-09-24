class DomainError(Exception):
    """Base class for expected domain errors."""


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class DomainValidationError(DomainError):
    pass
