from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, String, ARRAY, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from backend.core.database import Base
from backend.core.helper import get_utc_now


class TicketPanel(Base):
    __tablename__ = "ticket_panel"

    panel_id = Column(String(64), primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id", ondelete="CASCADE"), index=True, nullable=False)
    panel_name = Column(String(64), nullable=True)
    category_channel_id = Column(BigInteger, nullable=True)
    staff_role_ids = Column(ARRAY(BigInteger), default=list)
    mention_role_ids = Column(ARRAY(BigInteger), default=list)
    panel_embed = Column(JSONB, default=lambda: {"title": None, "description": None}, nullable=True)
    logging_channel_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=get_utc_now())
    updated_at = Column(DateTime, default=get_utc_now(), onupdate=get_utc_now())
    updated_by = Column(BigInteger, nullable=True)
    is_enabled = Column(Boolean, default=True)
