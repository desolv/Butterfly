import discord
from discord import ButtonStyle

from backend.tickets.director import send_ticket_close_logging, get_ticket_by_channel, \
    update_or_retrieve_ticket_panel, mark_ticket_closed


class TicketCloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close",
        style=ButtonStyle.red,
        custom_id="tickets.close"
    )
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel is discord.TextChannel:
            return await interaction.followup.send("You may only use this command on a text channel!",
                                                   ephemeral=True)

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        ticket = get_ticket_by_channel(interaction.guild.id, interaction.channel.id)
        panel = update_or_retrieve_ticket_panel(interaction.guild.id, ticket.panel_id)

        if panel is None:
            return await interaction.followup.send("Ticket panel is not present!", ephemeral=True)

        if not interaction.user.guild_permissions.administrator and not any(
                role.id in panel.staff_role_ids for role in interaction.user.roles):
            return await interaction.followup.send("You are not allowed to close this ticket!", ephemeral=True)

        if ticket is None:
            return await interaction.followup.send("This channel is not a ticket!", ephemeral=True)
        if ticket.is_closed:
            return await interaction.followup.send("This ticket is already closed?", ephemeral=True)

        try:
            closed_ticket = mark_ticket_closed(interaction.guild.id, interaction.channel.id, interaction.user.id)
        except Exception:
            return await interaction.followup.send("Failed to close ticket. Contact an administrator!",
                                                   ephemeral=True)

        await interaction.followup.send("Closing ticket...!", ephemeral=True)

        try:
            await send_ticket_close_logging(interaction.guild, closed_ticket)
            await interaction.channel.delete(reason="Ticket closed")
        except Exception as e:
            await interaction.followup.send(
                f"Ticket closed in database. I couldn't perform last closing checks.. -> {e}", ephemeral=True)
