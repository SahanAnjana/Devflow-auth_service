# app/crud/role.py
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models.user import Role, UserRole, User

def get_all_roles(db: Session) -> List[Role]:
    return db.query(Role).all()

def get_role_by_id(db: Session, role_id: str) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id).first()

def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    return db.query(Role).filter(Role.name == name).first()

def create_role(db: Session, role_data) -> Role:
    db_role = Role(
        id=str(uuid.uuid4()),
        name=role_data.name,
        description=role_data.description,
        permissions=role_data.permissions,
        created_at=datetime.utcnow()
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, role_id: str, role_data) -> Optional[Role]:
    db_role = get_role_by_id(db, role_id)
    if not db_role:
        return None
    
    update_data = role_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(db_role, key, value)
    
    db_role.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: str) -> bool:
    db_role = get_role_by_id(db, role_id)
    if not db_role:
        return False
    
    db.delete(db_role)
    db.commit()
    return True

def assign_role_to_user(db: Session, user_id: str, role_id: str) -> Optional[User]:
    # Check if user and role exist
    db_user = db.query(User).filter(User.id == user_id).first()
    db_role = db.query(Role).filter(Role.id == role_id).first()
    
    if not db_user or not db_role:
        return None
    
    # Update user's role field directly (simple approach)
    db_user.role = db_role.name
    
    # Alternatively, create a user_role association (for more complex role systems)
    user_role = UserRole(
        user_id=user_id,
        role_id=role_id,
        created_at=datetime.utcnow()
    )
    
    db.add(user_role)
    db.commit()
    db.refresh(db_user)
    return db_user