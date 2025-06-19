from sqlalchemy.orm import Session
from structure.repo.database import engine
from structure.repo.models.logbook_model import Logbook

def create_logbook(discord_id: int, message: str, message_id: int, channel_id: int):
    with Session(engine) as session:
        entry = Logbook(
            discord_id=discord_id,
            message=message,
            message_id=message_id,
            channel_id=channel_id
        )
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry

def get_logbook(message_id: int) -> Logbook | None:
    with Session(engine) as session:
        return session.query(Logbook).filter_by(message_id=message_id).first()

def delete_logbook(message_id: int) -> bool:
    with Session(engine) as session:
        entry = session.query(Logbook).filter_by(message_id=message_id).first()
        if entry:
            entry.mark_deleted()
            session.commit()
            return True
        return False

def restore_logbook(message_id: int) -> bool:
    with Session(engine) as session:
        entry = session.query(Logbook).filter_by(message_id=message_id).first()
        if entry:
            entry.unmark_deleted()
            session.commit()
            return True
        return False
