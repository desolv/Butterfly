from discord.ext import commands

from backend.errors.logging import log_error


class Errors(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("❌ You don’t have permission to do that", delete_after=10)
            return

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.reply("❌ I’m missing permissions for that action", delete_after=10)
            return

        if isinstance(error, commands.ChannelNotFound):
            await ctx.reply(f"⚠️ {error}", delete_after=10)
            return

        if isinstance(error, commands.BadArgument):
            await ctx.reply("⚠️ Invalid argument. Check your input and try again", delete_after=10)
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"⚠️ Missing argument: `{error.param.name}`", delete_after=10)
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(f"⌛ This command is on cooldown. Try again in {error.retry_after:.1f}s", delete_after=10)
            return

        if isinstance(error, ValueError):
            await ctx.reply(f"⚠️ Invalid value. {error}", delete_after=10)
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.reply(f"⚠️ Something went wrong for some checks. {error}", delete_after=10)
            return

        await ctx.reply(f"❌ Something went wrong. Contact an administrator!", delete_after=15)
        log_error(
            ctx.guild.id if ctx.guild else None,
            error,
            f"Command: {ctx.command}, User: {ctx.author}"
        )


async def setup(bot):
    await bot.add_cog(Errors(bot))
