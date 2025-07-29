from datetime import datetime

import discord
from discord.ext import commands

from backend.core.helper import get_sub_commands_help_message, get_formatted_time
from backend.guilds.manager import get_guild_by_id, create_or_update_guild


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
        try:
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
        except Exception as e:
            print(e)

    @_guild.command(
        name="permissions",
        description="Show the permission config for this guild"
    )
    async def _guild_permissions(self, ctx, guild_id: int = None):
        guild_id = guild_id or ctx.guild.id
        config = get_guild_by_id(guild_id).permissions_config

        if not config:
            await ctx.send("No permission config found.")
            return

        desc = (
            f"**Command**: `{config.command_name}`\n"
            f"**Enabled**: {'✅' if config.is_enabled else '❎'}\n"
            f"**Allowed Roles**: {', '.join(map(str, config.allowed_roles)) or 'None'}\n"
            f"**Blocked Users**: {', '.join(map(str, config.blocked_users)) or 'None'}"
        )

        await ctx.send(embed=discord.Embed(
            title="Permission Config",
            description=desc,
            color=0x2ECC71
        ))

    @_guild.command(
        name="punishments",
        description="Show the punishment config for this guild"
    )
    async def _guild_punishments(self, ctx, guild_id: int = None):
        guild_id = guild_id or ctx.guild.id
        config = get_guild_by_id(guild_id).punishment_config

        if not config:
            await ctx.send("No punishment config found.")
            return

        desc = (
            f"**Muted Role**: <@&{config.muted_role}>\n"
            f"**Exempt Roles**: {', '.join(f'<@&{r}>' for r in config.exempt_roles) or 'None'}\n"
            f"**Exempt Users**: {', '.join(f'<@{u}>' for u in config.exempt_users) or 'None'}\n"
            f"**Mod Channel**: <#{config.moderation_channel}>"
        )

        await ctx.send(embed=discord.Embed(
            title="Punishment Config",
            description=desc,
            color=0xE67E22
        ))

    @_guild.command(
        name="config",
        description="Show all config values for this guild"
    )
    async def _guild_config(self, ctx, guild_id: int = None):
        guild_id = guild_id or ctx.guild.id

        guild_db = get_guild_by_id(guild_id)
        perm = guild_db.permissions_config(guild_id)
        punish = guild_db.punishment_config(guild_id)

        desc = f"**Guild ID**: `{guild_id}`\n"
        desc += f"**Active**: {'✅' if guild_db and guild_db.is_active else '❎'}\n\n"

        desc += "**Permissions:**\n"
        if perm:
            desc += (
                f" - Command: `{perm.command_name}`\n"
                f" - Enabled: {'✅' if perm.is_enabled else '❎'}\n"
            )
        else:
            desc += " - No permission config.\n"

        desc += "\n**Punishments:**\n"
        if punish:
            desc += (
                f" - Muted Role: <@&{punish.muted_role}>\n"
                f" - Mod Channel: <#{punish.moderation_channel}>\n"
            )
        else:
            desc += " - No punishment config.\n"

        await ctx.send(embed=discord.Embed(
            title="Full Guild Configuration",
            description=desc,
            color=0x3498DB
        ))


async def setup(bot):
    await bot.add_cog(GuildCommand(bot))
