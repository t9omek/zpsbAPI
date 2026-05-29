import os

from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, declarative_base


load_dotenv(find_dotenv())


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or value.strip() == "":
        raise RuntimeError(f"Brak wymaganej zmiennej środowiskowej: {name}")

    return value


DB_USER = get_required_env("DB_USER")
DB_PASSWORD = get_required_env("DB_PASSWORD")
DB_HOST = get_required_env("DB_HOST")
DB_PORT = int(get_required_env("DB_PORT"))
DB_NAME = get_required_env("DB_NAME")
DB_SCHEMA = get_required_env("DB_SCHEMA")


SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    query={
        "options": f"-csearch_path={DB_SCHEMA}",
        "client_encoding": "UTF8"
    }
)


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=False
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()