from discord.ext import commands

from backend.core.helper import get_utc_now
from backend.guilds.manager import create_or_update_guild


class GuildEvents(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f"New guild named {guild.name} has added! #{guild.id}")
        create_or_update_guild(guild.id, added_at=get_utc_now(), is_active=True)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        print(f"A guild named {guild.name} left! #{guild.id}")
        create_or_update_guild(guild.id, removed_at=get_utc_now(), is_active=False)


async def setup(bot):
    await bot.add_cog(GuildEvents(bot))
