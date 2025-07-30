from sqlalchemy import Column, BigInteger, Boolean, DateTime
from sqlalchemy.orm import relationship

from backend.core.database import base
from backend.core.helper import get_utc_now


class Guild(base):
    __tablename__ = "guilds"

    guild_id = Column(BigInteger, primary_key=True)
    added_at = Column(DateTime, default=get_utc_now())
    removed_at = Column(DateTime, default=None)
    is_active = Column(Boolean, default=True)

    punishment_config = relationship("PunishmentConfig", uselist=False, back_populates="guild")
    permissions_config = relationship("PermissionConfig", back_populates="guild")
