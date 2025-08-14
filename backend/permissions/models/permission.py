from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, ARRAY, DateTime

from backend.core.database import Base
from backend.core.helper import get_time_now


class Permission(Base):
    __tablename__ = "permissions"

    command_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id", ondelete="CASCADE"), index=True)
    command_name = Column(String(64), nullable=False)
    command_cooldown = Column(BigInteger, default=5)
    required_role_ids = Column(ARRAY(BigInteger), default=list)
    added_at = Column(DateTime, default=get_time_now())
    is_admin = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=True)
