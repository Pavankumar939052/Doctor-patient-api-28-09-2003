from getpass import getpass

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def create_admin():
    db = SessionLocal()

    try:
        email = input("Admin email: ").strip()
        password = getpass("Admin password: ")

        existing_user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if existing_user:
            print("A user with this email already exists.")
            return

        admin = User(
            email=email,
            hashed_password=hash_password(password),
            role="admin"
        )

        db.add(admin)
        db.commit()

        print("Admin created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()