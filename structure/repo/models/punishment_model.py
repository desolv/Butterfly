from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Integer, BigInteger, DateTime, Enum as SqlEnum, String, Index, Boolean

from structure.repo.database import base


class PunishmentType(Enum):
    BAN = "ban"
    MUTE = "mute"
    KICK = "kick"
    WARN = "warn"


class Punishment(base):
    __tablename__ = "punishments"
    __table_args__ = (
        Index("ix_punishment_punishment_id", "punishment_id"),
        Index("ix_punishment_user_id", "user_id"),
        Index("ix_punishment_created_at", "created_at"),
        Index("ix_punishment_removed_by", "removed_by"),
        Index("ix_punishment_is_active", "is_active"),
        Index("ix_punishment_type", "type"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci"
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    punishment_id = Column(String(255), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    moderator_id = Column(BigInteger, nullable=False)
    type = Column(SqlEnum(PunishmentType), nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    removed_by = Column(BigInteger, nullable=True)
    removed_at = Column(DateTime, nullable=True)
    removed_reason = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=True)

    def __repr__(self):
        return f"<Punishment {self.type.value.upper()} for {self.user_id}>"


    def get_duration(self) -> int | None:
        if self.expires_at and self.created_at:
            return int((self.expires_at - self.created_at).total_seconds())
        return None


    def has_expired(self) -> bool:
        return self.expires_at is not None and datetime.utcnow() >= self.expires_at