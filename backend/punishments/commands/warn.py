import discord
from discord.ext import commands

from backend.core.helper import send_private_dm
from backend.permissions.enforce import has_permission, has_cooldown
from backend.punishments.director import has_permission_to_punish, create_punishment, send_punishment_moderation_log
from backend.punishments.models import PunishmentType


class WarnCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @has_cooldown()
    @commands.command(name="warn")
    async def _warn(self, ctx, member: discord.Member, *, reason: str = "No reason"):
        """
        Warn a member via sending a private message
        """
        if not await has_permission_to_punish(ctx, member):
            return

        punishment = create_punishment(
            ctx.guild.id,
            member.id,
            ctx.author.id,
            PunishmentType.WARN,
            reason
        )

        await ctx.send(f"**@{member}** has been warned for **{reason}**.")
        sent_dm = await send_private_dm(member, f"You have been warned from **{ctx.guild.name}** for **{reason}**.",
                                        ctx)

        await send_punishment_moderation_log(
            ctx.guild,
            member,
            ctx.author,
            punishment,
            sent_dm
        )


async def setup(bot):
    await bot.add_cog(WarnCommand(bot))
