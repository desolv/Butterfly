from discord.ext import commands
from discord.ext.commands import Context, CheckFailure

from backend.guilds.director import create_or_update_guild
from backend.permissions.director import create_or_retrieve_command


def has_permission():
    """
    Decorator to ensure the invoking user has permission to run the given command
    """

    def predicate(ctx: Context) -> bool:
        if ctx.guild is None:
            return True

        guild_id = ctx.guild.id

        create_or_update_guild(ctx.bot, guild_id)
        permission = create_or_retrieve_command(None, guild_id, str(ctx.command))

        if not permission.is_enabled:
            raise CheckFailure("That command is currently disabled in this guild.")

        if ctx.author.guild_permissions.administrator:
            return True

        if permission.is_admin and not ctx.author.guild_permissions.administrator:
            return False

        if permission.allowed_roles:
            user_role_ids = {role.id for role in ctx.author.roles}
            if not user_role_ids.intersection(permission.allowed_roles):
                raise CheckFailure("You don't have the required role to use this command.")

        return True

    return commands.check(predicate)
