from datetime import datetime, timedelta

from sqlalchemy import and_
from sqlalchemy.orm import Session

from structure.repo.database import engine
from structure.repo.models.punishment_model import Punishment, PunishmentType


def create_punishment(punishment_id: str, user_id: int, moderator_id: int, type: PunishmentType, reason: str = None, duration: datetime = None):
    with Session(engine) as session:
        punishment = Punishment(
            punishment_id=punishment_id,
            user_id=user_id,
            moderator_id=moderator_id,
            type=type,
            reason=reason,
            created_at=datetime.utcnow(),
            expires_at=duration,
            is_active=True if type in (PunishmentType.MUTE, PunishmentType.BAN) else None
        )

        session.add(punishment)
        session.commit()
        session.refresh(punishment)

        return punishment


def get_global_active_expiring_punishments_within(within_seconds: int = 120):
    threshold = datetime.utcnow() + timedelta(seconds=within_seconds)
    with Session(engine) as session:
        return session.query(Punishment).filter(
            and_(
                Punishment.is_active == True,
                Punishment.expires_at <= threshold
            )
        ).order_by(Punishment.expires_at.asc()).all()


def get_id_punishment(punishment_id: str):
    with Session(engine) as session:
        return session.query(Punishment).filter_by(punishment_id=punishment_id).first()


def get_user_punishments(user_id: int, type : PunishmentType = None):
    with Session(engine) as session:
        if type:
            return session.query(Punishment).filter_by(
                user_id=user_id,
                type=type
            ).all()
        return session.query(Punishment).filter_by(user_id=user_id).all()


def get_user_active_punishment(user_id: int, type: PunishmentType):
    with Session(engine) as session:
        return session.query(Punishment).filter_by(
            user_id=user_id,
            type=type,
            is_active=True
        ).first()


def remove_user_active_punishment(punishment_id: str, moderator_id: int = None, reason : str = "No reason provided"):
    with Session(engine) as session:
        punishment = session.query(Punishment).filter_by(
            punishment_id=punishment_id,
            is_active=True
        ).first()

        if not punishment:
            return False

        punishment.removed_at = datetime.utcnow()
        punishment.removed_by = moderator_id  # can be None
        punishment.removed_reason = reason
        punishment.is_active = False

        session.add(punishment)
        session.commit()
        session.refresh(punishment)

        return punishment, True


