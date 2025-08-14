from discord.ext import commands

from backend.core.helper import get_time_now, get_current_time
from backend.guilds.director import create_or_update_guild


class GuildEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user} with {len(self.bot.guilds)} guild(s) at {get_current_time()}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"New guild named {guild.name} has been added! #{guild.id}")

        create_or_update_guild(
            self.bot,
            guild.id,
            added_at=get_time_now(),
            is_active=True
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(f"A guild named {guild.name} has left! #{guild.id}")

        create_or_update_guild(
            self.bot,
            guild.id,
            removed_at=get_time_now(),
            is_active=False
        )


async def setup(bot):
    await bot.add_cog(GuildEvents(bot))
