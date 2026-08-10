"""Standalone script to seed demo data into ProjectForge AI database."""
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.core.database import SessionLocal, init_db
from backend.app.models.user import User
from backend.app.core.security import hash_password
from backend.app.services.demo_data import create_demo_project


def main():
    print("Initializing database...")
    init_db()

    db = SessionLocal()
    try:
        # Create or get demo user
        user = db.query(User).filter_by(username="demo").first()
        if not user:
            print("Creating demo user (demo / demo123)...")
            user = User(
                username="demo",
                email="demo@projectforge.ai",
                password_hash=hash_password("demo123"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        print("Seeding demo project...")
        proj = create_demo_project(db, user.id)
        print(f"[OK] Demo project created: '{proj.name}' (ID: {proj.id})")
        print("You can now login as 'demo' / 'demo123' and test technology selection.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
