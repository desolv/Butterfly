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
        Index("ix_relay_type", "type"),
        Index("ix_relay_created_at", "created_at"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci"
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    moderator_id = Column(BigInteger, nullable=False)
    type = Column(SqlEnum(PunishmentType), nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    duration = Column(Integer, nullable=True)  # seconds; null = permanent
    expires_at = Column(DateTime, nullable=True)
    active = Column(Boolean, nullable=True)

    def __repr__(self):
        return f"<Punishment {self.type.value.upper()} for {self.user_id}>"
