from sqlalchemy import Column, BigInteger, DateTime, Enum, String, Boolean, ForeignKey

from backend.core.database import Base
from backend.core.helper import get_time_now
from backend.punishments.models.punishment_type import PunishmentType


class Punishment(Base):
    __tablename__ = "punishments"

    punishment_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id", ondelete="CASCADE"), index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    added_by = Column(BigInteger, nullable=False, index=True)
    type = Column(Enum(PunishmentType), nullable=False, index=True)
    reason = Column(String(255), nullable=True)
    added_at = Column(DateTime, default=get_time_now())
    expires_at = Column(DateTime, nullable=True)
    removed_by = Column(BigInteger, nullable=True, index=True)
    removed_at = Column(DateTime, nullable=True)
    removed_reason = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=True, index=True)

    def has_expired(self) -> bool:
        return self.expires_at is not None and get_time_now() >= self.expires_at
