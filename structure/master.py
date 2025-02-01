from discord.ext import commands

from structure.helper import get_time


class MasterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        guild_word = "guild" if len(self.bot.guilds) == 1 else "guilds"
        print(f"Logged in as {self.bot.user} with {len(self.bot.guilds)} {guild_word} at {get_time()}\n")


async def setup(bot):
    await bot.add_cog(MasterCog(bot))
