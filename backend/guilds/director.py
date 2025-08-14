from discord.ext import commands
from sqlalchemy.orm import Session

from backend.core.database import Engine
from backend.core.helper import get_time_now
from backend.guilds.models.guild import Guild
from backend.permissions.director import initialize_permissions_for_guild
from backend.punishments.models.punishment_config import PunishmentConfig


def create_or_update_guild(bot: commands.Bot, guild_id: int, **kwargs):
    """
        Ensure a Guild record exists in the database and apply updates.
    """
    with Session(Engine) as session:
        guild = session.query(Guild).filter_by(guild_id=guild_id).first()

        if not guild:
            guild = Guild(guild_id=guild_id, added_at=get_time_now(), is_active=True)
            guild.punishment_configs = PunishmentConfig(guild_id=guild_id)

            session.add(guild)
            session.commit()
            session.refresh(guild)

            initialize_permissions_for_guild(bot, guild_id)

        for field, value in kwargs.items():
            if value is not None and hasattr(guild, field):
                setattr(guild, field, value)

        session.add(guild)
        session.commit()
        session.refresh(guild)

        return guild
