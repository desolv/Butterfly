import discord
from discord.ext import commands

from backend.core.helper import get_sub_commands_help_message, format_time_in_zone, get_utc_now, format_duration
from backend.core.pagination import Pagination
from backend.permissions.enforce import has_permission
from backend.punishments.manager import get_punishment_by_id, get_punishment_metadata, process_punishment_removal
from backend.punishments.models import PunishmentType


class PunishmentCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @commands.group(
        name="punishment",
        invoke_without_command=True
    )
    async def _punishment(self, ctx):
        view = Pagination(
            "ᴘᴜɴɪѕʜᴍᴇɴᴛ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_sub_commands_help_message(self.bot, "punishment"),
            3,
            ctx.author.id
        )

        await ctx.send(embed=view.create_embed(), view=view)

    @has_permission()
    @_punishment.command(name="view")
    async def _punishment_view(self, ctx, punishment_id: int):
        """
        Display detailed information about a specific punishment by ID
        :param ctx:
        :param punishment_id:
        :return:
        """
        punishment = get_punishment_by_id(ctx.guild.id, punishment_id)

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
        added_at_time = format_time_in_zone(punishment.added_at, format="%d/%m/%y %H:%M %Z")

        description = (
            f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ɪᴅ**: **{punishment_id}**\n"
            f"**ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴛʏᴘᴇ**: **{punishment_name}**\n\n"
            f"**ᴀᴅᴅᴇᴅ ʙʏ**: {punishment.added_by if not added_by else added_by.mention}\n"
            f"**ᴀᴅᴅᴇᴅ ᴀᴛ**: **{added_at_time}**\n"
            f"**ᴀᴅᴅᴇᴅ ʀᴇᴀѕᴏɴ**: {punishment.reason}\n"
        )

        if punishment.type is PunishmentType.MUTE or punishment.type is PunishmentType.BAN:
            try:
                expires_at_time = format_duration(punishment.added_at, punishment.expires_at)
                description += (
                    f"**ᴅᴜʀᴀᴛɪᴏɴ**: **{expires_at_time}**\n"
                )
            except Exception as e:
                print(e)
            if not punishment.is_active:
                try:
                    removed_by = await self.bot.fetch_user(punishment.removed_by)
                except Exception:
                    removed_by = None

                description += (
                    f"\n**ʀᴇᴍᴏᴠᴇᴅ ʙʏ**: {self.bot.user.mention if removed_by is None else removed_by.mention}\n"
                    f"**ʀᴇᴍᴏᴠᴇᴅ ᴀᴛ**: **{format_time_in_zone(punishment.removed_at, format="%d/%m/%y %H:%M %Z")}**\n"
                    f"**ʀᴇᴍᴏᴠᴇᴅ ʀᴇᴀѕᴏɴ**: {punishment.removed_reason}"
                )

        embed = discord.Embed(
            title=f"ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ ꜰᴏʀ @{punishment.user_id if not member else member}",
            description=description,
            color=punishment_color,
            timestamp=get_utc_now()
        )

        avatar_url = member.avatar.url if member.avatar is not None else "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_thumbnail(url=avatar_url)

        await ctx.send(embed=embed)

    @has_permission()
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
        :param ctx:
        :param punishment_id:
        :param reason:
        :return:
        """
        punishment = get_punishment_by_id(ctx.guild.id, punishment_id)

        if not punishment:
            await ctx.send(f"No punishment matching **{punishment_id}** found!")
            return

        if not punishment.is_active:
            await ctx.send(f"Punishment type is **not active**!")
            return

        guild = ctx.guild

        await process_punishment_removal(
            self.bot,
            guild,
            punishment,
            ctx.author,
            reason
        )

        member = guild.get_member(punishment.user_id)

        await ctx.send(
            f"**@{member if member else punishment.user_id}**'s punishment **#{punishment.punishment_id}** has been removed for **{reason}**.")


async def setup(bot):
    await bot.add_cog(PunishmentCommand(bot))
