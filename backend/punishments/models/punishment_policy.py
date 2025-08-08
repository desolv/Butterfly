from sqlalchemy import Column, BigInteger, ForeignKey, ARRAY, DateTime
from sqlalchemy.orm import relationship

from backend.core.database import Base
from backend.core.helper import get_utc_now


class PunishmentPolicy(Base):
    __tablename__ = "punishment_policy"

    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id", ondelete="CASCADE"), unique=True, primary_key=True)
    muted_role_id = Column(BigInteger)
    logging_channel_id = Column(BigInteger)
    protected_roles = Column(ARRAY(BigInteger), default=list)
    protected_users = Column(ARRAY(BigInteger), default=list)
    updated_at = Column(DateTime, default=get_utc_now(), onupdate=get_utc_now())
    updated_by = Column(BigInteger, nullable=True)

    guild = relationship("Guild", back_populates="punishment_policies")
