import discord
from discord.ext import commands

from backend.core.helper import send_private_dm
from backend.permissions.enforce import has_permission
from backend.punishments.manager import create_punishment, send_punishment_moderation_log, has_permission_to_punish
from backend.punishments.models import PunishmentType


class KickCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @commands.command(name="kick")
    async def _kick(self, ctx, member: discord.Member, *, reason: str = "No reason"):
        """
        Kick a member from the server
        """
        if not await has_permission_to_punish(ctx, member):
            return

        try:
            await member.kick(reason=reason)
        except discord.Forbidden:
            await ctx.send(f"Wasn't able to kick **{member}**. Aborting!")
            return

        punishment = create_punishment(
            ctx.guild.id,
            member.id,
            ctx.author.id,
            PunishmentType.KICK,
            reason
        )

        await ctx.send(f"**@{member}** has been kicked for **{reason}**.")
        sent_dm = await send_private_dm(member, f"You have been kicked from **{ctx.guild.name}** for **{reason}**.",
                                        ctx)

        await send_punishment_moderation_log(
            ctx.guild,
            member,
            ctx.author,
            punishment,
            sent_dm
        )


async def setup(bot):
    await bot.add_cog(KickCommand(bot))
