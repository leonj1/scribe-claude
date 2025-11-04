from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from typing import Optional
from database import get_db
from repositories.user_repository import MySQLUserRepository
from utils.jwt_utils import create_access_token
from config import settings


router = APIRouter(prefix="/auth", tags=["authentication"])

# Configure OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth2 login flow

    Returns:
        Redirect to Google OAuth consent page
    """
    redirect_uri = settings.REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Google OAuth2 callback

    Args:
        request: Starlette request object
        db: Database session

    Returns:
        Redirect to frontend with JWT token
    """
    try:
        # Get access token from Google
        token = await oauth.google.authorize_access_token(request)

        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )

        google_id = user_info.get('sub')
        email = user_info.get('email')
        display_name = user_info.get('name')
        avatar_url = user_info.get('picture')

        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required user information"
            )

        # Check if user exists, create if not
        user_repo = MySQLUserRepository(db)
        user = user_repo.get_user_by_google_id(google_id)

        if not user:
            # Create new user
            user = user_repo.create_user(
                google_id=google_id,
                email=email,
                display_name=display_name,
                avatar_url=avatar_url
            )
        else:
            # Update existing user info
            user = user_repo.update_user(
                user_id=user.id,
                email=email,
                display_name=display_name,
                avatar_url=avatar_url
            )

        # Create JWT token
        access_token = create_access_token(data={"sub": user.id})

        # Redirect to frontend with token
        frontend_url = f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
        return RedirectResponse(url=frontend_url)

    except Exception as e:
        # Redirect to frontend with error
        error_url = f"{settings.FRONTEND_URL}/auth/error?message={str(e)}"
        return RedirectResponse(url=error_url)
