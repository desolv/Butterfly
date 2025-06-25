from datetime import datetime

from sqlalchemy import Column, Integer, BigInteger, DateTime, Text, Boolean, Index

from structure.repo.database import base


class Relay(base):
    __tablename__ = "relay"
    __table_args__ = (
        Index("ix_relay_message_id", "message_id"),
        Index("ix_relay_discord_id", "discord_id"),
        Index("ix_relay_timestamp", "timestamp"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci"
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(BigInteger, nullable=False)
    message = Column(Text, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    channel_id = Column(BigInteger, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Relay {self.discord_id} @ {self.channel_id} & {self.message_id}>"

    def mark_deleted(self):
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def unmark_deleted(self):
        self.is_deleted = False
        self.deleted_at = None

