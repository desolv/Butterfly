import discord
from discord.ext import commands

from backend.configs.manager import update_punishment_config, get_punishment_settings
from backend.core.helper import get_sub_commands_help_message, get_utc_now, get_formatted_time, parse_iso
from backend.core.pagination import Pagination
from backend.permissions.enforce import has_permission


class PunishmentAdminCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @commands.group(
        name="punishment-admin",
        invoke_without_command=True
    )
    async def _punishment(self, ctx):
        view = Pagination(
            "ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴀᴅᴍɪɴ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_sub_commands_help_message(self.bot, "punishment-admin"),
            3,
            ctx.author.id
        )

        await ctx.send(embed=view.create_embed(), view=view)

    @has_permission()
    @_punishment.command(name="catalog")
    async def _catalog(self, ctx):
        """Display the current punishment catalog."""

        guild = ctx.guild

        muted_role, protected_roles, protected_users, moderation_channel, last_modify = get_punishment_settings(
            ctx.guild.id)

        muted_role = guild.get_role(muted_role)

        protected_roles = " ".join(
            [
                role.mention
                for role in (guild.get_role(int(role_id)) for role_id in protected_roles)
                if role
            ]
        ) or "None"

        protected_users = " ".join(
            [
                member.mention
                for member in (guild.get_member(int(member_id)) for member_id in protected_users)
                if member
            ]
        ) or "None"

        moderation_channel = guild.get_channel(moderation_channel)

        last_modify = get_formatted_time(
            parse_iso(last_modify),
            format="%d/%m/%y %H:%M %Z"
        ) if last_modify else "None"

        description = (
            f"**ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʀᴏʟᴇѕ**: {protected_roles}\n"
            f"**ᴘʀᴏᴛᴇᴄᴛᴇᴅ ᴜѕᴇʀѕ**: {protected_users}\n\n"
            f"**ᴍᴜᴛᴇᴅ ʀᴏʟᴇ**: {muted_role.mention if muted_role else "None"}\n"
            f"**ᴍᴏᴅᴇʀᴀᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ**: {moderation_channel.mention if moderation_channel else "None"}\n"
        )

        embed = discord.Embed(
            title=f"ᴘᴜɴɪѕʜᴍᴇɴᴛ ᴄᴀᴛᴀʟᴏɢ ꜰᴏʀ {guild.name}",
            description=description,
            color=0x393A41,
            timestamp=get_utc_now()
        )

        embed.add_field(name="**ʟᴀѕᴛ ᴍᴏᴅɪꜰʏ**", value=f"{last_modify}",
                        inline=True)
        embed.add_field(name="**ɢᴜɪʟᴅ ɪᴅ**", value=f"{guild.id}", inline=True)

        await ctx.send(embed=embed)

    @has_permission()
    @_punishment.command(name="muted_role")
    async def _muted_role(
            self,
            ctx,
            role: discord.Role
    ):
        """Set the muted role for punishments"""

        update_punishment_config(
            ctx.guild.id,
            muted_role=role.id,
            last_modify=get_utc_now().isoformat()
        )

        await ctx.send(f"Updated punishment **muted role** to {role.mention}")

    @has_permission()
    @_punishment.command(name="moderation_channel")
    async def _moderation_channel(
            self,
            ctx,
            channel: discord.TextChannel
    ):
        """Set the logging channel for punishments"""

        update_punishment_config(
            ctx.guild.id,
            moderation_channel=channel.id,
            last_modify=get_utc_now().isoformat()
        )

        await ctx.send(f"Updated punishment **moderation channel** to {channel.mention}")

    @has_permission()
    @_punishment.group(name="protected_roles")
    async def _protected_roles(self, ctx):
        pass

    @has_permission()
    @_protected_roles.command(name="add")
    async def _protected_roles_add(
            self,
            ctx,
            role: discord.Role
    ):
        """Add a role to punishment protected roles"""

        role_id = role.id
        _, protected_roles, _, _, _ = get_punishment_settings(ctx.guild.id)

        if role_id in protected_roles:
            return await ctx.send(f"Role {role.mention} is **present**!")

        protected_roles.append(role_id)

        update_punishment_config(
            ctx.guild.id,
            protected_roles=protected_roles,
            last_modify=get_utc_now().isoformat()
        )

        await ctx.send(f"Added {role.mention} to protected roles!")

    @has_permission()
    @_protected_roles.command(name="remove")
    async def _protected_roles_remove(
            self,
            ctx,
            role: discord.Role
    ):
        """Remove a role from punishment protected roles"""

        role_id = role.id
        _, protected_roles, _, _, _ = get_punishment_settings(ctx.guild.id)

        if role_id not in protected_roles:
            return await ctx.send(f"Role {role.mention} is **not present**!")

        protected_roles.remove(role_id)

        update_punishment_config(
            ctx.guild.id,
            protected_roles=protected_roles,
            last_modify=get_utc_now().isoformat()
        )

        await ctx.send(f"Removed {role.mention} from protected roles!")

    @has_permission()
    @_punishment.group(name="protected_users")
    async def _protected_users(self, ctx):
        pass

    @has_permission()
    @_protected_users.command(name="add")
    async def _protected_users_add(
            self,
            ctx,
            member: discord.Member
    ):
        """Add a member to punishment protected users"""

        member_id = member.id
        _, _, protected_users, _, _ = get_punishment_settings(ctx.guild.id)

        if member_id in protected_users:
            return await ctx.send(f"User {member.mention} is **present**!")

        protected_users.append(member_id)

        update_punishment_config(
            ctx.guild.id,
            protected_users=protected_users,
            last_modify=get_utc_now().isoformat()
        )

        await ctx.send(f"Added {member.mention} to protected users!")

    @has_permission()
    @_protected_users.command(name="remove")
    async def _protected_users_remove(
            self,
            ctx,
            member: discord.Member
    ):
        """Remove a member from punishment protected users"""

        member_id = member.id
        _, _, protected_users, _, _ = get_punishment_settings(ctx.guild.id)

        if member_id not in protected_users:
            return await ctx.send(f"User {member.mention} is **not present**!")

        protected_users.remove(member_id)

        update_punishment_config(
            ctx.guild.id,
            protected_users=protected_users,
            last_modify=get_utc_now().isoformat()
        )

        await ctx.send(f"Removed {member.mention} from protected users!")


async def setup(bot):
    await bot.add_cog(PunishmentAdminCommand(bot))
