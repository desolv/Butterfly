from sqlalchemy.orm import Session

from backend.configs.models import Config
from backend.core.database import Engine
from backend.core.helper import get_utc_now
from backend.guilds.models import Guild
from backend.permissions.models import Permission


def create_or_update_guild(bot, guild_id: int, **kwargs):
    with Session(Engine) as session:
        guild = session.query(Guild).filter_by(guild_id=guild_id).first()
        discord_guild = bot.get_guild(guild_id)

        if discord_guild and not guild:
            guild = Guild(guild_id=guild_id, added_at=get_utc_now(), is_active=True)
            guild.config = Config(guild_id=guild_id)
            guild.permission = Permission(guild_id=guild_id)

        for field, value in kwargs.items():
            if value is not None and hasattr(guild, field):
                setattr(guild, field, value)

        session.add(guild)
        session.commit()
        session.refresh(guild)

        return guild, discord_guild
