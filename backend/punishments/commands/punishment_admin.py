import discord
from discord.ext import commands

from backend.core.helper import get_time_now, format_time_in_zone, get_commands_help_messages, fmt_role, fmt_roles, \
    fmt_users, fmt_channel, fmt_user
from backend.core.pagination import Pagination
from backend.permissions.enforce import has_permission
from backend.punishments.director import create_or_update_punishment_config


class PunishmentAdminCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @commands.group(name="punishment-admin", invoke_without_command=True)
    async def _punishment_admin(self, ctx):
        view = Pagination(
            "ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴀᴅᴍɪɴ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_commands_help_messages(self.bot, [PunishmentAdminCommand], ctx.author.guild_permissions.administrator),
            3,
            ctx.author.id
        )

        await ctx.reply(embed=view.create_embed(), view=view)

    @has_permission()
    @_punishment_admin.command(name="manifest")
    async def _manifest(self, ctx):
        """
        Display the current punishments config
        """
        punishment_config = create_or_update_punishment_config(ctx.guild.id)

        description = (
            f"**ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʀᴏʟᴇѕ**: {fmt_roles(punishment_config.protected_roles)}\n"
            f"**ᴘʀᴏᴛᴇᴄᴛᴇᴅ ᴜѕᴇʀѕ**: {fmt_users(punishment_config.protected_users)}\n\n"
            f"**ᴍᴜᴛᴇᴅ ʀᴏʟᴇ**: {fmt_role(punishment_config.muted_role_id)}\n"
            f"**ʟᴏɢɢɪɴɢ ᴄʜᴀɴɴᴇʟ**: {fmt_channel(punishment_config.logging_channel_id)}\n"
        )

        embed = discord.Embed(
            title=f"ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴍᴀɴɪꜰᴇѕᴛ",
            description=description,
            color=0x393A41,
            timestamp=get_time_now()
        )

        embed.add_field(name="**ᴜᴘᴅᴀᴛᴇᴅ ᴀᴛ**", value=f"{format_time_in_zone(punishment_config.updated_at)}",
                        inline=True)
        embed.add_field(name="**ᴜᴘᴅᴀᴛᴇᴅ ʙʏ**", value=f"{fmt_user(punishment_config.updated_by)}", inline=True)

        await ctx.reply(embed=embed)

    @has_permission()
    @_punishment_admin.command(name="muted_role")
    async def _muted_role(
            self,
            ctx,
            role: discord.Role
    ):
        """
        Set the muted role for punishment config
        """
        create_or_update_punishment_config(
            ctx.guild.id,
            muted_role_id=role.id,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated punishment config **muted role** to {role.mention}.")

    @has_permission()
    @_punishment_admin.command(name="logging_channel")
    async def _logging_channel(
            self,
            ctx,
            channel: discord.TextChannel
    ):
        """
        Set the logging channel for punishment config
        """
        create_or_update_punishment_config(
            ctx.guild.id,
            logging_channel_id=channel.id,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated punishment config **logging channel** to {channel.mention}.")

    @has_permission()
    @_punishment_admin.group(name="protected_roles")
    async def _protected_roles(self, ctx):
        pass

    @has_permission()
    @_protected_roles.command(name="add")
    async def _protected_roles_add(
            self,
            ctx,
            role: discord.Role
    ):
        """
        Add a role to punishment config protected roles
        """
        punishment_config = create_or_update_punishment_config(ctx.guild.id)
        protected_roles = punishment_config.protected_roles

        if role.id in protected_roles:
            return await ctx.reply(f"Role {role.mention} is present!")

        protected_roles.append(role.id)

        create_or_update_punishment_config(
            ctx.guild.id,
            protected_roles=protected_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated punishment config **protected roles** by adding {role.mention}.")

    @has_permission()
    @_protected_roles.command(name="remove")
    async def _protected_roles_remove(
            self,
            ctx,
            role: discord.Role
    ):
        """
        Remove a role from punishment config protected roles
        """
        punishment_config = create_or_update_punishment_config(ctx.guild.id)
        protected_roles = punishment_config.protected_roles

        if role.id not in protected_roles:
            return await ctx.reply(f"Role {role.mention} is not present!")

        protected_roles.remove(role.id)

        create_or_update_punishment_config(
            ctx.guild.id,
            protected_roles=protected_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated punishment config **protected roles** by removing {role.mention}.")

    @has_permission()
    @_punishment_admin.group(name="protected_users")
    async def _protected_users(self, ctx):
        pass

    @has_permission()
    @_protected_users.command(name="add")
    async def _protected_users_add(
            self,
            ctx,
            member: discord.Member
    ):
        """
        Add a member to punishment config protected users
        """
        punishment_config = create_or_update_punishment_config(ctx.guild.id)
        protected_users = punishment_config.protected_users

        if member.id in protected_users:
            return await ctx.reply(f"User {member.mention} is present!")

        protected_users.append(member.id)

        create_or_update_punishment_config(
            ctx.guild.id,
            protected_users=protected_users,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated punishment config **protected users** by adding {member.mention}.")

    @has_permission()
    @_protected_users.command(name="remove")
    async def _protected_users_remove(
            self,
            ctx,
            member: discord.Member
    ):
        """
        Remove a member from punishment config protected users
        """
        punishment_config = create_or_update_punishment_config(ctx.guild.id)
        protected_users = punishment_config.protected_users

        if member.id not in protected_users:
            return await ctx.reply(f"User {member.mention} is not present!")

        protected_users.remove(member.id)

        create_or_update_punishment_config(
            ctx.guild.id,
            protected_users=protected_users,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated punishment config **protected users** by removing {member.mention}.")


async def setup(bot):
    await bot.add_cog(PunishmentAdminCommand(bot))
