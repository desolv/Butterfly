from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, Boolean, String

from backend.core.database import Base
from backend.core.helper import get_utc_now


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id"), index=True)
    panel_id = Column(String(64), nullable=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    channel_id = Column(BigInteger, nullable=False, unique=True)
    created_at = Column(DateTime, default=get_utc_now())
    closed_at = Column(DateTime, nullable=True)
    closed_by = Column(BigInteger, nullable=True, index=True)
    updated_at = Column(DateTime, default=get_utc_now(), onupdate=get_utc_now())
    is_closed = Column(Boolean, default=False, index=True)
