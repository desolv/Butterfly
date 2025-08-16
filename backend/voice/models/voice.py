from sqlalchemy import Column, BigInteger, ForeignKey, ARRAY, Boolean, DateTime

from backend.core.database import Base
from backend.core.helper import get_time_now


class Voice(Base):
    __tablename__ = "voices"

    channel_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id"), index=True)
    owner_id = Column(BigInteger, nullable=False, index=True)
    allowed_user_ids = Column(ARRAY(BigInteger), default=list)
    is_temporary = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=get_time_now())
    is_deleted = Column(Boolean, default=False, index=True)
