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
    max_overflow=5,
    echo=os.getenv("DEBUG") == "True"
)

base = declarative_base()

def init_tables():
    from structure.repo.models.tracking_model import Track
    from structure.repo.models.punishment_model import Punishment
    base.metadata.create_all(engine)