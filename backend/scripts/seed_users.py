from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def require_seed_password(
    name: str,
    value: str | None,
) -> str:
    if not value:
        raise RuntimeError(
            f"Set {name} in .env "
            "before seeding users"
        )

    return value


def seed_users():
    users = [
        {
            "username": "sales",
            "email": "sales@relay.local",
            "password": require_seed_password(
                "SEED_SALES_PASSWORD",
                settings.seed_sales_password,
            ),
            "role": "sales_rep",
        },
        {
            "username": "manager",
            "email": "manager@relay.local",
            "password": require_seed_password(
                "SEED_MANAGER_PASSWORD",
                settings.seed_manager_password,
            ),
            "role": "manager",
        },
        {
            "username": "admin",
            "email": "admin@relay.local",
            "password": require_seed_password(
                "SEED_ADMIN_PASSWORD",
                settings.seed_admin_password,
            ),
            "role": "admin",
        },
    ]

    db = SessionLocal()

    try:

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