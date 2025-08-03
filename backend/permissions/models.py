from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

from backend.core.database import Base


class Permission(Base):
    __tablename__ = "permissions"

    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id"), primary_key=True)
    command_name = Column(String(64), nullable=False)
    allowed_roles = Column(JSON, default=list)
    blocked_users = Column(JSON, default=list)
    is_enabled = Column(Boolean, default=True)

    guild = relationship("Guild", back_populates="permission")
