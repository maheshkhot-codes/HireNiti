from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import HTTPBearer

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.security import decode_access_token


security = HTTPBearer()


def get_current_user(
    credentials=Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:

        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if not user_id:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        from app.database.models import User

        user = (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )

        if not user:

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def require_role(required_role: str):

    def role_checker(
        current_user=Depends(
            get_current_user
        )
    ):

        if current_user.role != required_role:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"{required_role} role required"
                )
            )

        return current_user

    return role_checker