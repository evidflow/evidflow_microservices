from fastapi import HTTPException, status, Request, Response
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
import logging

logger = logging.getLogger(__name__)

class CookieAuth:
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
        
        # Production cookie settings
        self.access_token_cookie_name = "evid_access_token"
        self.refresh_token_cookie_name = "evid_refresh_token"
        self.cookie_domain = os.getenv("COOKIE_DOMAIN", ".evidflow.com")
        self.cookie_secure = os.getenv("COOKIE_SECURE", "True").lower() == "true"
        self.cookie_httponly = True
        self.cookie_samesite = "lax"
    
    def create_access_token(self, data: dict) -> str:
        """Create access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: dict) -> str:
        """Create refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def get_token_from_cookie(self, request: Request, token_type: str = "access") -> str:
        """Get token from HTTP-only cookie"""
        cookie_name = self.access_token_cookie_name if token_type == "access" else self.refresh_token_cookie_name
        return request.cookies.get(cookie_name)
    
    def set_access_token_cookie(self, response: Response, token: str):
        """Set access token as HTTP-only cookie"""
        response.set_cookie(
            key=self.access_token_cookie_name,
            value=token,
            httponly=self.cookie_httponly,
            secure=self.cookie_secure,
            samesite=self.cookie_samesite,
            max_age=self.access_token_expire_minutes * 60,
            domain=self.cookie_domain,
            path="/"
        )
    
    def set_refresh_token_cookie(self, response: Response, token: str):
        """Set refresh token as HTTP-only cookie"""
        response.set_cookie(
            key=self.refresh_token_cookie_name,
            value=token,
            httponly=self.cookie_httponly,
            secure=self.cookie_secure,
            samesite=self.cookie_samesite,
            max_age=7 * 24 * 60 * 60,
            domain=self.cookie_domain,
            path="/"
        )
    
    def clear_token_cookies(self, response: Response):
        """Clear authentication cookies"""
        response.delete_cookie(self.access_token_cookie_name, domain=self.cookie_domain, path="/")
        response.delete_cookie(self.refresh_token_cookie_name, domain=self.cookie_domain, path="/")
    
    async def get_current_user(
        self,
        request: Request,
        session: AsyncSession
    ):
        """Get current user from HTTP-only cookie"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        # Get token from cookie
        token = self.get_token_from_cookie(request)
        if not token:
            raise credentials_exception
        
        # Verify token
        payload = self.verify_token(token)
        if not payload or payload.get("type") != "access":
            raise credentials_exception
        
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # Get user from database
        from app.models import User
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        return user

# Create global instance
cookie_auth = CookieAuth()
