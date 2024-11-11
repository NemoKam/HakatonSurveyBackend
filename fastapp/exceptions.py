from typing import Any

from fastapi import HTTPException, status


class AuthFailedException(HTTPException):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail if detail else "Authenticate failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


class BadRequestException(HTTPException):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail if detail else "Bad request",
        )


class NotFoundException(HTTPException):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail if detail else "Not found",
        )

class NotAllowedException(HTTPException):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=detail if detail else "Not allowed",
        )


class CodeMoreThanExisting(Exception):
    pass

class UnAvailable(Exception):
    pass