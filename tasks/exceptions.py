from typing import Optional

class KanbanyBaseException(Exception):
    """Base exception class for Kanbany application"""
    def __init__(self, message: str, code: Optional[str] = None) -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)

class TaskValidationError(KanbanyBaseException):
    """Raised when task validation fails"""
    pass

class WorkerGroupError(KanbanyBaseException):
    """Raised when worker group operations fail"""
    pass

class UserProfileError(KanbanyBaseException):
    """Raised when user profile operations fail"""
    pass

class ResourceNotFoundError(KanbanyBaseException):
    """Raised when a requested resource is not found"""
    pass

class PermissionDeniedError(KanbanyBaseException):
    """Raised when user doesn't have required permissions"""
    pass

class DueDateError(TaskValidationError):
    """Raised when there are issues with task due dates"""
    pass

class MaxMembersExceededError(WorkerGroupError):
    """Raised when attempting to add members beyond the group limit"""
    pass