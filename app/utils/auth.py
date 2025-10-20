from typing import Dict, Optional, Union
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param


class OAuth2PasswordBearerWithCookie(HTTPBearer):
    """
    HTTP Bearer authentication scheme that can extract token from cookies or authorization header.
    This is a simplified version that only requires the bearer token, with no OAuth2 parameters.
    """
    
    def __init__(
        self,
        tokenUrl: str = None,  # Not used, but kept for backward compatibility
        auto_error: bool = True,
    ):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        # Check for Authorization header first
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if not authorization or scheme.lower() != "bearer":
            # If not found, check for access token cookie
            token = request.cookies.get("access_token")
            if not token:
                if self.auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authenticated",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                else:
                    return None
            return token
        
        return param