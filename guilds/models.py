from datetime import datetime

from sqlalchemy import Column, BigInteger, Boolean, DateTime
from sqlalchemy.orm import relationship

from core.database import base


class Guild(base):
    __tablename__ = "guilds"

    guild_id = Column(BigInteger, primary_key=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    removed_at = Column(DateTime, default=None)
    is_active = Column(Boolean, default=True)

    punishment_config = relationship("PunishmentConfig", uselist=False, back_populates="guild")
    permissions_config = relationship("PermissionConfig", back_populates="guild")
