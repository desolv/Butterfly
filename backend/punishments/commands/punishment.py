import discord
from discord.ext import commands

from backend.core.helper import format_time_in_zone, get_time_now, format_duration, \
    get_commands_help_messages
from backend.core.pagination import Pagination
from backend.permissions.enforce import has_permission, has_cooldown
from backend.punishments.director import get_punishment_by_id, get_punishment_metadata, process_punishment_removal, \
    get_user_punishments
from backend.punishments.models.punishment import PunishmentType


class PunishmentCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @commands.group(name="punishment", invoke_without_command=True)
    async def _punishment(self, ctx):
        view = Pagination(
            "ᴘᴜɴɪѕʜᴍᴇɴᴛ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_commands_help_messages(self.bot, [PunishmentCommand], ctx.author.guild_permissions.administrator),
            3,
            ctx.author.id
        )

        await ctx.reply(embed=view.create_embed(), view=view)

    @has_permission()
    @has_cooldown()
    @_punishment.command(name="view")
    async def _punishment_view(self, ctx, punishment_id: int):
        """
        Display detailed information about a specific punishment by ID
        """
        punishment = get_punishment_by_id(ctx.guild.id, punishment_id)

        if not punishment:
            await ctx.reply(f"No punishment matching **#{punishment_id}** found!")
            return

        try:
            member = await self.bot.fetch_user(punishment.user_id)
            added_by = await self.bot.fetch_user(punishment.added_by)
        except Exception:
            member = None
            added_by = None

        member = member.mention if member else "None"
        added_by = added_by.mention if added_by else "None"

        punishment_name, punishment_fancy, punishment_color = get_punishment_metadata(punishment.type)
        added_at_time = format_time_in_zone(punishment.added_at)

        description = (
            f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ɪᴅ**: **{punishment_id}**\n"
            f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴛʏᴘᴇ**: **{punishment_name}**\n\n"
            f"**ᴀᴅᴅᴇᴅ ʙʏ**: {added_by}\n"
            f"**ᴀᴅᴅᴇᴅ ᴀᴛ**: **{added_at_time}**\n"
            f"**ᴀᴅᴅᴇᴅ ʀᴇᴀѕᴏɴ**: {punishment.reason}\n"
        )

        if punishment.type is PunishmentType.MUTE or punishment.type is PunishmentType.BAN:
            expires_at_time = format_duration(punishment.added_at, punishment.expires_at)
            description += (
                f"**ᴅᴜʀᴀᴛɪᴏɴ**: **{expires_at_time}**\n"
            )

            if not punishment.is_active:
                try:
                    removed_by = await self.bot.fetch_user(punishment.removed_by)
                except Exception:
                    removed_by = None

                description += (
                    f"\n**ʀᴇᴍᴏᴠᴇᴅ ʙʏ**: {self.bot.user.mention if removed_by is None else removed_by.mention}\n"
                    f"**ʀᴇᴍᴏᴠᴇᴅ ᴀᴛ**: **{format_time_in_zone(punishment.removed_at)}**\n"
                    f"**ʀᴇᴍᴏᴠᴇᴅ ʀᴇᴀѕᴏɴ**: {punishment.removed_reason}"
                )

        embed = discord.Embed(
            title=f"ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ ꜰᴏʀ @{member}",
            description=description,
            color=punishment_color,
            timestamp=get_time_now()
        )

        avatar_url = member.avatar.url if member.avatar is not None else "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_thumbnail(url=avatar_url)

        await ctx.reply(embed=embed)

    @has_permission()
    @has_cooldown()
    @_punishment.command(name="remove")
    async def _punishment_remove(
            self,
            ctx,
            punishment_id: int,
            *,
            reason: str = "No reason"
    ):
        """
        Remove an active punishment and log the removal with reason
        """
        punishment = get_punishment_by_id(ctx.guild.id, punishment_id)

        if not punishment:
            await ctx.reply(f"No punishment matching **#{punishment_id}** found!")
            return

        if not punishment.is_active:
            await ctx.reply(f"Punishment is currently not active!")
            return

        await process_punishment_removal(
            self.bot,
            punishment,
            ctx.author,
            reason
        )

        member = ctx.guild.get_member(punishment.user_id)

        await ctx.reply(
            f"**@{member if member else punishment.user_id}**'s punishment **#{punishment.punishment_id}** has been removed for **{reason}**")

    @has_permission()
    @has_cooldown()
    @_punishment.command(name="modlog")
    async def _modlog(
            self,
            ctx,
            member: discord.Member,
            punishment_type: PunishmentType = None
    ):
        """
        Display all punishments of member
        """
        guild = ctx.guild
        punishments = get_user_punishments(guild.id, member.id, punishment_type)
        punishment_name, punishment_fancy, _ = get_punishment_metadata(punishment_type)

        if len(punishments) <= 0:
            return await ctx.reply(
                f"No {punishment_name.lower() if punishment_type else ""} punishments to display yet!")

        lines: list[str] = []
        for punishment in punishments:
            try:
                member = await self.bot.fetch_user(punishment.user_id)
                added_by = await self.bot.fetch_user(punishment.added_by)
            except Exception:
                member = None
                added_by = None

            member = member if member else "None"
            added_by = added_by.mention if added_by else "None"

            added_at_time = format_time_in_zone(punishment.added_at)

            punishment_name, _, _ = get_punishment_metadata(punishment.type)

            description = (
                f"**#{punishment.punishment_id}**\n"
                f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴛʏᴘᴇ**: **{punishment_name}**\n"
                f"**ᴀᴅᴅᴇᴅ ʙʏ**: {added_by}\n"
                f"**ᴀᴅᴅᴇᴅ ᴀᴛ**: **{added_at_time}**\n"
                f"**ᴀᴅᴅᴇᴅ ʀᴇᴀѕᴏɴ**: {punishment.reason}\n"
            )

            if punishment.type is PunishmentType.MUTE or punishment.type is PunishmentType.BAN:

                expires_at_time = format_duration(punishment.added_at, punishment.expires_at)
                description += (
                    f"**ᴅᴜʀᴀᴛɪᴏɴ**: **{expires_at_time}**\n"
                )

                if not punishment.is_active:
                    try:
                        removed_by = await self.bot.fetch_user(punishment.removed_by)
                    except Exception:
                        removed_by = None

                    description += (
                        f"**ʀᴇᴍᴏᴠᴇᴅ ʙʏ**: {self.bot.user.mention if removed_by is None else removed_by.mention}\n"
                        f"**ʀᴇᴍᴏᴠᴇᴅ ᴀᴛ**: **{format_time_in_zone(punishment.removed_at)}**\n"
                        f"**ʀᴇᴍᴏᴠᴇᴅ ʀᴇᴀѕᴏɴ**: {punishment.removed_reason}"
                    )

            lines.append(description)

        view = Pagination(
            f"ᴘᴜɴɪѕʜᴍᴇɴᴛ {punishment_fancy if punishment_type else ""} ᴍᴏᴅʟᴏɢ ꜰᴏʀ @{member}",
            lines,
            3,
            ctx.author.id,
            True
        )

        await ctx.reply(embed=view.create_embed(), view=view)


async def setup(bot):
    await bot.add_cog(PunishmentCommand(bot))
