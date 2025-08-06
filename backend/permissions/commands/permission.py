import discord
from discord.ext import commands

from backend.core.helper import get_sub_commands_help_message, get_utc_now, get_formatted_time
from backend.core.pagination import Pagination
from backend.permissions.enforce import has_permission
from backend.permissions.manager import create_or_retrieve_command, get_permissions_for_guild


class PermissionCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @commands.group(
        name="permission",
        invoke_without_command=True
    )
    async def _permission(self, ctx):
        view = Pagination(
            "ᴘᴇʀᴍɪѕѕɪᴏɴ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_sub_commands_help_message(self.bot, "permission"),
            3,
            ctx.author.id
        )

        await ctx.send(embed=view.create_embed(), view=view)

    @has_permission()
    @_permission.command(name="view")
    async def _view(
            self,
            ctx,
            *,
            command_name: str
    ):
        """Display the current command information."""

        guild = ctx.guild
        command_name = command_name.lower()

        permission = create_or_retrieve_command(self.bot, guild.id, command_name)

        if not permission:
            return await ctx.send(f"No command **{command_name}** has been found!")

        allowed_roles = " ".join(
            [
                role.mention
                for role in (guild.get_role(int(role_id)) for role_id in permission.allowed_roles)
                if role
            ]
        ) or "None"

        description = (
            f"**ᴀᴅᴍɪɴ**: {'✅' if permission.is_admin else '❎'}\n"
            f"**ᴀʟʟᴏᴡᴇᴅ ʀᴏʟᴇѕ**: {allowed_roles}\n\n"
            f"**ᴇɴᴀʙʟᴇᴅ**: {'✅' if permission.is_enabled else '❎'}\n"
        )

        embed = discord.Embed(
            title=f"**{permission.command_name}** ᴄᴏᴍᴍᴀɴᴅ",
            description=description,
            color=0x393A41,
            timestamp=get_utc_now()
        )

        embed.add_field(name="**ᴀᴅᴅᴇᴅ ᴀᴛ**",
                        value=f"{get_formatted_time(permission.added_at, format="%d/%m/%y %H:%M %Z")}", inline=True)
        embed.add_field(name="**ɢᴜɪʟᴅ ɪᴅ**", value=f"{guild.id}", inline=True)

        await ctx.send(embed=embed)

    @has_permission()
    @_permission.command(name="catalog")
    async def _catalog(self, ctx):
        """Display the current commands loaded to the server."""

        permissions = get_permissions_for_guild(self.bot, ctx.guild.id)

        lines: list[str] = []
        for permission in permissions:
            allowed_roles = " ".join(
                [
                    role.mention
                    for role in (ctx.guild.get_role(int(role_id)) for role_id in permission.allowed_roles)
                    if role
                ]
            ) or "None"

            lines.append(
                f"**{permission.command_name}**\n"
                f"**ᴀᴅᴍɪɴ**: {'✅' if permission.is_admin else '❎'}\n"
                f"**ᴀʟʟᴏᴡᴇᴅ ʀᴏʟᴇѕ**: {allowed_roles}\n"
                f"**ᴇɴᴀʙʟᴇᴅ**: {'✅' if permission.is_enabled else '❎'}\n"
            )

        view = Pagination(
            f"ᴘᴇʀᴍɪѕѕɪᴏɴ ᴄᴀᴛᴀʟᴏɢ ꜰᴏʀ {ctx.guild.name}",
            lines,
            3,
            ctx.author.id
        )

        await ctx.send(embed=view.create_embed(), view=view)

    @has_permission()
    @_permission.command(name="is_admin")
    async def _is_admin(
            self,
            ctx,
            is_admin: bool,
            *,
            command_name: str
    ):
        """Set the admin only for commands"""

        guild = ctx.guild
        command_name = command_name.lower()

        permission = create_or_retrieve_command(
            self.bot,
            guild.id,
            command_name,
            is_admin=is_admin
        )

        if not permission:
            return await ctx.send(f"No command **{command_name}** has been found!")

        await ctx.send(
            f"Updated permission **is admin** for **{permission.command_name}** command to **{permission.is_admin}**")

    @has_permission()
    @_permission.command(name="is_enabled")
    async def _is_enabled(
            self,
            ctx,
            is_enabled: bool,
            *,
            command_name: str
    ):
        """Set the enabled for commands"""

        guild = ctx.guild
        command_name = command_name.lower()

        permission = create_or_retrieve_command(
            self.bot,
            guild.id,
            command_name,
            is_enabled=is_enabled
        )

        if not permission:
            return await ctx.send(f"No command **{command_name}** has been found!")

        await ctx.send(
            f"Updated permission **is enabled** for **{permission.command_name}** command to **{permission.is_enabled}**")

    @has_permission()
    @_permission.group(name="allowed_roles")
    async def _allowed_roles(self, ctx):
        pass

    @has_permission()
    @_allowed_roles.command(name="add")
    async def __allowed_roles_add(
            self,
            ctx,
            role: discord.Role,
            *,
            command_name: str
    ):
        """Add a role to permissions allowed roles"""

        role_id = role.id
        guild = ctx.guild
        command_name = command_name.lower()

        permission = create_or_retrieve_command(
            self.bot,
            guild.id,
            command_name
        )

        if not permission:
            return await ctx.send(f"No command **{command_name}** has been found!")

        if role_id in permission.allowed_roles:
            return await ctx.send(f"Role {role.mention} is **present**!")

        permission.allowed_roles.append(role_id)

        create_or_retrieve_command(
            self.bot,
            guild.id,
            command_name,
            allowed_roles=permission.allowed_roles
        )

        await ctx.send(f"Added {role.mention} to **{permission.command_name}** command allowed roles!")

    @has_permission()
    @_allowed_roles.command(name="remove")
    async def __allowed_roles_remove(
            self,
            ctx,
            role: discord.Role,
            *,
            command_name: str
    ):
        """Remove a role from permissions allowed roles"""

        role_id = role.id
        guild = ctx.guild
        command_name = command_name.lower()

        permission = create_or_retrieve_command(
            self.bot,
            guild.id,
            command_name
        )

        if not permission:
            return await ctx.send(f"No command **{command_name}** has been found!")

        if role_id not in permission.allowed_roles:
            return await ctx.send(f"Role {role.mention} is not **present**!")

        permission.allowed_roles.remove(role_id)

        create_or_retrieve_command(
            self.bot,
            guild.id,
            command_name,
            allowed_roles=permission.allowed_roles
        )

        await ctx.send(f"Removed {role.mention} from **{permission.command_name}** command allowed roles!")


async def setup(bot):
    await bot.add_cog(PermissionCommand(bot))
