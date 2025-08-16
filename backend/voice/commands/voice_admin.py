import discord
from discord.ext import commands

from backend.core.helper import get_commands_help_messages, fmt_channel, fmt_roles, format_time_in_zone, fmt_user, \
    get_time_now
from backend.core.pagination import Pagination
from backend.permissions.enforce import has_permission
from backend.voice.director import update_or_retrieve_voice_config


class VoiceAdminCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @commands.group(name="voice-admin", invoke_without_command=True)
    async def _voice_admin(self, ctx):
        view = Pagination(
            "ᴠᴏɪᴄᴇ ᴀᴅᴍɪɴ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_commands_help_messages(self.bot, [VoiceAdminCommand], ctx.author.guild_permissions.administrator),
            3,
            ctx.author.id
        )

        await ctx.reply(embed=view.create_embed(), view=view)

    @has_permission()
    @_voice_admin.command(name="manifest")
    async def _manifest(self, ctx):
        """
        Display the voice config
        """
        config = update_or_retrieve_voice_config(ctx.guild.id)

        description = (
            f"**ᴄᴀᴛᴇɢᴏʀʏ ᴄʜᴀɴɴᴇʟ**: {fmt_channel(config.category_id)}\n"
            f"**ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ**: {fmt_channel(config.join_channel_id)}\n"
            f"**ᴄᴏᴍᴍᴀɴᴅ ᴄʜᴀɴɴᴇʟ**: {fmt_channel(config.command_channel_id)}\n"
            f"**ѕᴛᴀꜰꜰ ʀᴏʟᴇѕ**: {fmt_roles(config.staff_role_ids)}\n\n"

            f"**ᴇᴍʙᴇᴅ ᴛɪᴛʟᴇ**: {config.embed.get("title")}\n"
            f"**ᴇᴍʙᴇᴅ ᴅᴇѕᴄʀɪᴘᴛɪᴏɴ**: {config.embed.get("description")}\n\n"

            f"**ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴀꜰᴛᴇʀ**: {config.auto_delete_after}\n"
            f"**ʟᴏɢɢɪɴɢ ᴄʜᴀɴɴᴇʟ**: {fmt_channel(config.logging_channel_id)}\n"
        )

        embed = discord.Embed(
            title=f"ᴠᴏɪᴄᴇ ᴄᴏɴꜰɪɢ ᴍᴀɴɪꜰᴇѕᴛ",
            description=description,
            color=0x393A41,
            timestamp=get_time_now()
        )

        embed.add_field(name="**ᴜᴘᴅᴀᴛᴇᴅ ᴀᴛ**", value=format_time_in_zone(config.updated_at), inline=True)
        embed.add_field(name="**ᴜᴘᴅᴀᴛᴇᴅ ʙʏ**", value=fmt_user(config.updated_by), inline=True)

        await ctx.reply(embed=embed)

    @has_permission()
    @_voice_admin.command(name="category_id")
    async def _category_id(
            self,
            ctx,
            channel: discord.CategoryChannel
    ):
        """
        Set the category id for voice config
        """
        update_or_retrieve_voice_config(
            ctx.guild.id,
            category_id=channel.id,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **category id** to **{channel.name}**.")

    @has_permission()
    @_voice_admin.command(name="join_channel")
    async def _join_channel(
            self,
            ctx,
            channel: discord.VoiceChannel
    ):
        """
        Set the join channel for voice config
        """
        update_or_retrieve_voice_config(
            ctx.guild.id,
            join_channel_id=channel.id,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **join channel** to **{channel.name}**.")

    @has_permission()
    @_voice_admin.command(name="command_channel")
    async def _command_channel(
            self,
            ctx,
            channel: discord.TextChannel
    ):
        """
        Set the command channel for voice config
        """
        update_or_retrieve_voice_config(
            ctx.guild.id,
            command_channel_id=channel.id,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **command channel** to **{channel.name}**.")

    @has_permission()
    @_voice_admin.group(name="staff_roles")
    async def _staff_roles(self, ctx):
        pass

    @has_permission()
    @_staff_roles.command(name="add")
    async def _staff_roles_add(
            self,
            ctx,
            role: discord.Role
    ):
        """
        Add a role to voice config staff roles
        """
        config = update_or_retrieve_voice_config(ctx.guild.id)
        staff_roles = config.staff_role_ids

        if role.id in staff_roles:
            return await ctx.reply(f"Role {role.mention} is present!")

        staff_roles.append(role.id)

        update_or_retrieve_voice_config(
            ctx.guild.id,
            staff_role_ids=staff_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **staff roles** by adding {role.mention}.")

    @has_permission()
    @_staff_roles.command(name="remove")
    async def _staff_roles_remove(
            self,
            ctx,
            role: discord.Role
    ):
        """
        Remove a role from voice config staff roles
        """
        config = update_or_retrieve_voice_config(ctx.guild.id)
        staff_roles = config.staff_role_ids

        if role.id not in staff_roles:
            return await ctx.reply(f"Role {role.mention} is not present!")

        staff_roles.remove(role.id)

        update_or_retrieve_voice_config(
            ctx.guild.id,
            staff_role_ids=staff_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **staff roles** by removing {role.mention}.")

    @has_permission()
    @_voice_admin.group(name="embed")
    async def _embed(self, ctx):
        pass

    @has_permission()
    @_embed.command(name="title")
    async def _embed_title(
            self,
            ctx,
            *,
            title: str
    ):
        """
        Set the embed title for voice config
        """
        update_or_retrieve_voice_config(
            ctx.guild.id,
            embed_title=title,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **embed title** to **{title}**.")

    @has_permission()
    @_embed.command(name="description")
    async def _embed_description(
            self,
            ctx,
            *,
            description: str
    ):
        """
        Set the embed description for voice config
        """
        update_or_retrieve_voice_config(
            ctx.guild.id,
            embed_description=description,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **embed description** to **{description}**.")

    @has_permission()
    @_voice_admin.command(name="logging_channel")
    async def _logging_channel(
            self,
            ctx,
            channel: discord.TextChannel
    ):
        """
        Set the logging channel for voice config
        """
        update_or_retrieve_voice_config(
            ctx.guild.id,
            logging_channel_id=channel.id,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **logging channel** to **{channel.name}**.")

    @has_permission()
    @_voice_admin.command(name="auto_delete_after")
    async def _auto_delete_after(
            self,
            ctx,
            seconds: int
    ):
        """
        Set the auto delete for voice config
        """
        if seconds > 1800 or seconds < 120:
            return await ctx.reply(f"Seconds must be between 120-1800!")

        update_or_retrieve_voice_config(
            ctx.guild.id,
            auto_delete_after=seconds,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **auto delete after** to **{seconds}s**.")


async def setup(bot):
    await bot.add_cog(VoiceAdminCommand(bot))
