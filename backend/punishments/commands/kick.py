import discord
from discord.ext import commands

from backend.core.helper import send_private_dm, is_valid_url
from backend.permissions.enforce import has_permission, has_cooldown
from backend.punishments.director import create_punishment, send_punishment_moderation_log, has_permission_to_punish
from backend.punishments.models.punishment import PunishmentType


class KickCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @has_cooldown()
    @commands.command(name="kick")
    async def _kick(
            self,
            ctx,
            member: discord.Member,
            evidence_url: str,
            *,
            reason: str = "No reason"
    ):
        """
        Kick a member from the server
        """
        if not await has_permission_to_punish(ctx, member):
            return

        if not is_valid_url(evidence_url):
            return await ctx.reply(f"Invalid url entered. Please make sure it includes **http/https**!")

        try:
            await member.kick(reason=reason)
        except discord.Forbidden:
            return await ctx.reply(f"Wasn't able to kick **{member}**. Aborting!")

        punishment = create_punishment(
            ctx.guild.id,
            member.id,
            ctx.author.id,
            PunishmentType.KICK,
            evidence_url,
            reason
        )

        await ctx.reply(f"**@{member}** has been kicked for **{reason}**")
        sent_dm = await send_private_dm(member, f"You have been kicked from **{ctx.guild.name}** for **{reason}**",
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
