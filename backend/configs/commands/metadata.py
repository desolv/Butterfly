import discord
from discord.ext import commands

from backend.configs.manager import update_punishment_config, get_punishment_settings
from backend.core.helper import get_sub_commands_help_message, get_utc_now
from backend.guilds.manager import create_or_update_guild


class MetadataCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="metadata",
        invoke_without_command=True
    )
    async def _metadata(self, ctx):
        embed = discord.Embed(
            title="ᴍᴇᴛᴀᴅᴀᴛᴀ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            description=get_sub_commands_help_message(self.bot, "metadata"),
            color=0x393A41,
            timestamp=get_utc_now()
        )

        await ctx.send(embed=embed)

    @_metadata.group(name="punishment")
    async def _punishment(self, ctx):
        pass

    @_punishment.command(name="dump")
    async def _dump(self, ctx):
        try:
            guild, discord_guild = create_or_update_guild(self.bot, ctx.guild.id)

            muted_role, protected_roles, protected_users, logging_channel = get_punishment_settings(ctx.guild.id)

            muted_role = discord_guild.get_role(muted_role)

            protected_roles = " ".join(
                [
                    role.mention
                    for role in (discord_guild.get_role(int(role_id)) for role_id in protected_roles)
                    if role
                ]
            ) or "None"

            protected_users = " ".join(
                [
                    member.mention
                    for member in (discord_guild.get_member(int(member_id)) for member_id in protected_users)
                    if member
                ]
            ) or "None"

            logging_channel = discord_guild.get_channel(logging_channel)

            description = (
                f"**ᴍᴜᴛᴇᴅ ʀᴏʟᴇ**: {muted_role.mention if muted_role else "None"}\n\n"
                f"**ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʀᴏʟᴇѕ**: {protected_roles}\n"
                f"**ᴘʀᴏᴛᴇᴄᴛᴇᴅ ᴜѕᴇʀѕ**: {protected_users}\n\n"
                f"**ʟᴏɢɢɪɴɢ ᴄʜᴀɴɴᴇʟ**: {logging_channel.mention if logging_channel else "None"}\n"
                f"**ʟᴀѕᴛ ᴍᴏᴅɪꜰʏ**: {get_utc_now()}"
            )

            embed = discord.Embed(
                title=f"ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴅᴜᴍᴘ ꜰᴏʀ {discord_guild.name}",
                description=description,
                color=0x393A41,
                timestamp=get_utc_now()
            )

            await ctx.send(embed=embed)
        except Exception as e:
            print(e)

    @_punishment.command(name="muted_role")
    async def _muted_role(
            self,
            ctx,
            role: discord.Role
    ):
        update_punishment_config(ctx.guild.id, muted_role=role.id)
        await ctx.send(f"Updated punishment configuration for **muted_role** to **{role.name}**")


async def setup(bot):
    await bot.add_cog(MetadataCommand(bot))
