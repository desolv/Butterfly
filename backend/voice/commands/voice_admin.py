import discord
from discord.ext import commands

from backend.core.helper import get_commands_help_messages, fmt_channel, fmt_roles, format_time_in_zone, fmt_user, \
    get_time_now, fmt_users
from backend.core.pagination import Pagination
from backend.permissions.enforce import has_permission
from backend.voice.director import create_or_update_voice_config
from backend.voice.ui.voice_views import VoiceViews


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
        config = create_or_update_voice_config(ctx.guild.id)

        description = (
            f"**ᴄᴀᴛᴇɢᴏʀʏ ᴄʜᴀɴɴᴇʟ**: {fmt_channel(config.category_id).replace("#", "")}\n"
            f"**ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ**: {fmt_channel(config.join_channel_id)}\n"
            f"**ʟᴏɢɢɪɴɢ ᴄʜᴀɴɴᴇʟ**: {fmt_channel(config.logging_channel_id)}\n\n"

            f"**ѕᴛᴀꜰꜰ ʀᴏʟᴇѕ**: {fmt_roles(config.staff_role_ids)}\n\n"

            f"**ᴇᴍʙᴇᴅ ᴛɪᴛʟᴇ**: {config.embed.get("title")}\n"
            f"**ᴇᴍʙᴇᴅ ᴅᴇѕᴄʀɪᴘᴛɪᴏɴ**: {config.embed.get("description")}\n\n"

            f"**ʙᴀɴɴᴇᴅ ᴜѕᴇʀѕ**: {fmt_users(config.banned_user_ids)}\n"
            f"**ʙᴀɴɴᴇᴅ ʀᴏʟᴇѕ**: {fmt_roles(config.banned_role_ids)}\n"
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
        create_or_update_voice_config(
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
        create_or_update_voice_config(
            ctx.guild.id,
            join_channel_id=channel.id,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **join channel** to {channel.mention}.")

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
        config = create_or_update_voice_config(ctx.guild.id)
        staff_roles = config.staff_role_ids

        if role.id in staff_roles:
            return await ctx.reply(f"Role {role.mention} is present!")

        staff_roles.append(role.id)

        create_or_update_voice_config(
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
        config = create_or_update_voice_config(ctx.guild.id)
        staff_roles = config.staff_role_ids

        if role.id not in staff_roles:
            return await ctx.reply(f"Role {role.mention} is not present!")

        staff_roles.remove(role.id)

        create_or_update_voice_config(
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
        create_or_update_voice_config(
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
        create_or_update_voice_config(
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
        create_or_update_voice_config(
            ctx.guild.id,
            logging_channel_id=channel.id,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **logging channel** to {channel.mention}.")

    @has_permission()
    @_voice_admin.command(name="is_enabled")
    async def _is_enabled(
            self,
            ctx,
            enabled: bool
    ):
        """
        Set the enabled for voice config
        """
        create_or_update_voice_config(
            ctx.guild.id,
            is_enabled=enabled,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **is enabled** to **{enabled}**.")

    @has_permission()
    @_voice_admin.group(name="banned_roles")
    async def _banned_roles(self, ctx):
        pass

    @has_permission()
    @_banned_roles.command(name="add")
    async def _banned_roles_add(
            self,
            ctx,
            role: discord.Role
    ):
        """
        Add a role to voice config banned roles
        """
        config = create_or_update_voice_config(ctx.guild.id)

        banned_roles = config.banned_role_ids

        if role.id in banned_roles:
            return await ctx.reply(f"Role {role.mention} is present!")

        banned_roles.append(role.id)

        create_or_update_voice_config(
            ctx.guild.id,
            banned_role_ids=banned_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **banned roles** by adding {role.mention}.")

    @has_permission()
    @_banned_roles.command(name="remove")
    async def _banned_roles_remove(
            self,
            ctx,
            role: discord.Role
    ):
        """
        Remove a role from voice config banned roles
        """
        config = create_or_update_voice_config(ctx.guild.id)

        banned_roles = config.banned_role_ids

        if role.id not in banned_roles:
            return await ctx.reply(f"Role {role.mention} is not present!")

        banned_roles.remove(role.id)

        create_or_update_voice_config(
            ctx.guild.id,
            banned_role_ids=banned_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **banned roles** by removing {role.mention}.")

    @has_permission()
    @_voice_admin.group(name="banned_users")
    async def _banned_users(self, ctx):
        pass

    @has_permission()
    @_banned_users.command(name="add")
    async def _banned_users_add(
            self,
            ctx,
            member: discord.Member
    ):
        """
        Add a role to voice config banned users
        """
        config = create_or_update_voice_config(ctx.guild.id)

        banned_users = config.banned_user_ids

        if member.id in banned_users:
            return await ctx.reply(f"User {member.mention} is present!")

        banned_users.append(member.id)

        create_or_update_voice_config(
            ctx.guild.id,
            banned_user_ids=banned_users,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **banned users** by adding {role.mention}.")

    @has_permission()
    @_banned_users.command(name="remove")
    async def _banned_users_remove(
            self,
            ctx,
            member: discord.Member
    ):
        """
        Remove a role from voice config banned users
        """
        config = create_or_update_voice_config(ctx.guild.id)

        banned_users = config.banned_user_ids

        if member.id not in banned_users:
            return await ctx.reply(f"User {member.mention} is not present!")

        banned_users.remove(member.id)

        create_or_update_voice_config(
            ctx.guild.id,
            banned_user_ids=banned_users,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated voice config **banned users** by removing {role.mention}.")

    @has_permission()
    @_voice_admin.command(name="send-embed")
    async def _send_embed(self, ctx):
        """
        Post the voice control panel
        """
        config_embed = create_or_update_voice_config(ctx.guild.id).embed

        embed = discord.Embed(
            title=config_embed.get("title"),
            description=config_embed.get("description"),
            color=0x393A41,
            timestamp=get_time_now(),
        )

        await ctx.send(embed=embed, view=VoiceViews())


async def setup(bot):
    await bot.add_cog(VoiceAdminCommand(bot))
