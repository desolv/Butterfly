from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

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
    from structure.repo.models.relay_model import Relay
    base.metadata.create_all(engine)