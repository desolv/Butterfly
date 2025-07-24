from datetime import datetime

import discord
from discord.ext import commands

from structure.providers.helper import load_json_data, generate_id, parse_time_window, send_private_dm, \
    format_subcommands, get_formatted_time
from structure.providers.preconditions import has_roles
from structure.repo.models.punishment_model import PunishmentType, Punishment
from structure.repo.services.punishment_service import create_punishment, get_user_active_punishment, get_id_punishment


def get_punishment_metadata(punishment_type: PunishmentType):
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
                                         punishment: Punishment, moderation_channel: int, sent_dm: bool,
                                         duration: str = None, removed: bool = False):
    punishment_name, punishment_fancy, punishment_color = get_punishment_metadata(punishment.type)
    punishment_color = discord.Color.pink() if removed else punishment_color

    description = (
        f"**ᴍᴏᴅᴇʀᴀᴛᴏʀ**: {'?' if moderator is None else moderator.mention}\n"
        f"**ʀᴇᴀѕᴏɴ**: {punishment.removed_reason if removed else punishment.added_reason}\n"
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


class PunishmentCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = load_json_data(f"environment")["guild_id"]
        punishments = load_json_data(f"environment")["punishments"]
        self.exempt_roles = punishments["exempt_roles"]
        self.exempt_users = punishments["exempt_users"]
        self.moderation_channel = punishments["moderation_channel"]
        self.muted_role_id = punishments["muted_role"]

    def is_exempt(self, member: discord.Member) -> bool:
        if member.id in self.exempt_users:
            return True
        for role in member.roles:
            if role.id in self.exempt_roles:
                return True
        return False

    @has_roles(name="punishment")
    @commands.group(
        name="punishment",
        aliases=['punish'],
        invoke_without_command=True
    )
    async def _punishment(self, ctx):
        embed = discord.Embed(
            title="ᴘᴜɴɪѕʜᴍᴇɴᴛ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            description="\n".join(format_subcommands(self.bot, "punishment")),
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        await ctx.send(embed=embed)

    @has_roles(name="punishment", sub="metadata")
    @_punishment.command(
        name="metadata",
        description="Show punishment information"
    )
    async def _punishment_metadata(self, ctx, punishment_id: str):
        punishment = get_id_punishment(punishment_id)

        if not punishment:
            await ctx.send(f"No punishment matching **{punishment_id}** found!")
            return

        try:
            member = await self.bot.fetch_user(punishment.user_id)
            added_by = await self.bot.fetch_user(punishment.added_by)
        except Exception:
            member = None
            added_by = None

        punishment_name, punishment_fancy, punishment_color = get_punishment_metadata(punishment.type)

        description = (
            f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ɪᴅ**: **{punishment_id}**\n"
            f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴛʏᴘᴇ**: **{punishment_name}**\n\n"
            f"**ᴀᴅᴅᴇᴅ ʙʏ**: {punishment.added_by if not added_by else added_by.mention}\n"
            f"**ᴀᴅᴅᴇᴅ ᴀᴛ**: **{get_formatted_time(punishment.added_at, format="%d/%m/%y %H:%M %Z")}**\n"
            f"**ᴀᴅᴅᴇᴅ ʀᴇᴀѕᴏɴ**: {punishment.added_reason}\n"
            f"**ᴅᴜʀᴀᴛɪᴏɴ**: {punishment.get_duration()}s\n"
        )

        if not punishment.is_active and (
                punishment.type is PunishmentType.MUTE or punishment.type is PunishmentType.BAN):

            try:
                removed_by = await self.bot.fetch_user(punishment.removed_by)
            except Exception:
                removed_by = None

            description += (
                f"\n**ʀᴇᴍᴏᴠᴇᴅ ʙʏ**: {self.bot.user.mention if removed_by is None else removed_by.mention}\n"
                f"**ʀᴇᴍᴏᴠᴇᴅ ᴀᴛ**: **{get_formatted_time(punishment.removed_at, format="%d/%m/%y %H:%M %Z")}**\n"
                f"**ʀᴇᴍᴏᴠᴇᴅ ʀᴇᴀѕᴏɴ**: {punishment.removed_reason}"
            )

        embed = discord.Embed(
            title=f"ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ ꜰᴏʀ @{punishment.user_id if not member else member}",
            description=description,
            color=punishment_color,
            timestamp=datetime.utcnow()
        )

        avatar_url = member.avatar.url if member.avatar is not None else "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_thumbnail(url=avatar_url)

        await ctx.send(embed=embed)

    @has_roles(name="kick")
    @commands.command(
        name="kick",
        description="Kick a member from the server"
    )
    async def _kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.id == ctx.author.id:
            await ctx.send(f"You can't punish your self!")
            return

        if self.is_exempt(member):
            await ctx.send(f"**@{member}** is exempt from punishments!")
            return

        try:
            await member.kick(reason=reason)
        except discord.Forbidden:
            await ctx.send(f"Wasn't able to kick **{member}**. Aborting!")
            return

        punishment = create_punishment(
            generate_id(),
            member.id,
            ctx.author.id,
            PunishmentType.KICK,
            reason
        )

        await ctx.send(f"**@{member}** has been kicked for **{reason}**.")
        sent_dm = await send_private_dm(member, f"You have been kicked from the server for **{reason}**.", ctx)

        await send_punishment_moderation_log(
            ctx.guild,
            member,
            ctx.author,
            punishment,
            self.moderation_channel,
            sent_dm
        )

    @has_roles(name="warn")
    @commands.command(
        name="warn",
        description="Warn a member via sending a private message"
    )
    async def _warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member.id == ctx.author.id:
            await ctx.send(f"You can't punish your self!")
            return

        if self.is_exempt(member):
            await ctx.send(f"**@{member}** is exempt from punishments!")
            return

        punishment = create_punishment(
            generate_id(),
            member.id,
            ctx.author.id,
            PunishmentType.WARN,
            reason
        )

        await ctx.send(f"**@{member}** has been warned for **{reason}**.")
        sent_dm = await send_private_dm(member, f"You have been warned for **{reason}**.", ctx)

        await send_punishment_moderation_log(
            ctx.guild,
            member,
            ctx.author,
            punishment,
            self.moderation_channel,
            sent_dm
        )

    @has_roles(name="mute")
    @commands.command(
        name="mute",
        description="Mute a member by giving them a role"
    )
    async def _mute(self, ctx, member: discord.Member, duration: str = "1h", *, reason: str = "No reason provided"):
        if member.id == ctx.author.id:
            await ctx.send(f"You can't punish your self!")
            return

        if self.is_exempt(member):
            await ctx.send(f"**@{member}** is exempt from punishments!")
            return

        if get_user_active_punishment(member.id, PunishmentType.MUTE):
            await ctx.send(f"**@{member}** is already muted!")
            return

        permanent = True if duration.lower() in ("permanent", "perm") else False

        if not permanent:
            try:
                parse_duration = parse_time_window(duration)
            except ValueError as e:
                await ctx.send(e)
                return

        try:
            muted_role = ctx.guild.get_role(self.muted_role_id)
            await member.add_roles(muted_role, reason=reason)
        except discord.Forbidden:
            await ctx.send(f"Wasn't able to add mute to **{member}**. Aborting!")
            return

        punishment = create_punishment(
            generate_id(),
            member.id,
            ctx.author.id,
            PunishmentType.MUTE,
            reason,
            None if permanent else parse_duration
        )

        duration_msg = "permanently" if permanent else "temporarily"
        await ctx.send(f"**@{member}** has been {duration_msg} muted for **{reason}**.")

        expiring = "**never** expiring!" if permanent else f"expiring in **{duration}**."
        sent_dm = await send_private_dm(member, f"You have been muted for **{reason}** it's {expiring}", ctx)

        await send_punishment_moderation_log(
            ctx.guild,
            member,
            ctx.author,
            punishment,
            self.moderation_channel,
            sent_dm,
            duration
        )

    @has_roles(name="ban")
    @commands.command(
        name="ban",
        description="Ban a member by removing them from the server"
    )
    async def _ban(self, ctx, member: discord.Member, duration: str = "1h", *, reason: str = "No reason provided"):
        if member.id == ctx.author.id:
            await ctx.send(f"You can't punish your self!")
            return

        if self.is_exempt(member):
            await ctx.send(f"**@{member}** is exempt from punishments!")
            return

        if get_user_active_punishment(member.id, PunishmentType.BAN):
            await ctx.send(f"**@{member}** is already banned!")
            return

        permanent = True if duration.lower() in ("permanent", "perm") else False

        if not permanent:
            try:
                parse_duration = parse_time_window(duration)
            except ValueError as e:
                await ctx.send(e)
                return

        try:
            await member.ban(reason=reason)
        except discord.Forbidden:
            await ctx.send(f"Wasn't able to ban **{member}**. Aborting!")
            return

        punishment = create_punishment(
            generate_id(),
            member.id,
            ctx.author.id,
            PunishmentType.BAN,
            reason,
            None if permanent else parse_duration
        )

        duration_msg = "permanently" if permanent else "temporarily"
        await ctx.send(f"**@{member}** has been {duration_msg} banned for **{reason}**.")

        expiring = "**never** expiring!" if permanent else f"expiring in **{duration}**."
        sent_dm = await send_private_dm(member, f"You have been banned for **{reason}** it's {expiring}", ctx)

        await send_punishment_moderation_log(
            ctx.guild,
            member,
            ctx.author,
            punishment,
            self.moderation_channel,
            sent_dm,
            duration
        )


async def setup(bot):
    await bot.add_cog(PunishmentCommandCog(bot))
