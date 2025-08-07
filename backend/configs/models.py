from sqlalchemy import Column, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import relationship

from backend.core.database import Base


class Config(Base):
    __tablename__ = "configurations"

    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id", ondelete="CASCADE"), primary_key=True)
    punishment = Column(MutableDict.as_mutable(JSONB), default=lambda: {
        "muted_role": None,
        "protected_roles": [],
        "protected_users": [],
        "moderation_channel": None,
        "last_modify": None
    })

    guild = relationship("Guild", back_populates="configuration")
