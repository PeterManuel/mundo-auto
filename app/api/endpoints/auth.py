from datetime import datetime, timedelta
from typing import Annotated, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.crud.user import get_user_by_email, create_user, record_login_history, get_user, update_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token, TokenPayload, PasswordReset, PasswordUpdate, LoginCredentials
from app.schemas.user import UserCreate, UserResponse, GoogleAuthRequest
from app.utils.auth import OAuth2PasswordBearerWithCookie
from app.utils.oauth import GoogleOAuth

router = APIRouter(
    tags=["authentication"],
    responses={401: {"description": "Not authenticated"}},
)
# Allow extracting token from both header and cookies
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user_optional(request: Request, db: Session) -> Optional[User]:
    """
    Extract user from request without raising exception if not authenticated
    """
    auth_header = request.headers.get("Authorization")
    cookie_token = request.cookies.get("access_token")
    
    # No authentication provided
    if not auth_header and not cookie_token:
        return None
        
    # Extract token from header or cookie
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
    elif cookie_token and cookie_token.startswith("Bearer "):
        token = cookie_token.replace("Bearer ", "")
        
    if not token:
        return None
        
    try:
        # Decode token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            return None
            
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except JWTError:
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Validates the access token and returns the current user.
    This only requires the access token, not username/password or any client_id.
    The token can be provided via the Authorization header (Bearer token) or as a cookie.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenPayload(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login endpoint supporting OAuth2 password flow.
    Expects form data with username and password fields.
    """
    print(f"Raw form data received: {form_data}")
    username = form_data.username
    password = form_data.password
    
    print(f"Login attempt with username: {username}, password_length: {len(password)}")
    
    user = get_user_by_email(db, email=username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # Record login with IP and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    record_login_history(db, user.id, ip_address, user_agent)
    
    # Set token in cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login-json", response_model=Token)
async def login_json(
    response: Response,
    request: Request,
    login_data: LoginCredentials,
    db: Session = Depends(get_db),
):
    """
    Alternative login endpoint that accepts JSON data
    """
    print(f"JSON login attempt with data: {login_data}")
    
    user = get_user_by_email(db, email=login_data.username)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # Record login with IP and user agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    record_login_history(db, user.id, ip_address, user_agent)
    
    # Set token in cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    db_user = create_user(db, user)
    
    return db_user


@router.post("/logout")
def logout(response: Response):
    """
    Logout user by clearing the cookie
    """
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}


@router.post("/password-recovery")
def recover_password(password_reset: PasswordReset, db: Session = Depends(get_db)):
    """
    Password Recovery - sends an email with reset token
    """
    user = get_user_by_email(db, email=password_reset.email)
    if not user:
        # Don't reveal that email doesn't exist
        return {"message": "If the email exists, a password recovery link has been sent"}
    
    # In a real implementation, we would:
    # 1. Generate a password reset token
    # 2. Store it with an expiration time
    # 3. Send an email with a link including the token
    
    # For now, we'll just return a success message
    return {"message": "If the email exists, a password recovery link has been sent"}


@router.post("/reset-password")
def reset_password(password_update: PasswordUpdate, db: Session = Depends(get_db)):
    """
    Reset password using token from email
    """
    # In a real implementation, we would:
    # 1. Verify the token is valid and not expired
    # 2. Find the user associated with the token
    # 3. Update their password
    
    # For now, we'll just return a success message
    return {"message": "Password has been reset"}


@router.get("/google/login")
def google_login():
    """
    Redirect the user to Google's OAuth consent screen
    """
    authorization_url = GoogleOAuth.get_authorization_url()
    return RedirectResponse(authorization_url)


@router.get("/google/callback")
def google_callback(
    code: str, 
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Handle the OAuth callback from Google
    """
    try:
        # Exchange code for tokens
        token_data = GoogleOAuth.exchange_code_for_token(code)
        
        # Get user info using access token
        id_token_data = token_data.get("id_token")
        if not id_token_data:
            raise HTTPException(status_code=400, detail="Invalid token data")
        
        user_info = GoogleOAuth.validate_token(id_token_data)
        
        # Check if user with Google ID exists
        email = user_info.get("email")
        google_id = user_info.get("sub")
        
        if not email or not google_id:
            raise HTTPException(
                status_code=400, 
                detail="Could not get email or user ID from Google"
            )
        
        # Check if user exists by Google ID or email
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if not user:
            # Try to find user by email
            user = get_user_by_email(db, email=email)
            
            if user:
                # Update existing user with Google ID
                user.google_id = google_id
                db.commit()
                db.refresh(user)
            else:
                # Create new user
                # Generate a random secure password since the user won't use it
                random_password = uuid.uuid4().hex
                hashed_password = get_password_hash(random_password)
                
                new_user = User(
                    email=email,
                    hashed_password=hashed_password,
                    first_name=user_info.get("given_name"),
                    last_name=user_info.get("family_name"),
                    profile_image=user_info.get("picture"),
                    google_id=google_id,
                    is_active=True
                )
                
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                user = new_user
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        # Record login with IP and user agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        record_login_history(db, user.id, ip_address, user_agent)
        
        # Set cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
        
        # Redirect to frontend with token
        frontend_url = settings.BACKEND_CORS_ORIGINS[0] if settings.BACKEND_CORS_ORIGINS else "http://localhost:3000"
        return RedirectResponse(f"{frontend_url}/auth-success?token={access_token}")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not authenticate with Google: {str(e)}"
        )


@router.post("/google/token", response_model=Token)
def google_token(
    auth_request: GoogleAuthRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Exchange Google authorization code for access token (for mobile/SPA clients)
    """
    try:
        # Exchange code for tokens
        token_data = GoogleOAuth.exchange_code_for_token(auth_request.code)
        
        # Get user info using access token
        id_token_data = token_data.get("id_token")
        if not id_token_data:
            raise HTTPException(status_code=400, detail="Invalid token data")
        
        user_info = GoogleOAuth.validate_token(id_token_data)
        
        # Check if user with Google ID exists
        email = user_info.get("email")
        google_id = user_info.get("sub")
        
        if not email or not google_id:
            raise HTTPException(
                status_code=400, 
                detail="Could not get email or user ID from Google"
            )
        
        # Check if user exists by Google ID or email
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if not user:
            # Try to find user by email
            user = get_user_by_email(db, email=email)
            
            if user:
                # Update existing user with Google ID
                user.google_id = google_id
                db.commit()
                db.refresh(user)
            else:
                # Create new user
                # Generate a random secure password since the user won't use it
                random_password = uuid.uuid4().hex
                hashed_password = get_password_hash(random_password)
                
                new_user = User(
                    email=email,
                    hashed_password=hashed_password,
                    first_name=user_info.get("given_name"),
                    last_name=user_info.get("family_name"),
                    profile_image=user_info.get("picture"),
                    google_id=google_id,
                    is_active=True
                )
                
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                user = new_user
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        # Record login with IP and user agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        record_login_history(db, user.id, ip_address, user_agent)
        
        # Set cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax"
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not authenticate with Google: {str(e)}"
        )


@router.get("/social/facebook-login")
def facebook_login():
    """
    Facebook OAuth login
    """
    # This would redirect to Facebook OAuth
    return {"message": "Facebook login not yet implemented"}