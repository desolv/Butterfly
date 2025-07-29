import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

load_dotenv(f"io/.env")

engine = create_engine(
    os.getenv("MYSQL"),
    pool_pre_ping=True,
    pool_recycle=280,
    pool_timeout=30,
    pool_size=10,
    max_overflow=5
)

base = declarative_base()


def init_tables():
    # noinspection PyUnresolvedReferences
    from structure.guilds.models import Guild

    # noinspection PyUnresolvedReferences
    from structure.permissions.models import PermissionConfig

    base.metadata.create_all(engine)
