from discord.ext import commands
from sqlalchemy.orm import Session

from backend.core.database import Engine
from backend.core.helper import is_valid_command, get_all_command_names
from backend.permissions.models.permission import Permission


def get_permissions_for_guild(bot: commands.Bot | None, guild_id: int) -> list[type[Permission]]:
    """
    Retrieve all Permission entries for the given guild.
    """
    with Session(Engine) as session:
        for perm in session.query(Permission).filter_by(guild_id=guild_id):
            if bot is not None and not is_valid_command(bot, perm.command_name):
                session.delete(perm)

        session.commit()
        results = session.query(Permission).filter_by(guild_id=guild_id).all()

    return results


def create_or_retrieve_command(
        bot: commands.Bot | None,
        guild_id: int,
        command_name: str,
        **kwargs
):
    """
    Retrieve existing or create new Permission entry for the given guild and command.
    """
    command_name = command_name.lower()

    with Session(Engine) as session:
        permission = session.query(Permission).filter_by(guild_id=guild_id, command_name=command_name).first()

        if permission is not None:
            if bot is not None and not is_valid_command(bot, command_name):
                session.delete(permission)
                session.commit()
                return None

        if permission is None:
            if bot is not None and not is_valid_command(bot, command_name):
                return None

            permission = Permission(guild_id=guild_id, command_name=command_name)

        for field, value in kwargs.items():
            if value is not None and hasattr(permission, field):
                setattr(permission, field, value)

        session.add(permission)
        session.commit()
        session.refresh(permission)
        return permission


def initialize_permissions_for_guild(bot: commands.Bot, guild_id: int):
    """
    Seed a fresh Permission table for a new guild.
    Creates one Permission row per command/subcommand without checking for existing entries.
    """
    all_names = get_all_command_names(bot, True)

    perms = [
        Permission(guild_id=guild_id, command_name=name)
        for name in all_names
    ]

    with Session(Engine) as session:
        session.add_all(perms)
        session.commit()
        print(f"Created permissions for {guild_id}!")
