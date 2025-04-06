# app/crud/token.py
import uuid
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.db.models.user import RefreshToken
from app.core.config import settings

def create_refresh_token(db: Session, user_id: str) -> RefreshToken:
    # Set expiration time for refresh token (e.g., 7 days)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Create a unique token
    token = str(uuid.uuid4())
    
    db_token = RefreshToken(
        id=str(uuid.uuid4()),
        token=token,
        user_id=user_id,
        expires_at=expires_at,
        created_at=datetime.utcnow(),
        is_revoked=False
    )
    
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    return (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == token,
            RefreshToken.expires_at > datetime.utcnow(),
            RefreshToken.is_revoked == False
        )
        .first()
    )

def invalidate_refresh_token(db: Session, token: str) -> bool:
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if not db_token:
        return False
    
    db_token.is_revoked = True
    db.commit()
    return True

def delete_expired_tokens(db: Session) -> int:
    """Delete all expired tokens from database"""
    expired_tokens = (
        db.query(RefreshToken)
        .filter(
            (RefreshToken.expires_at < datetime.utcnow()) | 
            (RefreshToken.is_revoked == True)
        )
        .delete()
    )
    db.commit()
    return expired_tokens