from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from . import models, schemas, utils, database

router = APIRouter()


def get_db():
    db = database.SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter_by(username=user.username).first()

    if existing:
        raise HTTPException(
            status_code=400, detail="Username already registered"
        )

    hashed_pw = utils.hash_password(user.password)
    new_user = models.User(
        name=user.name, username=user.username, hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = utils.create_access_token(data={"sub": user.username})

    return {"access_token": token}


@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter_by(username=user.username).first()
    verified_user = utils.verify_password(
        user.password, db_user.hashed_password
    )

    if not db_user or not verified_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = utils.create_access_token(data={"sub": user.username})

    return {"access_token": token}
