from datetime import datetime, timedelta
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import User


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_user(self, google_id: str, email: str, name: str, picture: str | None = None) -> User:
        stmt = select(User).where(User.google_id == google_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            user.last_login = datetime.utcnow()
            user.name = name
            user.picture = picture
            await self.db.commit()
            return user

        user = User(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def create_access_token(user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
        }
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    def verify_token(token: str) -> int | None:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id = payload.get("sub")
            if user_id is None:
                return None
            return int(user_id)
        except JWTError:
            return None
