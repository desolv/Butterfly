from sqlalchemy.orm import Session

from structure.repo.database import engine
from structure.repo.models.relay_model import Relay


def create_relay(user_id: int, message: str, message_id: int, channel_id: int):
    with Session(engine) as session:
        entry = Relay(
            user_id=user_id,
            message=message,
            message_id=message_id,
            channel_id=channel_id
        )
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry

def get_relay(message_id: int) -> Relay | None:
    with Session(engine) as session:
        return session.query(Relay).filter_by(message_id=message_id).first()

def delete_relay(message_id: int) -> bool:
    with Session(engine) as session:
        entry = session.query(Relay).filter_by(message_id=message_id).first()
        if entry:
            entry.mark_deleted()
            session.commit()
            return True
        return False

def restore_relay(message_id: int) -> bool:
    with Session(engine) as session:
        entry = session.query(Relay).filter_by(message_id=message_id).first()
        if entry:
            entry.unmark_deleted()
            session.commit()
            return True
        return False
