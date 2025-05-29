from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import database, models, utils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_db():
    db = database.SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials"
    )

    try:
        payload = jwt.decode(
            token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM]
        )
        username = payload.get("sub")

        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter_by(username=username).first()

    if user is None:
        raise credentials_exception

    return user
