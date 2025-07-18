from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from structure.repo.database import engine
from structure.repo.models.punishment_model import Punishment, PunishmentType


def create_punishment(punishment_id: str, user_id: int, moderator_id: int, type: PunishmentType, reason: str = None, duration: int = None):
    now = datetime.utcnow()
    expires_at = now + timedelta(seconds=duration) if duration else None
    is_active = True if type in (PunishmentType.MUTE, PunishmentType.BAN) and expires_at else None

    with Session(engine) as session:
        punishment = Punishment(
            punishment_id=punishment_id,
            user_id=user_id,
            moderator_id=moderator_id,
            type=type,
            reason=reason,
            created_at=now,
            duration=duration,
            expires_at=expires_at,
            active=is_active
        )
        session.add(punishment)
        session.commit()
        session.refresh(punishment)
        return punishment


def get_user_punishments(user_id: int):
    with Session(engine) as session:
        return session.query(Punishment).filter_by(user_id=user_id).order_by(Punishment.created_at.desc()).all()


def get_active_punishments():
    with Session(engine) as session:
        return session.query(Punishment).filter(
            Punishment.active == True,
            Punishment.expires_at <= datetime.utcnow()
        ).all()

def deactivate_punishment(punishment_id: str, moderator_id: int | None = None) -> bool:
    with Session(engine) as session:
        punishment = session.query(Punishment).filter_by(punishment_id=punishment_id).first()
        if not punishment:
            return False
        punishment.removed_at = datetime.utcnow()
        punishment.removed_by = moderator_id  # can be None
        punishment.active = False
        session.commit()
        return True

