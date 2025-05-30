import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.utils import read_bool_from_os_env

DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "postgresql")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME", "")
SQLALCHELMY_ECHO = read_bool_from_os_env("SQLALCHELMY_ECHO", 0)

if DB_USER and DB_PASSWORD and DB_HOST and DB_NAME:
    DATABASE_URL = (
        f"{DATABASE_PREFIX}://"
        f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
elif DB_USER and DB_HOST and DB_NAME:
    DATABASE_URL = (
        f"{DATABASE_PREFIX}://"
        f"{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
else:
    DATABASE_URL = "sqlite:///./dev.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=SQLALCHELMY_ECHO
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
