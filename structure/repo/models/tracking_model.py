from datetime import datetime

from sqlalchemy import Column, Integer, BigInteger, DateTime, Text, Boolean, Index

from structure.repo.database import base


class Track(base):
    __tablename__ = "track"
    __table_args__ = (
        Index("ix_track_user_id", "user_id"),
        Index("ix_track_channel_id", "channel_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci"
        }
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)
    message = Column(Text, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    channel_id = Column(BigInteger, nullable=False)
    removed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Track {self.user_id} @ {self.channel_id} & {self.message_id}>"
