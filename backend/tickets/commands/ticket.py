import discord
from discord.ext import commands

from backend.core.helper import get_commands_help_messages
from backend.core.pagination import Pagination
from backend.permissions.enforce import has_permission
from backend.tickets.director import get_panels_for_guild, build_panel_list_view, \
    mark_ticket_closed, get_ticket_by_channel, send_ticket_close_logging


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
            await send_ticket_close_logging(ctx.guild, closed_ticket)
            await ctx.channel.delete(reason="Ticket closed")
        except Exception as e:
            await ctx.reply(f"Ticket closed in database. I couldn't perform last closing checks.. -> {e}")


async def setup(bot):
    await bot.add_cog(TicketCommand(bot))
