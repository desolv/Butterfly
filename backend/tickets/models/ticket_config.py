from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from backend.core.database import Base


class TicketConfig(Base):
    __tablename__ = "ticket_config"

    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id", ondelete="CASCADE"), unique=True, primary_key=True)
    panel_embed = Column(JSONB,
                         default=lambda: {
                             "title": "Ticket Panels",
                             "description": "Select to open a ticket"
                         },
                         nullable=True)
