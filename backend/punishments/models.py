from sqlalchemy import Column, BigInteger, JSON, ForeignKey
from sqlalchemy.orm import relationship

from backend.core.database import base


class PunishmentConfig(base):
    __tablename__ = "punishment_configs"

    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id"), primary_key=True)
    muted_role = Column(BigInteger, default=None)
    exempt_roles = Column(JSON, default=list)
    exempt_users = Column(JSON, default=list)
    moderation_channel = Column(BigInteger, default=None)

    guild = relationship("Guild", back_populates="punishment_config")
