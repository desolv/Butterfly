from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from backend.core.database import base


class PermissionConfig(base):
    __tablename__ = "permissions_configs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id"))
    command_name = Column(String(64), nullable=False)
    allowed_roles = Column(JSON, default=list)
    blocked_users = Column(JSON, default=list)
    is_enabled = Column(Boolean, default=True)

    guild = relationship("Guild", back_populates="permissions_config")
