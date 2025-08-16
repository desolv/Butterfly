import discord
from discord.ext import commands

from backend.core.helper import format_time_in_zone, get_time_now, format_duration, \
    get_commands_help_messages, get_user_best, fmt_user
from backend.core.pagination import Pagination
from backend.permissions.enforce import has_permission, has_cooldown
from backend.punishments.director import get_punishment, get_punishment_metadata, process_punishment_removal, \
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
        punishment = get_punishment(ctx.guild.id, punishment_id)

        if not punishment:
            await ctx.reply(f"No punishment matching **#{punishment_id}** found!")
            return

        punishment_name, _, punishment_color = get_punishment_metadata(punishment.type)

        description = (
            f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ɪᴅ**: **{punishment_id}**\n"
            f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴛʏᴘᴇ**: **{punishment_name}**\n\n"
            f"**ᴀᴅᴅᴇᴅ ʙʏ**: {fmt_user(punishment.added_by)}\n"
            f"**ᴀᴅᴅᴇᴅ ᴀᴛ**: {format_time_in_zone(punishment.added_at)}\n"
            f"**ᴇᴠɪᴅᴇɴᴄᴇ**: {punishment.evidence}\n"
            f"**ᴀᴅᴅᴇᴅ ʀᴇᴀѕᴏɴ**: {punishment.reason}\n"
        )

        if punishment.type in (PunishmentType.MUTE, PunishmentType.BAN):
            description += (
                f"**ᴅᴜʀᴀᴛɪᴏɴ**: **{format_duration(punishment.added_at, punishment.expires_at)}**\n"
            )

            if not punishment.is_active:
                description += (
                    f"\n**ʀᴇᴍᴏᴠᴇᴅ ʙʏ**: {fmt_user(punishment.removed_by) if punishment.removed_by is None else self.bot.user.mention}\n"
                    f"**ʀᴇᴍᴏᴠᴇᴅ ᴀᴛ**: **{format_time_in_zone(punishment.removed_at)}**\n"
                    f"**ʀᴇᴍᴏᴠᴇᴅ ʀᴇᴀѕᴏɴ**: {punishment.removed_reason}"
                )

        member = await get_user_best(self.bot, ctx.guild, punishment.user_id)

        embed = discord.Embed(
            title=f"ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ ꜰᴏʀ @{member if member else "None"}",
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
        punishment = get_punishment(ctx.guild.id, punishment_id)

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

        await ctx.reply(
            f"**@{fmt_user(punishment.user_id)}**'s punishment **#{punishment.punishment_id}** has been removed for **{reason}**")

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
        punishments = get_user_punishments(ctx.guild.id, member.id, punishment_type)

        if len(punishments) <= 0:
            return await ctx.reply(
                f"No {punishment_type if punishment_type else ""} punishments to display yet!")

        lines: list[str] = []
        for punishment in punishments:
            punishment_name, _, _ = get_punishment_metadata(punishment.type)

            description = (
                f"**#{punishment.punishment_id}**\n"
                f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴛʏᴘᴇ**: **{punishment_name}**\n"
                f"**ᴀᴅᴅᴇᴅ ʙʏ**: {fmt_user(punishment.added_by)}\n"
                f"**ᴀᴅᴅᴇᴅ ᴀᴛ**: **{format_time_in_zone(punishment.added_at)}**\n"
                f"**ᴇᴠɪᴅᴇɴᴄᴇ**: {punishment.evidence}\n"
                f"**ᴀᴅᴅᴇᴅ ʀᴇᴀѕᴏɴ**: {punishment.reason}\n"
            )

            if punishment.type in (PunishmentType.MUTE or PunishmentType.BAN):
                description += (
                    f"**ᴅᴜʀᴀᴛɪᴏɴ**: **{format_duration(punishment.added_at, punishment.expires_at)}**\n"
                )

                if not punishment.is_active:
                    description += (
                        f"**ʀᴇᴍᴏᴠᴇᴅ ʙʏ**: {self.bot.user.mention if punishment.removed_by is None else fmt_user(punishment.removed_by)}\n"
                        f"**ʀᴇᴍᴏᴠᴇᴅ ᴀᴛ**: **{format_time_in_zone(punishment.removed_at)}**\n"
                        f"**ʀᴇᴍᴏᴠᴇᴅ ʀᴇᴀѕᴏɴ**: {punishment.removed_reason}"
                    )

            lines.append(description)

        _, punishment_fancy, _ = get_punishment_metadata(punishment_type)

        view = Pagination(
            f"ᴘᴜɴɪѕʜᴍᴇɴᴛ {punishment_fancy if punishment_type else ""} ᴍᴏᴅʟᴏɢ ꜰᴏʀ @{member if member else "None"}",
            lines,
            3,
            ctx.author.id,
            True
        )

        await ctx.reply(embed=view.create_embed(), view=view)


async def setup(bot):
    await bot.add_cog(PunishmentCommand(bot))
