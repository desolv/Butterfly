import discord
from discord.ext import commands

from backend.core.helper import get_time_now, format_time_in_zone, get_commands_help_messages, fmt_roles
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
            raise CommandNotFound(command_name)

        description = (
            f"**ᴀᴅᴍɪɴ**: {'✅' if permission.is_admin else '❎'}\n"
            f"**ʀᴇǫᴜɪʀᴇᴅ ʀᴏʟᴇѕ**: {fmt_roles(permission.required_role_ids)}\n"
            f"**ᴄᴏᴏʟᴅᴏᴡɴ**: **{permission.command_cooldown}s**\n\n"
            f"**ᴇɴᴀʙʟᴇᴅ**: {'✅' if permission.is_enabled else '❎'}\n"
        )

        embed = discord.Embed(
            title=f"**{permission.command_name}** ᴄᴏᴍᴍᴀɴᴅ",
            description=description,
            color=0x393A41,
            timestamp=get_time_now()
        )

        embed.add_field(name="**ᴀᴅᴅᴇᴅ ᴀᴛ**",
                        value=f"{format_time_in_zone(permission.added_at)}", inline=True)
        embed.add_field(name="**ɢᴜɪʟᴅ ɪᴅ**", value=f"{ctx.guild.id}", inline=True)

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
            f"ᴘᴇʀᴍɪѕѕɪᴏɴ ᴍᴀɴɪꜰᴇѕᴛ ꜰᴏʀ {ctx.guild.name}",
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
            is_admin=is_admin
        )

        if not permission:
            raise CommandNotFound(command_name)

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
            is_enabled=is_enabled
        )

        if not permission:
            raise CommandNotFound(command_name)

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
            command_cooldown=seconds
        )

        if not permission:
            raise CommandNotFound(command_name)

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
            raise CommandNotFound(command_name)

        if role.id in permission.required_role_ids:
            return await ctx.reply(f"Role {role.mention} is present!")

        permission.required_role_ids.append(role.id)

        create_or_retrieve_command(
            self.bot,
            ctx.guild.id,
            command_name,
            required_role_ids=permission.required_role_ids
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
            raise CommandNotFound(command_name)

        if role.id not in permission.required_role_ids:
            return await ctx.reply(f"Role {role.mention} is not present!")

        permission.required_role_ids.remove(role.id)

        create_or_retrieve_command(
            self.bot,
            ctx.guild.id,
            command_name,
            required_role_ids=permission.required_role_ids
        )

        await ctx.reply(
            f"Updated **{permission.command_name}** command **required_roles** permission by removing {role.mention}.")


async def setup(bot):
    await bot.add_cog(PermissionAdminCommand(bot))
