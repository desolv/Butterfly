import asyncio

import discord
from discord import InteractionType, AuditLogAction
from discord.ext import commands

from backend.tickets.director import (
    get_panels_for_guild,
    build_panel_list_view,
    handle_ticket_panel_selection, get_ticket_by_channel, mark_ticket_closed, send_ticket_close_logging,
)
from backend.tickets.models.ticket_close_button import TicketCloseButton


class TicketEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._bound_msgs: set[int] = set()
        self.bot.add_view(TicketCloseButton())

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type is not InteractionType.component or interaction.guild is None:
            return

        if interaction.data.get("custom_id") != "tickets.menu":
            return

        message_id = interaction.message.id
        if message_id not in self._bound_msgs:
            view = build_panel_list_view(interaction.guild.id, get_panels_for_guild(interaction.guild.id))

            self.bot.add_view(view, message_id=message_id)
            self._bound_msgs.add(message_id)

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        values = interaction.data.get("values") or []
        await handle_ticket_panel_selection(interaction, values)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if channel == discord.TextChannel or channel.guild is None:
            return

        guild = channel.guild

        ticket = get_ticket_by_channel(guild.id, channel.id)
        if ticket is None or ticket.is_closed:
            return

        await asyncio.sleep(1)

        actioner_id = None
        try:
            async for entry in guild.audit_logs(
                    limit=5,
                    action=AuditLogAction.channel_delete
            ):
                if entry.target.channel.id == channel.id:
                    actioner_id = None if entry.user.id == self.bot.user.id else entry.user.id
                    break
        except Exception:
            pass

        try:
            closed_ticket = mark_ticket_closed(guild.id, channel.id, actioner_id)
            await send_ticket_close_logging(guild, closed_ticket)
        except Exception:
            return


async def setup(bot):
    await bot.add_cog(TicketEvents(bot))
