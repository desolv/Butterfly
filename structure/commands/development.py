import platform
import sys

import psutil
from discord.ext import commands

from structure.providers.helper import get_time, get_uptime
from structure.providers.preconditions import is_owner


class DevelopmentCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @is_owner()
    @commands.command(
        name="shutdown",
        description="Terminate robot activity",
        aliases=['stop'],
        hidden=True
    )
    async def _shutdown(self, ctx):
        """
        Terminate robot activity
        :param none:
        """
        await ctx.send(f"Paramount shutdown at **{get_time()}**!")
        print(f"Paramount shutdown called by {ctx.message.author} at {get_time()}!")
        await self.bot.close()
        sys.exit(0)

    @is_owner()
    @commands.command(
        name="debug",
        description="Displays bot runtime information.",
        hidden=True
    )
    async def _debug(self, ctx):
        """
        Displays robot runtime details
        :param none:
        """
        latency = round(self.bot.latency * 1000, 2)
        loaded_cogs = ", ".join(self.bot.extensions.keys()) or "None"
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024

        await ctx.send(f"- Latency -> {latency}ms\n"
                       f"- Loaded Cogs -> {loaded_cogs}\n"
                       f"- Running on Python {platform.python_version()}\n"
                       f"Paramount memory usage at **{memory_usage:.2f} MB**")

    @is_owner()
    @commands.command(
        name="load",
        description="Loads a cog",
        hidden=True
    )
    async def _load(self, ctx, cog: str):
        """
        Loads a specific cog
        :param cog: Cog that needs to be loaded
        """
        try:
            await self.bot.load_extension(f"structure.{cog}")
            await ctx.send(f"Successfully loaded `{cog}` cog")
        except Exception as e:
            await ctx.send(f"Failed to load '{cog}' cog -> {e}")

    @is_owner()
    @commands.command(
        name="unload",
        description="Unloads a cog",
        hidden=True
    )
    async def _unload(self, ctx, cog: str):
        """
        Unloads a specific cog
        :param cog: Cog that needs to be unloaded
        """
        try:
            await self.bot.unload_extension(f"structure.{cog}")
            await ctx.send(f"Successfully unloaded `{cog}` cog")
        except Exception as e:
            await ctx.send(f"Failed to unload '{cog}' cog -> {e}")

    @is_owner()
    @commands.command(
        name="reload",
        description="Reloads a cog or all cogs",
        hidden=True
    )
    async def _reload(self, ctx, cog: str = None):
        """
        Reloads all cogs if None
        :param cog: Cog that needs to be reloaded
        """
        if cog is None:
            reloaded_cogs = []
            for ext in list(self.bot.extensions.keys()):
                await self.bot.reload_extension(ext)
                reloaded_cogs.append(ext)

            await ctx.send(f"Reloaded all cogs -> {', '.join(reloaded_cogs)}")
            return

        try:
            await self.bot.reload_extension(f"structure.{cog}")
            await ctx.send(f"Successfully reloaded '{cog}' cog")
        except Exception as e:
            await ctx.send(f"Failed to reload '{cog}' cog -> {e}")

    @is_owner()
    @commands.command(
        name="uptime",
        description="Shows robot uptime",
        hidden=True
    )
    async def _uptime(self, ctx):
        """
        Displays robot uptime since last restart
        :param none:
        """
        await ctx.send(f"Paramount initialised at **{get_uptime(self.bot)}**!")


async def setup(bot):
    await bot.add_cog(DevelopmentCommandCog(bot))
