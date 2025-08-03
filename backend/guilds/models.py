from sqlalchemy import Column, BigInteger, Boolean, DateTime
from sqlalchemy.orm import relationship

from backend.core.database import Base
from backend.core.helper import get_utc_now


class Guild(Base):
    __tablename__ = "guilds"

    guild_id = Column(BigInteger, primary_key=True)
    added_at = Column(DateTime, default=get_utc_now())
    removed_at = Column(DateTime, default=None)
    is_active = Column(Boolean, default=True)

    config = relationship("Config", uselist=False, back_populates="guild")
    permission = relationship("Permission", back_populates="guild")
