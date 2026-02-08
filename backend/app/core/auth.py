"""
Authentication utilities for admin access control.

Provides session-based authentication with HTTP-only cookies for admin users.
"""

from fastapi import Cookie, HTTPException, status
from typing import Optional
import secrets

SESSION_COOKIE_NAME = "metacheck_admin_session"
SESSION_EXPIRY_HOURS = 24

# In-memory session store (token -> username)
# Note: Sessions reset on server restart
active_sessions = {}


def create_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)


async def require_admin(
    session: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME)
) -> None:
    """
    FastAPI dependency that verifies admin session.

    Raises HTTPException with 403 status if session is invalid or missing.
    """
    if not session or session not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def verify_credentials(username: str, password: str) -> bool:
    """
    Verify admin credentials against environment variables.

    Args:
        username: Username to verify
        password: Password to verify

    Returns:
        True if credentials match environment settings, False otherwise
    """
    from app.core.settings import get_settings

    settings = get_settings()
    return (
        username == settings.admin_username and
        password == settings.admin_password
    )
