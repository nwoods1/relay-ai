from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def seed_users():
    db = SessionLocal()

    try:
        users = [
            {
                "username": "sales",
                "email": "sales@relay.local",
                "password": "Sales123!",
                "role": "sales_rep",
            },
            {
                "username": "manager",
                "email": "manager@relay.local",
                "password": "Manager123!",
                "role": "manager",
            },
            {
                "username": "admin",
                "email": "admin@relay.local",
                "password": "Admin123!",
                "role": "admin",
            },
        ]

        for user_data in users:
            existing_user = (
                db.query(User)
                .filter(
                    User.username
                    == user_data["username"]
                )
                .first()
            )

            if existing_user:
                continue

            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hash_password(
                    user_data["password"]
                ),
                role=user_data["role"],
            )

            db.add(user)

        db.commit()

        print(
            "Development users seeded."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_users()