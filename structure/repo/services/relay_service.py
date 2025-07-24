from datetime import datetime

from sqlalchemy.orm import Session

from structure.repo.database import engine
from structure.repo.models.tracking_model import Track


def create_track(user_id: int, message: str, message_id: int, channel_id: int):
    with Session(engine) as session:
        tracked = Track(
            user_id=user_id,
            message=message,
            message_id=message_id,
            channel_id=channel_id
        )

        session.add(tracked)
        session.commit()
        session.refresh(tracked)

        return tracked


def get_user_track(message_id: int) -> Track | None:
    with Session(engine) as session:
        return session.query(Track).filter_by(message_id=message_id).first()


def remove_user_track(message_id: int):
    with Session(engine) as session:
        tracked = session.query(Track).filter_by(message_id=message_id).first()

        if not tracked:
            return False

        tracked.removed_at = datetime.utcnow()
        tracked.is_active = False

        session.add(tracked)
        session.commit()
        session.refresh(tracked)

        return tracked, True