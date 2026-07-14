from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.models.user import User

# Defines the permitted roles in ascending order of privilege.
ROLE_HIERARCHY = ("viewer", "editor", "admin")


def require_role(minimum_role: str) -> Callable:
    """Return a FastAPI dependency that enforces a minimum role level.

    Roles are ranked by ROLE_HIERARCHY, so require_role("editor") also
    allows "admin" users, but blocks "viewer" users.
    """

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user

        try:
            user_rank = ROLE_HIERARCHY.index(current_user.role)
            required_rank = ROLE_HIERARCHY.index(minimum_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid role configuration",
            )

        if user_rank < required_rank:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this action",
            )

        return current_user

    return dependency