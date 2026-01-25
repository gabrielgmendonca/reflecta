from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.config import settings
from app.database import get_db
from app.services.auth_service import AuthService

router = APIRouter()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    picture: str | None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


@router.get("/login")
async def login(request: Request):
    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")

    user_info = token.get("userinfo")
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info")

    auth_service = AuthService(db)
    user = await auth_service.get_or_create_user(
        google_id=user_info["sub"],
        email=user_info["email"],
        name=user_info.get("name", user_info["email"]),
        picture=user_info.get("picture"),
    )

    access_token = AuthService.create_access_token(user.id)

    # Redirect to frontend with token
    redirect_url = f"{settings.frontend_url}/auth/callback?token={access_token}"
    return RedirectResponse(url=redirect_url)


@router.get("/me", response_model=UserResponse)
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ")[1]
    user_id = AuthService.verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
