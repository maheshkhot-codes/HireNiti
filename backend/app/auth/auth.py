from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


def register_user(
    db: Session,
    name: str,
    email: str,
    password: str,
    role: str
):
    from app.database.models import User

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        return None

    hashed_password = hash_password(password)

    user = User(
        name=name,
        email=email,
        password_hash=hashed_password,
        role=role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    from app.database.models import User

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    return user


def generate_token(user):
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }

    return create_access_token(token_data)