from discord.ext import commands


class ErrorDirector(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                "❌ You don’t have permission to do that",
                delete_after=10,
                mention_author=False
            )
            return

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(
                "❌ I’m missing permissions for that action",
                delete_after=10,
                mention_author=False
            )
            return

        if isinstance(error, commands.ChannelNotFound):
            await ctx.reply(
                f"⚠️ Invalid value. {error}",
                delete_after=10,
                mention_author=False
            )
            return

        if isinstance(error, commands.BadArgument):
            await ctx.reply(
                "⚠️ Invalid argument. Check your input and try again",
                delete_after=10,
                mention_author=False
            )
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(
                f"⚠️ Missing argument: `{error.param.name}`",
                delete_after=10,
                mention_author=False
            )
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.reply(
                f"⌛ This command is on cooldown. Try again in {error.retry_after:.1f}s",
                delete_after=10,
                mention_author=False
            )
            return

        if isinstance(error, ValueError):
            await ctx.reply(
                f"⚠️ Invalid value. {error}",
                delete_after=10,
                mention_author=False
            )
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.reply(
                f"⚠️ Something went wrong for some checks. {error}",
                delete_after=10,
                mention_author=False
            )
            return

        print(f"Unhandled exception while '{ctx.command}' -> {error}")
        await ctx.reply(
            f"❌ Something went wrong. Contact an administrator if error persists! -> {error}",
            mention_author=False
        )


async def setup(bot):
    await bot.add_cog(ErrorDirector(bot))
