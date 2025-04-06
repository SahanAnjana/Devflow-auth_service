# app/db/seed.py
from app.db.session import SessionLocal
from app.crud.user import create_user, update_user
from app.schemas import UserCreate, UserUpdate

def seed_admin():
    db = SessionLocal()
    try:
        admin_data = UserCreate(
            email="admin@devflow.com",
            password="Admin123"
        )
        user = create_user(db, admin_data)
        
        update_data = UserUpdate(role="admin")
        update_user(db, user.id, update_data)
        print(f"Admin user {user.email} created successfully!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()