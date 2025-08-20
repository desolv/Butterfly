import discord
from discord.ext import commands

from backend.core.helper import get_commands_help_messages, fmt_user
from backend.core.pagination import Pagination
from backend.permissions.enforce import has_permission, has_cooldown
from backend.voice.director import create_or_update_voice_config, create_voice_channel, has_user_existing_voice_channel, \
    mark_voice_closed, get_voice_by_channel


class VoiceCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @commands.group(name="voice", invoke_without_command=True)
    async def _voice(self, ctx):
        view = Pagination(
            "ᴠᴏɪᴄᴇ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_commands_help_messages(self.bot, [VoiceCommand], ctx.author.guild_permissions.administrator),
            3,
            ctx.author.id
        )
        await ctx.reply(embed=view.create_embed(), view=view)

    @has_permission()
    @has_cooldown()
    @_voice.command(name="create")
    async def _create(
            self,
            ctx,
            member: discord.Member
    ):
        """
        Create a permanent voice channel for member
        """
        config = create_or_update_voice_config(member.guild.id)

        owned_channel = has_user_existing_voice_channel(member)
        if owned_channel:
            return await ctx.reply(f"An active voice channel found at {owned_channel.mention} for {member.mention}.")

        try:
            channel = await create_voice_channel(member, config.custom_category_id, False)
        except Exception as e:
            return await ctx.reply(f"Something went wrong while creating the ticket. -> {e}")

        await ctx.reply(f"Created new permanent voice channel at {channel.mention}!")

    @has_permission()
    @has_cooldown()
    @_voice.command(name="delete")
    async def _delete(
            self,
            ctx,
            channel: discord.VoiceChannel
    ):
        """
        Delete a voice channel for member
        """
        voice = get_voice_by_channel(ctx.guild.id, channel.id)
        if not voice:
            return await ctx.reply(f"You may delete only managed voice channels.")

        try:
            await channel.delete()
            mark_voice_closed(channel.id)
        except Exception as e:
            return await ctx.reply(f"Something went wrong while deleting a channel -> {e}")

        await ctx.reply(f"Deleted voice channel of {fmt_user(voice.user_id)}.")


async def setup(bot):
    await bot.add_cog(VoiceCommand(bot))
