from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, ARRAY, DateTime
from sqlalchemy.orm import relationship

from backend.core.database import Base
from backend.core.helper import get_utc_now


class Permission(Base):
    __tablename__ = "permissions"

    command_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id"), index=True)
    command_name = Column(String(64), nullable=False)
    allowed_roles = Column(ARRAY(BigInteger), default=list)
    added_at = Column(DateTime, default=get_utc_now())
    is_admin = Column(Boolean, default=True)
    is_enabled = Column(Boolean, default=True)

    guild = relationship("Guild", back_populates="permission")
