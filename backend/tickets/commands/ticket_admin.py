import discord
from discord.ext import commands

from backend.core.helper import get_commands_help_messages, format_time_in_zone, get_utc_now
from backend.core.pagination import Pagination
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
            return await ctx.reply("Name id is characters is too long!")

        panel = create_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            return await ctx.reply(f"Panel **{panel_id}** is present!")

        await ctx.reply(f"Created panel **{panel_id}**!")

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
            return await ctx.reply("Panel not found, or not owned by this guild!")

        await ctx.reply(f"Panel **{panel_id}** has been deleted!")

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
        guild = ctx.guild
        panel = update_or_retrieve_ticket_panel(guild.id, panel_id)

        if not panel:
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        category_channel = guild.get_channel(panel.category_channel_id)

        staff_roles = " ".join(
            [
                role.mention
                for role in (guild.get_role(int(role_id)) for role_id in panel.staff_role_ids)
                if role
            ]
        ) or "None"

        mention_roles = " ".join(
            [
                role.mention
                for role in (guild.get_role(int(role_id)) for role_id in panel.mention_role_ids)
                if role
            ]
        ) or "None"

        logging_channel = guild.get_channel(panel.logging_channel_id)

        created_at = format_time_in_zone(panel.created_at, format="%d/%m/%y %H:%M %Z")
        updated_at = format_time_in_zone(panel.updated_at,
                                         format="%d/%m/%y %H:%M %Z") if panel.updated_at else "None"

        updated_by = guild.get_member(panel.updated_by)
        updated_by = updated_by.mention if updated_by else "None"

        panel_embed = panel.panel_embed

        description = (
            f"**ᴘᴀɴᴇʟ ɴᴀᴍᴇ**: {panel_embed.get("name") or panel_id}\n"
            f"**ᴘᴀɴᴇʟ ᴅᴇѕᴄʀɪᴘᴛɪᴏɴ**: {panel_embed.get("description")}\n"
            f"**ᴘᴀɴᴇʟ ᴇᴍᴏᴊɪ**: {panel_embed.get("emoji")}\n"
            f"**ᴀᴜᴛʜᴏʀ ᴜʀʟ**: {'✅' if panel_embed.get("author_url") else '❎'}\n\n"

            f"**ᴄᴀᴛᴇɢᴏʀʏ ᴄʜᴀɴɴᴇʟ**: {category_channel.name if category_channel else panel.category_channel_id}\n"
            f"**ѕᴛᴀꜰꜰ ʀᴏʟᴇѕ**: {staff_roles}\n"
            f"**ᴍᴇɴᴛɪᴏɴ ʀᴏʟᴇѕ**: {mention_roles}\n\n"

            f"**ᴇᴍʙᴇᴅ ᴛɪᴛʟᴇ**: {panel.ticket_embed.get("title")}\n"
            f"**ᴇᴍʙᴇᴅ ᴅᴇѕᴄʀɪᴘᴛɪᴏɴ**: {panel.ticket_embed.get("description")}\n\n"

            f"**ʟᴏɢɢɪɴɢ ᴄʜᴀɴɴᴇʟ**: {logging_channel.mention if logging_channel else panel.logging_channel_id}\n"
            f"**ᴄʀᴇᴀᴛᴇᴅ ᴀᴛ**: {created_at}\n"
            f"**ᴇɴᴀʙʟᴇᴅ**: {'✅' if panel.is_enabled else '❎'}\n"
        )

        embed = discord.Embed(
            title=f"**{panel_id}** ᴛɪᴄᴋᴇᴛ ᴄᴀᴛᴇɢᴏʀʏ",
            description=description,
            color=0x393A41,
            timestamp=get_utc_now()
        )

        embed.add_field(name="**ᴜᴘᴅᴀᴛᴇᴅ ᴀᴛ**", value=updated_at, inline=True)
        embed.add_field(name="**ᴜᴘᴅᴀᴛᴇᴅ ʙʏ**", value=updated_by, inline=True)

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
            staff_roles = " ".join(
                [
                    role.mention
                    for role in (ctx.guild.get_role(int(role_id)) for role_id in panel.staff_role_ids)
                    if role
                ]
            ) or "None"

            lines.append(
                f"**{panel.panel_id}**\n"
                f"**ᴘᴀɴᴇʟ ɴᴀᴍᴇ**: {panel.panel_embed.get("name") or panel.panel_id}\n"
                f"**ѕᴛᴀꜰꜰ ʀᴏʟᴇѕ**: {staff_roles}\n"
                f"**ᴄʀᴇᴀᴛᴇᴅ ᴀᴛ**: **{format_time_in_zone(panel.created_at, format="%d/%m/%y %H:%M %Z")}**\n"
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
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        await ctx.reply(f"Updated panel **{panel_id}** 'panel name' to **{name}**!")

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
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        await ctx.reply(f"Updated panel **{panel_id}** 'pane description' to **{description}**!")

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
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        await ctx.reply(f"Updated panel **{panel_id}** 'panel emoji' to **{emoji}**!")

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
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        await ctx.reply(f"Updated panel **{panel_id}** 'author url' to **{enabled}**!")

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
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        await ctx.reply(f"Updated panel **{panel_id}** 'category channel' to **{channel.name}**!")

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
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        await ctx.reply(f"Updated panel **{panel_id}** 'embed title' to **{title}**!")

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
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        await ctx.reply(f"Updated panel **{panel_id}** 'embed description' to **{description}**!")

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
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        await ctx.reply(f"Updated panel **{panel_id}** 'logging channel' to {channel.mention}!")

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
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        await ctx.reply(f"Updated panel **{panel_id}** 'is enabled' to **{enabled}**!")

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
        role_id = role.id
        panel = update_or_retrieve_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        staff_roles = panel.staff_role_ids

        if role_id in staff_roles:
            return await ctx.reply(f"Role {role.mention} is present!")

        staff_roles.append(role_id)

        update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            staff_role_ids=staff_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated panel **{panel_id}** 'staff roles' by adding {role.mention}")

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
        role_id = role.id
        panel_id = panel_id.lower()
        panel = update_or_retrieve_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        staff_roles = panel.staff_role_ids

        if role_id not in staff_roles:
            return await ctx.reply(f"Role {role.mention} is not present!")

        staff_roles.remove(role_id)

        update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            staff_role_ids=staff_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated panel **{panel_id}** 'staff roles' by removing {role.mention}")

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
        role_id = role.id
        panel = update_or_retrieve_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        mention_roles = panel.mention_role_ids

        if role_id in mention_roles:
            return await ctx.reply(f"Role {role.mention} is present!")

        mention_roles.append(role_id)

        update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            mention_role_ids=mention_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated panel **{panel_id}** 'mention roles' by adding {role.mention}")

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
        role_id = role.id
        panel = update_or_retrieve_ticket_panel(ctx.guild.id, panel_id)

        if not panel:
            return await ctx.reply(f"No panel **{panel_id}** has been found!")

        mention_roles = panel.mention_role_ids

        if role_id not in mention_roles:
            return await ctx.reply(f"Role {role.mention} is not present!")

        mention_roles.remove(role_id)

        update_or_retrieve_ticket_panel(
            ctx.guild.id,
            panel_id,
            mention_role_ids=mention_roles,
            updated_by=ctx.author.id
        )

        await ctx.reply(f"Updated panel **{panel_id}** 'mention roles' by removing {role.mention}")


async def setup(bot):
    await bot.add_cog(TicketAdminCommand(bot))
