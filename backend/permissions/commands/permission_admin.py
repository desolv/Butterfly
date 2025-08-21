import discord
from discord.ext import commands

from backend.core.helper import get_time_now, format_time_in_zone, get_commands_help_messages, fmt_roles, fmt_user
from backend.core.pagination import Pagination
from backend.errors.custom_errors import CommandNotFound
from backend.permissions.director import create_or_retrieve_command, get_permissions_for_guild
from backend.permissions.enforce import has_permission


class PermissionAdminCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @commands.group(name="permission-admin", invoke_without_command=True)
    async def _permission_admin(self, ctx):
        view = Pagination(
            "ᴘᴇʀᴍɪѕѕɪᴏɴ ᴀᴅᴍɪɴ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_commands_help_messages(self.bot, [PermissionAdminCommand], ctx.author.guild_permissions.administrator),
            3,
            ctx.author.id
        )

        await ctx.reply(embed=view.create_embed(), view=view)

    @has_permission()
    @_permission_admin.command(name="view")
    async def _view(
            self,
            ctx,
            *,
            command_name: str
    ):
        """
        Display the current command information
        """
        permission = create_or_retrieve_command(self.bot, ctx.guild.id, command_name)

        if not permission:
            raise commands.ChannelNotFound

        description = (
            f"**ᴀᴅᴍɪɴ**: {'✅' if permission.is_admin else '❎'}\n"
            f"**ʀᴇǫᴜɪʀᴇᴅ ʀᴏʟᴇѕ**: {fmt_roles(permission.required_role_ids)}\n"
            f"**ᴄᴏᴏʟᴅᴏᴡɴ**: **{permission.command_cooldown}s**\n"
            f"**ᴇɴᴀʙʟᴇᴅ**: {'✅' if permission.is_enabled else '❎'}\n"
            f"**ᴀᴅᴅᴇᴅ ᴀᴛ**: {format_time_in_zone(permission.added_at)}\n"
        )

        embed = discord.Embed(
            title=f"**{permission.command_name}** ᴄᴏᴍᴍᴀɴᴅ",
            description=description,
            color=0x393A41,
            timestamp=get_time_now()
        )

        embed.add_field(name="**ᴜᴘᴅᴀᴛᴇᴅ ᴀᴛ**", value=f"{format_time_in_zone(permission.updated_at)}",
                        inline=True)
        embed.add_field(name="**ᴜᴘᴅᴀᴛᴇᴅ ʙʏ**", value=f"{fmt_user(permission.updated_by)}", inline=True)

        await ctx.reply(embed=embed)

    @has_permission()
    @_permission_admin.command(name="manifest")
    async def _manifest(self, ctx):
        """
        Display the current commands permissions
        """
        permissions = get_permissions_for_guild(self.bot, ctx.guild.id)

        lines: list[str] = []
        for permission in permissions:
            lines.append(
                f"**{permission.command_name}**\n"
                f"**ᴀᴅᴍɪɴ**: {'✅' if permission.is_admin else '❎'}\n"
                f"**ʀᴇǫᴜɪʀᴇᴅ ʀᴏʟᴇѕ**: {fmt_roles(permission.required_role_ids)}\n"
                f"**ᴄᴏᴏʟᴅᴏᴡɴ**: **{permission.command_cooldown}s**\n"
                f"**ᴇɴᴀʙʟᴇᴅ**: {'✅' if permission.is_enabled else '❎'}\n"
            )

        view = Pagination(
            f"ᴘᴇʀᴍɪѕѕɪᴏɴ ᴍᴀɴɪꜰᴇѕᴛ",
            lines,
            3,
            ctx.author.id,
            True
        )

        await ctx.reply(embed=view.create_embed(), view=view)

    @has_permission()
    @_permission_admin.command(name="is_admin")
    async def _is_admin(
            self,
            ctx,
            command_name: str,
            is_admin: bool
    ):
        """
        Set the admin only for commands
        """
        permission = create_or_retrieve_command(
            self.bot,
            ctx.guild.id,
            command_name,
            is_admin=is_admin,
            updated_by=ctx.author.id
        )

        if not permission:
            raise commands.ChannelNotFound

        await ctx.reply(
            f"Updated **{permission.command_name}** command **is_admin** permission to **{permission.is_admin}**.")

    @has_permission()
    @_permission_admin.command(name="is_enabled")
    async def _is_enabled(
            self,
            ctx,
            command_name: str,
            is_enabled: bool
    ):
        """
        Set the enabled for commands
        """
        permission = create_or_retrieve_command(
            self.bot,
            ctx.guild.id,
            command_name,
            is_enabled=is_enabled,
            updated_by=ctx.author.id
        )

        if not permission:
            raise commands.ChannelNotFound

        await ctx.reply(
            f"Updated **{permission.command_name}** command **is_enabled** permission to **{permission.is_enabled}**.")

    @has_permission()
    @_permission_admin.command(name="cooldown")
    async def _cooldown(
            self,
            ctx,
            command_name: str,
            seconds: int
    ):
        """
        Set the cooldown for commands
        """
        if seconds > 600 or seconds < 0:
            return await ctx.reply(f"Seconds must be between 0-600!")

        permission = create_or_retrieve_command(
            self.bot,
            ctx.guild.id,
            command_name,
            command_cooldown=seconds,
            updated_by=ctx.author.id
        )

        if not permission:
            raise commands.ChannelNotFound

        await ctx.reply(
            f"Updated **{permission.command_name}** command **cooldown** permission to **{seconds}s**.")

    @has_permission()
    @_permission_admin.group(name="required_roles")
    async def _required_roles(self, ctx):
        pass

    @has_permission()
    @_required_roles.command(name="add")
    async def _required_roles_add(
            self,
            ctx,
            command_name: str,
            role: discord.Role,
    ):
        """
        Add a role to permissions allowed roles
        """
        permission = create_or_retrieve_command(
            self.bot,
            ctx.guild.id,
            command_name
        )

        if not permission:
            raise commands.ChannelNotFound

        required_roles = permission.required_role_ids

        if role.id in required_roles:
            return await ctx.reply(f"Role {role.mention} is present!")

        required_roles.append(role.id)

        create_or_retrieve_command(
            self.bot,
            ctx.guild.id,
            command_name,
            required_role_ids=required_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(
            f"Updated **{permission.command_name}** command **required_roles** permission by adding {role.mention}.")

    @has_permission()
    @_required_roles.command(name="remove")
    async def _required_roles_remove(
            self,
            ctx,
            command_name: str,
            role: discord.Role
    ):
        """
        Remove a role from permissions allowed roles
        """
        permission = create_or_retrieve_command(
            self.bot,
            ctx.guild.id,
            command_name
        )

        if not permission:
            raise commands.ChannelNotFound

        required_roles = permission.required_role_ids

        if role.id not in required_roles:
            return await ctx.reply(f"Role {role.mention} is not present!")

        required_roles.remove(role.id)

        create_or_retrieve_command(
            self.bot,
            ctx.guild.id,
            command_name,
            required_role_ids=required_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(
            f"Updated **{permission.command_name}** command **required_roles** permission by removing {role.mention}.")

    @has_permission()
    @_required_roles.command(name="everyone")
    async def _required_roles_everyone(
            self,
            ctx,
            command_name: str,
            allow: bool
    ):
        """
        Allow everyone in this guild to run the command
        """
        permission = create_or_retrieve_command(
            self.bot,
            ctx.guild.id,
            command_name
        )

        if not permission:
            raise commands.ChannelNotFound

        if permission.is_admin:
            return await ctx.reply("This command is admin-only. Disable admin-only first.")

        required_roles = permission.required_role_ids
        guild_id = ctx.guild.id

        if allow:
            if guild_id in required_roles:
                return await ctx.reply(f"Role **everyone** is present!")

            required_roles.append(guild_id)
        else:
            if guild_id not in required_roles:
                return await ctx.reply(f"Role **everyone** is not present!")

            required_roles.remove(guild_id)

        create_or_retrieve_command(
            self.bot,
            guild_id,
            command_name,
            required_role_ids=required_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(
            f"Updated **{permission.command_name}** command **required_roles** permission by {"allowing" if allow else "restricting"} everyone.")


async def setup(bot):
    await bot.add_cog(PermissionAdminCommand(bot))
