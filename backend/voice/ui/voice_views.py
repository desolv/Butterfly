import discord

from backend.voice.director import (
    mark_voice_closed, handle_voice_channel_selection,
)
from backend.voice.ui.voice_modals import RenameModal, LimitModal, MemberPicker


class VoiceViews(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.secondary, custom_id="voice.button:rename")
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel, _ = await handle_voice_channel_selection(interaction)
        if not voice_channel:
            return
        await interaction.response.send_modal(RenameModal(voice_channel.id))

    @discord.ui.button(label="Limit", style=discord.ButtonStyle.secondary, custom_id="voice.button:limit")
    async def limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel, _ = await handle_voice_channel_selection(interaction)
        if not voice_channel:
            return
        await interaction.response.send_modal(LimitModal(voice_channel.id))

    @discord.ui.button(label="Lock", style=discord.ButtonStyle.primary, custom_id="voice.button:lock")
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel, voice = await handle_voice_channel_selection(interaction)
        if not voice_channel:
            return
        await voice_channel.set_permissions(interaction.guild.default_role, connect=False)
        owner_member = interaction.guild.get_member(voice.user_id)
        if owner_member:
            await voice_channel.set_permissions(owner_member, connect=True)
        await interaction.response.send_message("Locked.", ephemeral=True)

    @discord.ui.button(label="Unlock", style=discord.ButtonStyle.success, custom_id="voice.button:unlock")
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel, _ = await handle_voice_channel_selection(interaction)
        if not voice_channel:
            return
        await voice_channel.set_permissions(interaction.guild.default_role, overwrite=None)
        await interaction.response.send_message("Unlocked.", ephemeral=True)

    @discord.ui.button(label="Add", style=discord.ButtonStyle.secondary, custom_id="voice.button:add")
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel, _ = await handle_voice_channel_selection(interaction)
        if not voice_channel:
            return
        await interaction.response.send_message(
            "Pick a member to add.",
            view=MemberPicker(voice_channel.id, "add"),
            ephemeral=True
        )

    @discord.ui.button(label="Remove", style=discord.ButtonStyle.secondary, custom_id="voice.button:remove")
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel, _ = await handle_voice_channel_selection(interaction)
        if not voice_channel:
            return
        await interaction.response.send_message(
            "Pick a member to remove.",
            view=MemberPicker(voice_channel.id, "remove"),
            ephemeral=True
        )

    @discord.ui.button(label="Kick", style=discord.ButtonStyle.danger, custom_id="voice.button:kick")
    async def kick(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel, _ = await handle_voice_channel_selection(interaction)
        if not voice_channel:
            return
        await interaction.response.send_message(
            "Pick a member to kick.",
            view=MemberPicker(voice_channel.id, "kick"),
            ephemeral=True
        )

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, custom_id="voice.button:delete")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        voice_channel, _ = await handle_voice_channel_selection(interaction)
        if not voice_channel:
            return
        await voice_channel.delete()
        mark_voice_closed(voice_channel.id)
        await interaction.response.send_message("Channel deleted.", ephemeral=True)
