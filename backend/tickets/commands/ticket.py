import discord
from discord.ext import commands

from backend.core.helper import get_commands_help_messages, get_time_now, format_time_in_zone, fmt_user, get_user_best
from backend.core.pagination import Pagination
from backend.permissions.enforce import has_permission, has_cooldown
from backend.tickets.director import get_panels_for_guild, build_panel_list_view, \
    mark_ticket_closed, get_ticket_by_channel, send_ticket_logging, get_ticket_by_id, get_user_tickets


class TicketCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @has_permission()
    @commands.group(name="ticket", invoke_without_command=True)
    async def _ticket(self, ctx):
        view = Pagination(
            "ᴛɪᴄᴋᴇᴛ ѕᴜʙᴄᴏᴍᴍᴀɴᴅѕ",
            get_commands_help_messages(self.bot, [TicketCommand], ctx.author.guild_permissions.administrator),
            3,
            ctx.author.id
        )
        await ctx.reply(embed=view.create_embed(), view=view)

    @has_permission()
    @_ticket.command(name="send-embed", hidden=True)
    async def _send_embed(self, ctx):
        panels = get_panels_for_guild(ctx.guild.id)
        if not panels:
            return await ctx.reply("No panels configured for this guild!")

        view = build_panel_list_view(ctx.guild.id, panels)

        await ctx.send(embed=view.create_embed(), view=view)

    @has_permission()
    @has_cooldown()
    @commands.command(name="close")
    async def _close(self, ctx):
        """
        Close the current ticket channel
        """
        if ctx.channel is discord.TextChannel:
            return await ctx.reply("You may only use this command on a text channel!")

        ticket = get_ticket_by_channel(ctx.guild.id, ctx.channel.id)
        if ticket is None:
            return await ctx.reply("This channel is not a ticket!")
        if ticket.is_closed:
            return await ctx.reply("This ticket is already closed?")

        try:
            closed_ticket = mark_ticket_closed(ctx.guild.id, ctx.channel.id, ctx.author.id)
        except Exception:
            return await ctx.reply("Failed to close ticket. Contact an administrator!")

        await ctx.reply("Closing ticket...!")

        try:
            await send_ticket_logging(ctx.guild, closed_ticket)
            await ctx.channel.delete(reason="Ticket closed")
        except Exception as e:
            await ctx.reply(f"Ticket closed in database. I couldn't perform last closing checks.. -> {e}")

    @has_permission()
    @has_cooldown()
    @_ticket.command(name="view")
    async def _ticket_view(self, ctx, ticket_id: int):
        """
        Display detailed information about a specific ticket by ID
        """
        ticket = get_ticket_by_id(ctx.guild.id, ticket_id)

        if not ticket:
            await ctx.reply(f"No ticket matching **#{ticket_id}** found!")
            return

        description = (
            f"**ᴛɪᴄᴋᴇᴛ ɪᴅ**: **{ticket.ticket_id}**\n"
            f"**ᴘᴀɴᴇʟ ɪᴅ**: **{ticket.panel_id}**\n"
            f"**ᴄʜᴀɴɴᴇʟ ɪᴅ:** {ticket.channel_id}\n"
            f"**ᴄʀᴇᴀᴛᴇᴅ ᴀᴛ**: {format_time_in_zone(ticket.created_at)}\n"
        )

        if ticket.is_closed:
            description += (
                f"\n**ᴄʟᴏѕᴇᴅ ᴀᴛ**: {format_time_in_zone(ticket.closed_at)}\n"
                f"**ᴄʟᴏѕᴇᴅ ʙʏ**: {fmt_user(ticket.closed_by)}\n"
            )

        member = await get_user_best(self.bot, ctx.guild, ticket.user_id)

        embed = discord.Embed(
            title=f"ᴛɪᴄᴋᴇᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ ꜰᴏʀ @{member if member else ticket.user_id}",
            description=description,
            color=0x393A41,
            timestamp=get_time_now(),
        )

        embed.add_field(name="**ᴜᴘᴅᴀᴛᴇᴅ ᴀᴛ**",
                        value=f"{format_time_in_zone(ticket.updated_at)}", inline=True)
        embed.add_field(name="**ɢᴜɪʟᴅ ɪᴅ**", value=f"{ctx.guild.id}", inline=True)

        avatar_url = member.avatar.url if member.avatar is not None else "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_thumbnail(url=avatar_url)

        await ctx.reply(embed=embed)

    @has_permission()
    @has_cooldown()
    @_ticket.command(name="modlog")
    async def _modlog(self, ctx, member: discord.Member):
        """
        Display all tickets of member
        """
        tickets = get_user_tickets(ctx.guild.id, member.id)

        if len(tickets) <= 0:
            return await ctx.reply("No ticket to display yet!")

        lines: list[str] = []
        for ticket in tickets:
            description = (
                f"**#{ticket.ticket_id}**\n"
                f"**ᴘᴀɴᴇʟ ɪᴅ**: **{ticket.panel_id}**\n"
                f"**ᴄʀᴇᴀᴛᴇᴅ ᴀᴛ**: {format_time_in_zone(ticket.created_at)}\n"
            )

            if ticket.is_closed:
                description += (
                    f"**ᴄʟᴏѕᴇᴅ ᴀᴛ**: {format_time_in_zone(ticket.closed_at)}\n"
                    f"**ᴄʟᴏѕᴇᴅ ʙʏ**: {fmt_user(ticket.closed_by)}\n"
                )

            lines.append(description)

        view = Pagination(
            f"ᴛɪᴄᴋᴇᴛ ᴍᴏᴅʟᴏɢ ꜰᴏʀ @{member}",
            lines,
            3,
            ctx.author.id,
            True
        )

        await ctx.reply(embed=view.create_embed(), view=view)


async def setup(bot):
    await bot.add_cog(TicketCommand(bot))
