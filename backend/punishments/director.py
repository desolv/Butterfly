from datetime import datetime, timedelta
from typing import Any

import discord
from discord.ext import commands
from sqlalchemy import and_
from sqlalchemy.orm import Session

from backend.configs.director import get_guild_punishment_config
from backend.core.database import Engine
from backend.core.helper import get_utc_now, send_private_dm
from backend.punishments.models import Punishment, PunishmentType


def create_punishment(
        guild_id: int,
        user_id: int,
        added_by: int,
        punishment_type: PunishmentType,
        reason: str = "No reason",
        duration: datetime = None
):
    """
    Create and save a new punishment record
    """
    with Session(Engine) as session:
        punishment = Punishment(
            guild_id=guild_id,
            user_id=user_id,
            added_by=added_by,
            type=punishment_type,
            reason=reason,
            added_at=get_utc_now(),
            expires_at=duration,
            is_active=True if punishment_type in (PunishmentType.MUTE, PunishmentType.BAN) else False
        )

        session.add(punishment)
        session.commit()
        session.refresh(punishment)

        return punishment


def get_global_active_expiring_punishments_within(within_seconds: int = 120):
    """
    Fetch active mutes/bans expiring within a given timespan
    """
    threshold = get_utc_now() + timedelta(seconds=within_seconds)
    with Session(Engine) as session:
        return session.query(Punishment).filter(
            and_(
                Punishment.is_active == True,
                Punishment.type.in_([PunishmentType.MUTE, PunishmentType.BAN]),
                Punishment.expires_at <= threshold
            )
        ).all()


def get_punishment_by_id(guild_id: int, punishment_id: int):
    """
    Retrieve a punishment by its guild and ID
    """
    with Session(Engine) as session:
        return session.query(Punishment).filter_by(
            guild_id=guild_id,
            punishment_id=punishment_id
        ).first()


def get_user_punishments(
        guild_id: int,
        user_id: int,
        punishment_type: PunishmentType = None
):
    """
    List punishments for a user, optionally filtered by type
    """
    with Session(Engine) as session:
        if punishment_type:
            return session.query(Punishment).filter_by(
                guild_id=guild_id,
                user_id=user_id,
                type=punishment_type
            ).all()
        return session.query(Punishment).filter_by(
            guild_id=guild_id,
            user_id=user_id
        ).all()


def get_user_active_punishment(
        guild_id: int,
        user_id: int,
        punishment_type: PunishmentType
):
    """
    Get the active punishment of a specific type for a user
    """
    with Session(Engine) as session:
        return session.query(Punishment).filter_by(
            guild_id=guild_id,
            user_id=user_id,
            type=punishment_type,
            is_active=True
        ).first()


def remove_user_active_punishment(
        guild_id: int,
        punishment_id: int,
        removed_by: int = None,
        reason: str = "No reason"
):
    """
    Mark an active punishment as removed with a reason
    """
    with Session(Engine) as session:
        punishment = session.query(Punishment).filter_by(
            guild_id=guild_id,
            punishment_id=punishment_id,
            is_active=True
        ).first()

        if not punishment:
            return False

        punishment.removed_at = get_utc_now()
        punishment.removed_by = removed_by  # can be None
        punishment.removed_reason = reason
        punishment.is_active = False

        session.add(punishment)
        session.commit()
        session.refresh(punishment)

        return punishment, True


def is_valid_punishment_type(value: Any):
    """
    Check if a string matches a valid PunishmentType
    """
    if not isinstance(value, str):
        return False, None

    key = value.upper()
    try:
        member = PunishmentType[key]
        return True, member
    except KeyError:
        return False, None


def get_punishment_metadata(punishment_type: PunishmentType):
    """
    Map a PunishmentType to its display name, icon, and color
    """
    match punishment_type:
        case PunishmentType.KICK:
            return "Kick", "ᴋɪᴄᴋ", discord.Color.yellow()
        case PunishmentType.WARN:
            return "Warn", "ᴡᴀʀɴ", discord.Color.teal()
        case PunishmentType.MUTE:
            return "Mute", "ᴍᴜᴛᴇ", discord.Color.green()
        case PunishmentType.BAN:
            return "Ban", "ʙᴀɴ", discord.Color.red()
        case _:
            return "?", "?", discord.Color.from_str("#393A41")


async def send_punishment_moderation_log(guild: discord.Guild, member: discord.Member, moderator: discord.Member,
                                         punishment: Punishment, sent_dm: bool,
                                         duration: str = None, removed: bool = False):
    """
    Log punishment actions to the guild's moderation channel
    """
    punishment_name, punishment_fancy, punishment_color = get_punishment_metadata(punishment.type)
    punishment_color = discord.Color.pink() if removed else punishment_color

    _, _, _, moderation_channel, _ = get_guild_punishment_config(guild.id)

    description = (
        f"**ᴍᴏᴅᴇʀᴀᴛᴏʀ**: {'?' if moderator is None else moderator.mention}\n"
        f"**ʀᴇᴀѕᴏɴ**: {punishment.removed_reason if removed else punishment.reason}\n"
    )

    if not removed and punishment.type is not PunishmentType.WARN:
        description += f"**ᴅᴜʀᴀᴛɪᴏɴ**: {'Permanent' if duration in ('permanent', 'perm') else duration}\n"

    description += (
        f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ɪᴅ**: **{punishment.punishment_id}**\n"
        f"**ᴘʀɪᴠᴀᴛᴇ ᴅᴍ**: {'✅' if sent_dm else '❎'}"
    )

    embed = discord.Embed(
        title=f"{punishment_fancy} ᴘᴜɴɪѕʜᴍᴇɴᴛ ꜰᴏʀ @{member}" if not removed else f"{punishment_fancy} ʀᴇᴍᴏᴠᴇᴅ ꜰᴏʀ @{member}",
        description=description,
        color=punishment_color,
        timestamp=datetime.utcnow()
    )

    avatar_url = member.avatar.url if member.avatar is not None else "https://cdn.discordapp.com/embed/avatars/0.png"
    embed.set_thumbnail(url=avatar_url)

    channel = guild.get_channel(moderation_channel)

    if channel:
        await channel.send(embed=embed)


async def has_permission_to_punish(ctx, member: discord.Member) -> bool:
    """
    Verify the command issuer can punish the specified member
    """
    if member.id == ctx.author.id:
        await ctx.send(f"You can't punish your self!")
        return False

    if ctx.author.guild_permissions.administrator:
        return True

    _, protected_roles, protected_users, _, _ = get_guild_punishment_config(ctx.guild.id)

    protected_roles = set(protected_roles)
    member_role_ids = {role.id for role in member.roles}

    if member.id in protected_users or member_role_ids & protected_roles:
        await ctx.send(f"{member.mention} has an exception from punishments!")
        return False

    if ctx.author.top_role.position <= member.top_role.position:
        await ctx.send(f"{member.mention} has an higher or equal role to yours.")
        return False

    return True


async def process_punishment_removal(bot: commands.Bot, guild: discord.Guild, punishment: Punishment,
                                     moderator: discord.Member, reason: str):
    """
    Remove roles/unban and mark punishment as revoked
    """
    match punishment.type:
        case PunishmentType.MUTE:
            try:
                muted_role, _, _, _, _ = get_guild_punishment_config(punishment.guild_id)
                member = guild.get_member(punishment.user_id)
                muted_role = guild.get_role(muted_role)
                await member.remove_roles(muted_role, reason=reason)
            except Exception as e:
                print(f"Wasn't able remove mute for {punishment.user_id}. Aborting! -> {e}")
                return

            sent_dm = await send_private_dm(member,
                                            f"Hey! **You're able to chat now at {guild.name}!** Please refrain from breaking rules again.")
        case PunishmentType.BAN:
            try:
                await guild.unban(discord.Object(id=punishment.user_id), reason=reason)
            except Exception as e:
                print(f"Wasn't able remove ban for {punishment.user_id}. Aborting! -> {e}")
                return

            try:
                member = await bot.fetch_user(punishment.user_id)
            except Exception:
                member = None

            sent_dm = False
        case _:
            return

    removed_punishment, success = remove_user_active_punishment(
        punishment.guild_id,
        punishment.punishment_id,
        moderator.id,
        reason
    )

    await send_punishment_moderation_log(
        guild,
        member,
        moderator,
        removed_punishment,
        sent_dm,
        removed=True
    )
