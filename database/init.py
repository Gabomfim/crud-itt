from database.connection import AsyncSessionLocal, User
from services.password_service import hash_password


def init_db() -> None:
    """Initialize database with sample data"""
    db = AsyncSessionLocal()

    # Check if users already exist
    if db.query(User).count() == 0:
        # Create initial users with hashed passwords
        lavinia = User(
            username="lavinia",
            password=hash_password("Lavinia123!"),
            age=16,
            description="Odeio sushi",
        )
        gabriel = User(
            username="gabriel",
            password=hash_password("Gabriel456@"),
            age=26,
            description="Gosto de morango",
        )

        db.add(lavinia)
        db.add(gabriel)
        db.commit()
        print("Database initialized with sample users")
        print("lavinia password: Lavinia123!")
        print("gabriel password: Gabriel456@")

    db.close()


if __name__ == "__main__":
    init_db()
