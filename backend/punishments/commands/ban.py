import discord
from discord.ext import commands

from backend.core.helper import parse_time_window, send_private_dm
from backend.permissions.enforce import has_permission, has_cooldown
from backend.punishments.director import has_permission_to_punish, get_user_active_punishment, create_punishment, \
    send_punishment_moderation_log
from backend.punishments.models.punishment import PunishmentType


class BanCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @has_cooldown()
    @commands.command(name="ban")
    async def _ban(self, ctx, member: discord.Member, duration: str = "1h", *, reason: str = "No reason"):
        """
        Ban a member by removing them from the server
        """
        if not await has_permission_to_punish(ctx, member):
            return

        if get_user_active_punishment(ctx.guild.id, member.id, PunishmentType.BAN):
            await ctx.reply(f"**@{member}** is already banned!")
            return

        permanent = True if duration.lower() in ("permanent", "perm") else False

        if not permanent:
            parse_duration = parse_time_window(duration)

        try:
            await member.ban(reason=reason)
        except discord.Forbidden:
            await ctx.reply(f"Wasn't able to ban **{member}**. Aborting!")
            return

        punishment = create_punishment(
            ctx.guild.id,
            member.id,
            ctx.author.id,
            PunishmentType.BAN,
            reason,
            None if permanent else parse_duration
        )

        duration_msg = "permanently" if permanent else "temporarily"
        await ctx.reply(f"**@{member}** has been {duration_msg} banned for **{reason}**.")

        expiring = "**never** expiring!" if permanent else f"expiring in **{duration}**."
        sent_dm = await send_private_dm(member,
                                        f"You have been banned from **{ctx.guild.name}** for **{reason}** it's {expiring}",
                                        ctx)

        await send_punishment_moderation_log(
            ctx.guild,
            member,
            ctx.author,
            punishment,
            sent_dm,
            duration
        )


async def setup(bot):
    await bot.add_cog(BanCommand(bot))
