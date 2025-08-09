import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

load_dotenv(f"io/.env")

Engine = create_engine(
    os.getenv("POSTGRESQL"),
    pool_pre_ping=True,
    pool_recycle=280,
    pool_timeout=30,
    pool_size=10,
    max_overflow=5
)

Base = declarative_base()


def init_tables():
    # noinspection PyUnresolvedReferences
    from backend.guilds.models.guild import Guild

    # noinspection PyUnresolvedReferences
    from backend.permissions.models.permission import Permission

    # noinspection PyUnresolvedReferences
    from backend.punishments.models.punishment import Punishment

    # noinspection PyUnresolvedReferences
    from backend.punishments.models.punishment_config import PunishmentConfig

    # noinspection PyUnresolvedReferences
    from backend.tickets.models.ticket import Ticket

    # noinspection PyUnresolvedReferences
    from backend.tickets.models.ticket_panel import TicketPanel

    Base.metadata.create_all(Engine)
