import discord
from discord.ext import commands

from backend.core.helper import get_commands_help_messages, format_time_in_zone, get_time_now, fmt_channel, fmt_roles, \
    fmt_user
from backend.core.pagination import Pagination
from backend.errors.custom_errors import TicketPanelNotFound
from backend.permissions.enforce import has_permission
from backend.tickets.director import create_ticket_panel, delete_ticket_panel, update_or_retrieve_ticket_panel, \
    get_panels_for_guild


class TicketAdminCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @commands.group(name="ticket-admin", invoke_without_command=True)
    async def _ticket_admin(self, ctx):
        """
        Show ticket-admin subcommands
        """
        view = Pagination(
            "ᴛɪᴄᴋᴇᴛ ᴀᴅᴍɪɴ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_commands_help_messages(self.bot, [TicketAdminCommand], ctx.author.guild_permissions.administrator),
            3,
            ctx.author.id
        )
        await ctx.reply(embed=view.create_embed(), view=view)

    @has_permission()
    @_ticket_admin.command(name="create")
    async def _create(
            self,
            ctx,
            panel_id: str
    ):
        """
        Create a new ticket category
        """
        if len(panel_id) > 15:
            return await ctx.reply("Id characters length is too long!")

        panel = create_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            return await ctx.reply(f"Ticket panel {panel_id} is present!")

        await ctx.reply(f"Created ticket panel **{panel_id}**!")

    @has_permission()
    @_ticket_admin.command(name="delete")
    async def _delete(
            self,
            ctx,
            panel_id: str,
            confirm: bool = False
    ):
        """
        Delete a ticket category
        """
        if not confirm:
            return await ctx.reply(
                f"This will permanently delete panel **{panel_id}**!, Re-run by adding **true** to proceed!"
            )

        deleted = delete_ticket_panel(ctx.guild.id, panel_id)
        if not deleted:
            raise TicketPanelNotFound(panel_id)

        await ctx.reply(f"Ticket panel **{panel_id}** has been deleted!")

    @has_permission()
    @_ticket_admin.command(name="view")
    async def _view(
            self,
            ctx,
            *,
            panel_id: str
    ):
        """
        Display the current command information
        """
        panel = update_or_retrieve_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            raise TicketPanelNotFound(panel_id)

        panel_embed = panel.panel_embed

        description = (
            f"**ᴘᴀɴᴇʟ ɴᴀᴍᴇ**: {panel_embed.get("name") or panel_id}\n"
            f"**ᴘᴀɴᴇʟ ᴅᴇѕᴄʀɪᴘᴛɪᴏɴ**: {panel_embed.get("description")}\n"
            f"**ᴘᴀɴᴇʟ ᴇᴍᴏᴊɪ**: {panel_embed.get("emoji")}\n"
            f"**ᴀᴜᴛʜᴏʀ ᴜʀʟ**: {'✅' if panel_embed.get("author_url") else '❎'}\n\n"

            f"**ᴄᴀᴛᴇɢᴏʀʏ ᴄʜᴀɴɴᴇʟ**: {fmt_channel(panel.category_channel_id)}\n"
            f"**ѕᴛᴀꜰꜰ ʀᴏʟᴇѕ**: {fmt_roles(panel.staff_role_ids)}\n"
            f"**ᴍᴇɴᴛɪᴏɴ ʀᴏʟᴇѕ**: {fmt_roles(panel.mention_role_ids)}\n"
            f"**ʀᴇǫᴜɪʀᴇᴅ ʀᴏʟᴇѕ**: {fmt_roles(panel.required_role_ids)}\n\n"

            f"**ᴇᴍʙᴇᴅ ᴛɪᴛʟᴇ**: {panel.ticket_embed.get("title")}\n"
            f"**ᴇᴍʙᴇᴅ ᴅᴇѕᴄʀɪᴘᴛɪᴏɴ**: {panel.ticket_embed.get("description")}\n\n"

            f"**ʟᴏɢɢɪɴɢ ᴄʜᴀɴɴᴇʟ**: {fmt_channel(panel.logging_channel_id)}\n"
            f"**ᴄʀᴇᴀᴛᴇᴅ ᴀᴛ**: {format_time_in_zone(panel.created_at)}\n"
            f"**ᴇɴᴀʙʟᴇᴅ**: {'✅' if panel.is_enabled else '❎'}\n"
        )

        embed = discord.Embed(
            title=f"**{panel_id}** ᴛɪᴄᴋᴇᴛ ᴘᴀɴᴇʟ",
            description=description,
            color=0x393A41,
            timestamp=get_time_now()
        )

        embed.add_field(name="**ᴜᴘᴅᴀᴛᴇᴅ ᴀᴛ**", value=format_time_in_zone(panel.updated_at), inline=True)
        embed.add_field(name="**ᴜᴘᴅᴀᴛᴇᴅ ʙʏ**", value=fmt_user(panel.updated_by), inline=True)

        await ctx.reply(embed=embed)

    @has_permission()
    @_ticket_admin.command(name="manifest")
    async def _manifest(self, ctx):
        """
        Display the current ticket panels
        """
        panels = get_panels_for_guild(ctx.guild.id)

        if len(panels) <= 0:
            return await ctx.reply("No ticket panels to display yet!")

        lines: list[str] = []
        for panel in panels:
            lines.append(
                f"**{panel.panel_id}**\n"
                f"**ᴘᴀɴᴇʟ ɴᴀᴍᴇ**: {panel.panel_embed.get("name") or panel.panel_id}\n"
                f"**ѕᴛᴀꜰꜰ ʀᴏʟᴇѕ**: {fmt_roles(panel.staff_role_ids)}\n"
                f"**ʀᴇǫᴜɪʀᴇᴅ ʀᴏʟᴇѕ**: {fmt_roles(panel.required_role_ids)}\n"
                f"**ᴄʀᴇᴀᴛᴇᴅ ᴀᴛ**: **{format_time_in_zone(panel.created_at)}**\n"
                f"**ᴇɴᴀʙʟᴇᴅ**: {'✅' if panel.is_enabled else '❎'}\n"
            )

        view = Pagination(
            f"ᴛɪᴄᴋᴇᴛ ᴘᴀɴᴇʟ ᴍᴀɴɪꜰᴇѕᴛ ꜰᴏʀ {ctx.guild.name}",
            lines,
            3,
            ctx.author.id,
            True
        )

        await ctx.reply(embed=view.create_embed(), view=view)

    @has_permission()
    @_ticket_admin.group(name="panel")
    async def _panel(self, ctx):
        pass

    @has_permission()
    @_panel.command(name="name")
    async def _panel_name(
            self,
            ctx,
            panel_id: str,
            *,
            name: str
    ):
        """
        Set the panel name for ticket panel
        """
        panel = update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            panel_name=name,
            updated_by=ctx.author.id
        )

        if not panel:
            raise TicketPanelNotFound(panel_id)

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **panel name** to **{name}**.")

    @has_permission()
    @_panel.command(name="description")
    async def _panel_description(
            self,
            ctx,
            panel_id: str,
            *,
            description: str
    ):
        """
        Set the panel description for ticket panel
        """
        panel = update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            panel_description=description,
            updated_by=ctx.author.id
        )

        if not panel:
            raise TicketPanelNotFound(panel_id)

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **panel description** to **{description}**.")

    @has_permission()
    @_panel.command(name="emoji")
    async def _panel_emoji(
            self,
            ctx,
            panel_id: str,
            emoji: str
    ):
        """
        Set the panel emoji for ticket panel
        """
        panel = update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            panel_emoji=emoji,
            updated_by=ctx.author.id
        )

        if not panel:
            raise TicketPanelNotFound(panel_id)

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **panel emoji** to {emoji}.")

    @has_permission()
    @_panel.command(name="author_url")
    async def _panel_author_url(
            self,
            ctx,
            panel_id: str,
            enabled: bool
    ):
        """
        Set the enabled for ticket panel
        """
        panel = update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            panel_author_url=enabled,
            updated_by=ctx.author.id
        )

        if not panel:
            raise TicketPanelNotFound(panel_id)

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **panel author url** to **{enabled}**.")

    @has_permission()
    @_ticket_admin.command(name="category_channel")
    async def _category_channel(
            self,
            ctx,
            panel_id: str,
            channel: discord.CategoryChannel
    ):
        """
        Set the category channel for ticket panel
        """
        panel = update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            category_channel_id=channel.id,
            updated_by=ctx.author.id
        )

        if not panel:
            raise TicketPanelNotFound(panel_id)

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **category channel** to **{channel.name}**.")

    @has_permission()
    @_ticket_admin.group(name="embed")
    async def _embed(self, ctx):
        pass

    @has_permission()
    @_embed.command(name="title")
    async def _embed_title(
            self,
            ctx,
            panel_id: str,
            *,
            title: str
    ):
        """
        Set the embed title for ticket panel
        """
        panel = update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            ticket_title=title,
            updated_by=ctx.author.id
        )

        if not panel:
            raise TicketPanelNotFound(panel_id)

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **embed title** to **{title}**.")

    @has_permission()
    @_embed.command(name="description")
    async def _embed_description(
            self,
            ctx,
            panel_id: str,
            *,
            description: str
    ):
        """
        Set the embed description for ticket panel
        """
        panel = update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            ticket_description=description,
            updated_by=ctx.author.id
        )

        if not panel:
            raise TicketPanelNotFound(panel_id)

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **embed description** to **{description}**.")

    @has_permission()
    @_ticket_admin.command(name="logging_channel")
    async def _logging_channel(
            self,
            ctx,
            panel_id: str,
            channel: discord.TextChannel
    ):
        """
        Set the logging channel for ticket panel
        """
        panel = update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            logging_channel_id=channel.id,
            updated_by=ctx.author.id
        )

        if not panel:
            raise TicketPanelNotFound(panel_id)

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **logging channel** to {channel.mention}.")

    @has_permission()
    @_ticket_admin.command(name="is_enabled")
    async def _is_enabled(
            self,
            ctx,
            panel_id: str,
            enabled: bool
    ):
        """
        Set the enabled for ticket panel
        """
        panel = update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            is_enabled=enabled,
            updated_by=ctx.author.id
        )

        if not panel:
            raise TicketPanelNotFound(panel_id)

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **is enabled** to **{enabled}**.")

    @has_permission()
    @_ticket_admin.group(name="required_roles")
    async def _required_roles(self, ctx):
        pass

    @has_permission()
    @_required_roles.command(name="add")
    async def _required_roles_add(
            self,
            ctx,
            panel_id: str,
            role: discord.Role
    ):
        """
        Add a role to ticket panel required roles
        """
        panel = update_or_retrieve_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            raise TicketPanelNotFound(panel_id)

        required_roles = panel.required_role_ids

        if role.id in required_roles:
            return await ctx.reply(f"Role {role.mention} is present!")

        required_roles.append(role.id)

        update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            required_role_ids=required_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **required roles** by adding {role.mention}.")

    @has_permission()
    @_required_roles.command(name="remove")
    async def _required_roles_remove(
            self,
            ctx,
            panel_id: str,
            role: discord.Role
    ):
        """
        Remove a role from ticket panel required roles
        """
        panel = update_or_retrieve_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            raise TicketPanelNotFound(panel_id)

        required_roles = panel.required_role_ids

        if role.id not in required_roles:
            return await ctx.reply(f"Role {role.mention} is not present!")

        required_roles.remove(role.id)

        update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            required_role_ids=required_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **required roles** by removing {role.mention}.")

    @has_permission()
    @_required_roles.command(name="everyone")
    async def _required_roles_everyone(
            self,
            ctx,
            panel_id: str,
            allow: bool
    ):
        """
        Allow everyone in this guild to run the command
        """
        panel = update_or_retrieve_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            raise TicketPanelNotFound(panel_id)

        required_roles = panel.required_role_ids

        guild_id = ctx.guild.id
        if allow:
            if guild_id in required_roles:
                return await ctx.reply(f"Role **everyone** is present!")

            required_roles.append(guild_id)
        else:
            if guild_id not in required_roles:
                return await ctx.reply(f"Role **everyone** is not present!")

            required_roles.remove(guild_id)

        update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            required_role_ids=required_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(
            f"Updated ticket **{panel.panel_id}** panel **required roles** by {"allowing" if allow else "restricting"} everyone.")

    @has_permission()
    @_ticket_admin.group(name="staff_roles")
    async def _staff_roles(self, ctx):
        pass

    @has_permission()
    @_staff_roles.command(name="add")
    async def _staff_roles_add(
            self,
            ctx,
            panel_id: str,
            role: discord.Role
    ):
        """
        Add a role to ticket panel staff roles
        """
        panel = update_or_retrieve_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            raise TicketPanelNotFound(panel_id)

        staff_roles = panel.staff_role_ids

        if role.id in staff_roles:
            return await ctx.reply(f"Role {role.mention} is present!")

        staff_roles.append(role.id)

        update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            staff_role_ids=staff_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **staff roles** by adding {role.mention}.")

    @has_permission()
    @_staff_roles.command(name="remove")
    async def _staff_roles_remove(
            self,
            ctx,
            panel_id: str,
            role: discord.Role
    ):
        """
        Remove a role from ticket panel staff roles
        """
        panel = update_or_retrieve_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            raise TicketPanelNotFound(panel_id)

        staff_roles = panel.staff_role_ids

        if role.id not in staff_roles:
            return await ctx.reply(f"Role {role.mention} is not present!")

        staff_roles.remove(role.id)

        update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            staff_role_ids=staff_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **staff roles** by removing {role.mention}.")

    @has_permission()
    @_ticket_admin.group(name="mention_roles")
    async def _mention_roles(self, ctx):
        pass

    @has_permission()
    @_mention_roles.command(name="add")
    async def _mention_roles_add(
            self,
            ctx,
            panel_id: str,
            role: discord.Role
    ):
        """
        Add a role to ticket panel staff roles
        """
        panel = update_or_retrieve_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            raise TicketPanelNotFound(panel_id)

        mention_roles = panel.mention_role_ids

        if role.id in mention_roles:
            return await ctx.reply(f"Role {role.mention} is present!")

        mention_roles.append(role.id)

        update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            mention_role_ids=mention_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **mention roles** by adding {role.mention}.")

    @has_permission()
    @_mention_roles.command(name="remove")
    async def _mention_roles_remove(
            self,
            ctx,
            panel_id: str,
            role: discord.Role
    ):
        """
        Remove a role from ticket panel staff roles
        """
        panel = update_or_retrieve_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            raise TicketPanelNotFound(panel_id)

        mention_roles = panel.mention_role_ids

        if role.id not in mention_roles:
            return await ctx.reply(f"Role {role.mention} is not present!")

        mention_roles.remove(role.id)

        update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            mention_role_ids=mention_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated ticket **{panel.panel_id}** panel **mention roles** by removing {role.mention}.")


async def setup(bot):
    await bot.add_cog(TicketAdminCommand(bot))
