"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from config.database import get_db
from config.settings import settings
from config.security import get_password_hash
from models.models import User

# CREATE ROUTER (THIS WAS MISSING!)
router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """User login endpoint"""
    
    # Authenticate user
    user = db.query(User).filter(User.username == username).first()
    
    if not user or not pwd_context.verify(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account deactivated"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create token
    access_token = create_access_token({"sub": user.username, "role": user.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active
        }
    }


@router.post("/logout")
async def logout():
    """User logout endpoint"""
    return {"message": "Logged out successfully"}


@router.get("/fix-admin")
def fix_admin_password(db: Session = Depends(get_db)):
    """Temporary route to force-reset the admin password hash"""
    user = db.query(User).filter(User.username == "admin").first()
    if user:
        # Use the backend's own hasher to create the hash for 'admin123'
        user.password_hash = get_password_hash("admin123")
        user.is_active = True
        db.commit()
        return {"success": True, "message": "Admin password successfully reset to admin123!"}
    
    return {"success": False, "message": "Admin user not found in database."}
