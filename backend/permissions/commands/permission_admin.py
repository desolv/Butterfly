import discord
from discord.ext import commands

from backend.core.helper import get_utc_now, format_time_in_zone, get_commands_help_messages
from backend.core.pagination import Pagination
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
        guild = ctx.guild
        permission = create_or_retrieve_command(self.bot, guild.id, command_name)

        if not permission:
            return await ctx.reply(f"No command **{command_name}** has been found!")

        required_roles = " ".join(
            [
                role.mention
                for role in (guild.get_role(int(role_id)) for role_id in permission.required_role_ids)
                if role
            ]
        ) or "None"

        description = (
            f"**ᴀᴅᴍɪɴ**: {'✅' if permission.is_admin else '❎'}\n"
            f"**ʀᴇǫᴜɪʀᴇᴅ ʀᴏʟᴇѕ**: {required_roles}\n"
            f"**ᴄᴏᴏʟᴅᴏᴡɴ**: {f"**{permission.command_cooldown}s**" if permission.command_cooldown > 0 else "None"}\n\n"
            f"**ᴇɴᴀʙʟᴇᴅ**: {'✅' if permission.is_enabled else '❎'}\n"
        )

        embed = discord.Embed(
            title=f"**{permission.command_name}** ᴄᴏᴍᴍᴀɴᴅ",
            description=description,
            color=0x393A41,
            timestamp=get_utc_now()
        )

        embed.add_field(name="**ᴀᴅᴅᴇᴅ ᴀᴛ**",
                        value=f"{format_time_in_zone(permission.added_at, format="%d/%m/%y %H:%M %Z")}", inline=True)
        embed.add_field(name="**ɢᴜɪʟᴅ ɪᴅ**", value=f"{guild.id}", inline=True)

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
            required_roles = " ".join(
                [
                    role.mention
                    for role in (ctx.guild.get_role(int(role_id)) for role_id in permission.required_role_ids)
                    if role
                ]
            ) or "None"

            lines.append(
                f"**{permission.command_name}**\n"
                f"**ᴀᴅᴍɪɴ**: {'✅' if permission.is_admin else '❎'}\n"
                f"**ʀᴇǫᴜɪʀᴇᴅ ʀᴏʟᴇѕ**: {required_roles}\n"
                f"**ᴄᴏᴏʟᴅᴏᴡɴ**: {f"**{permission.command_cooldown}s**" if permission.command_cooldown > 0 else "None"}\n"
                f"**ᴇɴᴀʙʟᴇᴅ**: {'✅' if permission.is_enabled else '❎'}\n"
            )

        view = Pagination(
            f"ᴘᴇʀᴍɪѕѕɪᴏɴ ᴍᴀɴɪꜰᴇѕᴛ ꜰᴏʀ {ctx.guild.name}",
            lines,
            3,
            ctx.author.id
        )

        await ctx.reply(embed=view.create_embed(), view=view)

    @has_permission()
    @_permission_admin.command(name="is_admin")
    async def _is_admin(
            self,
            ctx,
            is_admin: bool,
            *,
            command_name: str
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
            return await ctx.reply(f"No command **{command_name}** has been found!")

        await ctx.reply(
            f"Updated permission **is admin** for **{permission.command_name}** command to **{permission.is_admin}**")

    @has_permission()
    @_permission_admin.command(name="is_enabled")
    async def _is_enabled(
            self,
            ctx,
            is_enabled: bool,
            *,
            command_name: str
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
            return await ctx.reply(f"No command **{command_name}** has been found!")

        await ctx.reply(
            f"Updated permission **is enabled** for **{permission.command_name}** command to **{permission.is_enabled}**")

    @has_permission()
    @_permission_admin.command(name="cooldown")
    async def _cooldown(
            self,
            ctx,
            seconds: int,
            *,
            command_name: str
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
            return await ctx.reply(f"No command **{command_name}** has been found!")

        await ctx.reply(
            f"Updated permission **cooldown** for **{permission.command_name}** command to **{f"{seconds}s" if seconds > 0 else "None"}**")

    @has_permission()
    @_permission_admin.group(name="required_roles")
    async def _required_roles(self, ctx):
        pass

    @has_permission()
    @_required_roles.command(name="add")
    async def _required_roles_add(
            self,
            ctx,
            role: discord.Role,
            *,
            command_name: str
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
            return await ctx.reply(f"No command **{command_name}** has been found!")

        role_id = role.id

        if role_id in permission.required_role_ids:
            return await ctx.reply(f"Role {role.mention} is **present**!")

        permission.required_role_ids.append(role_id)

        create_or_retrieve_command(
            self.bot,
            ctx.guild.id,
            command_name,
            required_role_ids=permission.required_role_ids
        )

        await ctx.reply(
            f"Updated permission **required roles** for **{permission.command_name}** command by adding {role.mention}")

    @has_permission()
    @_required_roles.command(name="remove")
    async def _required_roles_remove(
            self,
            ctx,
            role: discord.Role,
            *,
            command_name: str
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
            return await ctx.reply(f"No command **{command_name}** has been found!")

        role_id = role.id

        if role_id not in permission.required_role_ids:
            return await ctx.reply(f"Role {role.mention} is not **present**!")

        permission.required_role_ids.remove(role_id)

        create_or_retrieve_command(
            self.bot,
            ctx.guild.id,
            command_name,
            required_role_ids=permission.required_role_ids
        )

        await ctx.reply(
            f"Updated permission **required roles** for **{permission.command_name}** command by removing {role.mention}")


async def setup(bot):
    await bot.add_cog(PermissionAdminCommand(bot))
