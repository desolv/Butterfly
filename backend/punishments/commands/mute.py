import discord
from discord.ext import commands

from backend.configs.manager import get_punishment_settings
from backend.core.helper import parse_time_window, send_private_dm
from backend.permissions.enforce import has_permission
from backend.punishments.manager import has_permission_to_punish, get_user_active_punishment, create_punishment, \
    send_punishment_moderation_log
from backend.punishments.models import PunishmentType


class MuteCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @commands.command(name="mute")
    async def _mute(self, ctx, member: discord.Member, duration: str = "1h", *, reason: str = "No reason"):
        """Mute a member by giving them a role"""

        if not await has_permission_to_punish(ctx, member):
            return

        if get_user_active_punishment(ctx.guild.id, member.id, PunishmentType.MUTE):
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
            muted_role, _, _, _, _ = get_punishment_settings(ctx.guild.id)
            muted_role = ctx.guild.get_role(muted_role)
            await member.add_roles(muted_role, reason=reason)
        except discord.Forbidden:
            await ctx.send(f"Wasn't able to add mute to **{member}**. Aborting!")
            return

        punishment = create_punishment(
            ctx.guild.id,
            member.id,
            ctx.author.id,
            PunishmentType.MUTE,
            reason,
            None if permanent else parse_duration
        )

        duration_msg = "permanently" if permanent else "temporarily"
        await ctx.send(f"**@{member}** has been {duration_msg} muted for **{reason}**.")

        expiring = "**never** expiring!" if permanent else f"expiring in **{duration}**."
        sent_dm = await send_private_dm(member,
                                        f"You have been muted from **{ctx.guild.name}** for **{reason}** it's {expiring}",
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
    await bot.add_cog(MuteCommand(bot))
