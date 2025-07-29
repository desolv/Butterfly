from datetime import datetime

import discord
from discord.ext import commands

from core.helper import get_sub_commands_help_message, get_formatted_time
from guilds.manager import get_guild_by_id, create_or_update_guild


class GuildCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="guild",
        invoke_without_command=True
    )
    async def _guild(self, ctx):
        embed = discord.Embed(
            title="ɢᴜɪʟᴅ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            description=get_sub_commands_help_message(self.bot, "guild"),
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        await ctx.send(embed=embed)

    @_guild.command(
        name="info",
        description="Show guild information"
    )
    async def _guild_info(self, ctx, guild_id: int = None):
        create_or_update_guild(guild_id)
        guild_db = get_guild_by_id(guild_id)

        if not guild_db:
            await ctx.send(f"No guild matching **{guild_id}** found!")
            return

        guild = self.bot.get_guild(guild_id)

        description = (
            f"**ᴀᴅᴅᴇᴅ ᴀᴛ**: **{get_formatted_time(guild_db.added_at, format="%d/%m/%y %H:%M %Z")}**\n"
            f"**ᴀᴄᴛɪᴠᴇ**: {'✅' if guild_db.is_active else '❎'}\n"
        )

        if not guild_db.is_active:
            description += (
                f"**ʀᴇᴍᴏᴠᴇᴅ ᴀᴛ**: {get_formatted_time(guild_db.removed_at, format="%d/%m/%y %H:%M %Z")}\n"
            )

        embed = discord.Embed(
            title=f"ɢᴜɪʟᴅ ɪɴꜰᴏ ꜰᴏʀ {guild.name}",
            description=description,
            color=0x393A41,
            timestamp=datetime.utcnow()
        )

        avatar_url = guild.icon.url if guild.icon else "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_thumbnail(url=avatar_url)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(GuildCommand(bot))
