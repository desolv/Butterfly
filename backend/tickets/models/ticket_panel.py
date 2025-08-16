from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, String, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from backend.core.database import Base
from backend.core.helper import get_time_now


class TicketPanel(Base):
    __tablename__ = "ticket_panel"

    panel_id = Column(String, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id", ondelete="CASCADE"), index=True, nullable=False)
    panel_embed = Column(JSONB,
                         default=lambda: {
                             "name": None,
                             "description": "No description",
                             "emoji": "💬",
                             "author_url": False
                         },
                         nullable=True)
    category_id = Column(BigInteger, nullable=True)
    staff_role_ids = Column(ARRAY(BigInteger), default=list)
    mention_role_ids = Column(ARRAY(BigInteger), default=list)
    required_role_ids = Column(ARRAY(BigInteger), default=list)
    ticket_embed = Column(JSONB,
                          default=lambda: {
                              "title": "Ticket support",
                              "description": "Support will be with you shortly"
                          },
                          nullable=True)
    logging_channel_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=get_time_now())
    updated_at = Column(DateTime, default=get_time_now(), onupdate=get_time_now())
    updated_by = Column(BigInteger, nullable=True)
    is_enabled = Column(Boolean, default=True)
