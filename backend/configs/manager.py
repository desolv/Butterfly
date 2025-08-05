from sqlalchemy.orm import Session

from backend.configs.models import Config
from backend.core.database import Engine


def update_punishment_config(guild_id: int, **kwargs):
    """
    Update the punishment configuration for the specified guild using provided keyword arguments.
    """
    with Session(Engine) as session:
        config = session.query(Config).filter_by(guild_id=guild_id).first()
        session.add(config)
        session.commit()
        session.refresh(config)

        payload = config.punishment or {}

        for key, value in kwargs.items():
            if value is not None and key in payload:
                payload[key] = value

        config.punishment = payload
        session.commit()
        return config


def get_punishment_settings(guild_id: int) -> tuple:
    """
    Retrieve the punishment settings for the specified guild as a tuple
    """
    with Session(Engine) as session:
        config = session.get(Config, guild_id)
        if not config:
            config = Config(guild_id=guild_id)
            session.add(config)
            session.commit()
            session.refresh(config)
        data = config.punishment or {}
        return (
            data.get("muted_role"),
            data.get("protected_roles", []),
            data.get("protected_users", []),
            data.get("moderation_channel"),
            data.get("last_modify")
        )
