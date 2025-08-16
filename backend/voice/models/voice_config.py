from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, ARRAY, Integer
from sqlalchemy.dialects.postgresql import JSONB

from backend.core.database import Base
from backend.core.helper import get_time_now


class VoiceConfig(Base):
    __tablename__ = "voice_configs"

    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(BigInteger, nullable=True)
    join_channel_id = Column(BigInteger, nullable=True)
    command_channel_id = Column(BigInteger, nullable=True)
    embed = Column(JSONB,
                   default=lambda: {
                       "title": "Voice Channel Menu",
                       "description": "No description",
                   },
                   nullable=True)
    auto_delete_after = Column(Integer, default=15)
    staff_role_ids = Column(ARRAY(BigInteger), default=list)
    logging_channel_id = Column(BigInteger, nullable=True)
    updated_at = Column(DateTime, default=get_time_now(), onupdate=get_time_now())
    updated_by = Column(BigInteger, nullable=True)
