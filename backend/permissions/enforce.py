import time

from discord.app_commands import Cooldown
from discord.ext import commands
from discord.ext.commands import CheckFailure, BucketType
from discord.ext.commands import (
    Context,
    CommandOnCooldown,
)

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
        permission = create_or_retrieve_command(
            None,
            guild_id,
            ctx.command.qualified_name
        )

        if permission is None:
            raise CheckFailure("I couldn't retrieve the command permissions, contact an administrator!")

        if not permission.is_enabled:
            raise CheckFailure("That command is currently disabled in this guild")

        if ctx.author.guild_permissions.administrator:
            return True

        if permission.is_admin and not ctx.author.guild_permissions.administrator:
            return False

        required_ids = permission.required_role_ids or []
        if not required_ids:
            return False

        if guild_id in required_ids:
            return True

        return any(role.id in required_ids for role in ctx.author.roles)

    return commands.check(predicate)


_last_invocations: dict[tuple[int, str, int], float] = {}


def has_cooldown():
    """
    Decorator to enforce per-command cooldowns using _last_invocations
    """

    def predicate(ctx: Context) -> bool:
        if ctx.guild is None:
            return True

        if ctx.author.guild_permissions.administrator:
            return True

        guild_id = ctx.guild.id
        permission = create_or_retrieve_command(None, guild_id, str(ctx.command))
        cooldown_secs = permission.command_cooldown

        if cooldown_secs <= 0:
            return True

        key = (guild_id, str(ctx.command), ctx.author.id)
        now = time.time()
        last = _last_invocations.get(key)

        if last is not None:
            elapsed = now - last
            retry_after = cooldown_secs - elapsed

            if retry_after > 0:
                dummy_cd = Cooldown(1, cooldown_secs)
                raise CommandOnCooldown(dummy_cd, retry_after, BucketType.user)

        _last_invocations[key] = now
        return True

    return commands.check(predicate)
