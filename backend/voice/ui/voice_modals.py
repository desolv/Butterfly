import discord

from backend.voice.director import handle_voice_channel_selection


class RenameModal(discord.ui.Modal, title="Rename Channel"):
    new_name = discord.ui.TextInput(label="New name", max_length=100, required=True)

    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        voice_channel, _ = await handle_voice_channel_selection(interaction)
        if not voice_channel:
            return

        try:
            await voice_channel.edit(name=str(self.new_name))
        except Exception as e:
            return await interaction.response.send_message(f"Something went wrong while naming the channel -> {e}")

        await interaction.response.send_message(f"Renamed to **{self.new_name}**.", ephemeral=True)


class LimitModal(discord.ui.Modal, title="Set User Limit"):
    limit = discord.ui.TextInput(label="User limit (0 for no limit)", required=True)

    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id

    async def on_submit(self, interaction: discord.Interaction):
        voice_channel, _ = await handle_voice_channel_selection(interaction)
        if not voice_channel:
            return

        try:
            user_limit_value = max(0, min(99, int(str(self.limit))))
        except ValueError:
            return await interaction.response.send_message("Enter a number between 0–99.", ephemeral=True)

        try:
            await voice_channel.edit(user_limit=user_limit_value)
        except Exception as e:
            return await interaction.response.send_message(f"Something went wrong while limiting the channel -> {e}")

        pretty_value = "No limit" if user_limit_value == 0 else str(user_limit_value)
        await interaction.response.send_message(f"Limit set to **{pretty_value}**.", ephemeral=True)


class _MemberSelect(discord.ui.UserSelect):
    """
    Ephemeral picker used by the panel buttons
    """

    def __init__(self, channel_id: int, action: str):
        super().__init__(placeholder="Choose a member..", min_values=1, max_values=1)
        self.channel_id = channel_id
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        voice_channel, voice = await handle_voice_channel_selection(interaction)
        if not voice_channel:
            return

        selected_user = self.values[0]
        target_member = interaction.guild.get_member(selected_user.id)
        if not target_member:
            await interaction.response.send_message("Member not found.", ephemeral=True)
            return

        try:
            if self.action == "add":
                await voice_channel.set_permissions(target_member, connect=True)
                message_text = f"Added {target_member.mention}."

            elif self.action == "remove":
                await voice_channel.set_permissions(target_member, overwrite=None)
                message_text = f"Removed {target_member.mention}."

            elif self.action == "kick":
                if not (
                        target_member.voice and target_member.voice.channel and target_member.voice.channel.id == voice_channel.id):
                    message_text = f"{target_member.mention} is not in this voice channel."
                else:
                    try:
                        await target_member.move_to(None)
                    except discord.HTTPException:
                        pass
                    await voice_channel.set_permissions(target_member, overwrite=None)
                    message_text = f"Kicked {target_member.mention}."
        except Exception as e:
            return await interaction.response.send_message(f"Something went wrong while changing the channel -> {e}")

        await interaction.response.edit_message(content=message_text, view=None)


class MemberPicker(discord.ui.View):
    def __init__(self, channel_id: int, action: str):
        super().__init__(timeout=60)
        self.add_item(_MemberSelect(channel_id, action))
