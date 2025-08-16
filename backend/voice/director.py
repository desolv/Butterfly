from sqlalchemy.orm import Session

from backend.core.database import Engine
from backend.voice.models.voice_config import VoiceConfig


def update_or_retrieve_voice_config(guild_id: int, **kwargs):
    """
        Apply updates for voice config
    """
    with Session(Engine) as session:
        config = (
            session.query(VoiceConfig)
            .filter_by(guild_id=guild_id)
            .first()
        )

        if not config:
            config = VoiceConfig(guild_id=guild_id)

        embed_updates = {}
        if "embed_title" in kwargs:
            embed_updates["title"] = kwargs.pop("embed_title")
        if "embed_description" in kwargs:
            embed_updates["description"] = kwargs.pop("embed_description")

        if embed_updates:
            current = getattr(config, "embed") or {}
            setattr(config, "embed", {**current, **embed_updates})

        for field, value in kwargs.items():
            if value is not None and hasattr(config, field):
                setattr(config, field, value)

        session.add(config)
        session.commit()
        session.refresh(config)

        return config
