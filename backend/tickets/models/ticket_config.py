from sqlalchemy import Column, BigInteger, ForeignKey, ARRAY, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from backend.core.database import Base
from backend.core.helper import get_time_now


class TicketConfig(Base):
    __tablename__ = "ticket_config"

    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id", ondelete="CASCADE"), unique=True, primary_key=True)
    panel_embed = Column(JSONB,
                         default=lambda: {
                             "title": "Ticket Panels",
                             "description": "Select to open a ticket"
                         },
                         nullable=True)
    banned_user_ids = Column(ARRAY(BigInteger), default=list)
    banned_role_ids = Column(ARRAY(BigInteger), default=list)
    updated_at = Column(DateTime, default=get_time_now(), onupdate=get_time_now())
    updated_by = Column(BigInteger, nullable=True)
