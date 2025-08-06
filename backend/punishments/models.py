from enum import auto, StrEnum

from sqlalchemy import Column, BigInteger, DateTime, Enum as SqlEnum, String, Boolean, ForeignKey

from backend.core.database import Base
from backend.core.helper import get_utc_now


class PunishmentType(StrEnum):
    BAN = auto()
    MUTE = auto()
    KICK = auto()
    WARN = auto()


class Punishment(Base):
    __tablename__ = "punishments"

    punishment_id = Column(BigInteger, primary_key=True)
    guild_id = Column(BigInteger, ForeignKey("guilds.guild_id", ondelete="CASCADE"), index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    added_by = Column(BigInteger, nullable=False, index=True)
    type = Column(SqlEnum(PunishmentType), nullable=False, index=True)
    reason = Column(String(255), nullable=True)
    added_at = Column(DateTime, default=get_utc_now())
    expires_at = Column(DateTime, nullable=True)
    removed_by = Column(BigInteger, nullable=True, index=True)
    removed_at = Column(DateTime, nullable=True)
    removed_reason = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=True, index=True)

    def get_duration(self) -> int | None:
        if self.expires_at and self.added_at:
            return int((self.expires_at - self.added_at).total_seconds())
        return None

    def has_expired(self) -> bool:
        return self.expires_at is not None and get_utc_now() >= self.expires_at
