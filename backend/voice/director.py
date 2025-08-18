import discord
from sqlalchemy.orm import Session

from backend.core.database import Engine
from backend.voice.models.voice import Voice
from backend.voice.models.voice_config import VoiceConfig


def create_voice(
        guild_id: int,
        user_id: int,
        channel_id: int
):
    """
    Create and save a new voice record
    """
    with Session(Engine) as session:
        voice = Voice(
            guild_id=guild_id,
            user_id=user_id,
            channel_id=channel_id
        )

        session.add(voice)
        session.commit()
        session.refresh(voice)

        return voice


def delete_voice(channel_id: int):
    with Session(Engine) as session:
        voice = session.query(Voice).filter_by(channel_id=channel_id).first()

        if voice:
            session.delete(voice)
            session.commit()


def create_or_update_voice_config(guild_id: int, **kwargs):
    """
    Apply updates for voice config
    """
    with Session(Engine) as session:
        config = session.query(VoiceConfig).filter_by(guild_id=guild_id).first()

        if not config:
            config = VoiceConfig(guild_id=guild_id)

        embed_updates = {}
        if "embed_title" in kwargs:
            embed_updates["title"] = kwargs.pop("embed_title")
        if "embed_description" in kwargs:
            embed_updates["description"] = kwargs.pop("embed_description")

        if embed_updates:
            current = getattr(config, "embed") or {}
            setattr(config, "embed", {**current, **embed_updates})

        for field, value in kwargs.items():
            if value is not None and hasattr(config, field):
                setattr(config, field, value)

        session.add(config)
        session.commit()
        session.refresh(config)

        return config


def get_voice_by_channel(guild_id: int, channel_id: int):
    """
    Retrieve a voice obj by channel
    """
    with Session(Engine) as session:
        return session.query(Voice).filter_by(guild_id=guild_id, channel_id=channel_id).first()


def get_user_active_voice(guild_id: int, user_id: int):
    """
    Retrieve a user open ticket
    """
    with Session(Engine) as session:
        return session.query(Voice).filter_by(
            guild_id=guild_id,
            user_id=user_id,
            is_deleted=False
        ).first()


def is_controller(member: discord.Member, config: VoiceConfig, voice: Voice) -> bool:
    """
    Allow channel's owner and staff to manage
    """
    if member.id == voice.user_id:
        return True

    return any(role.id in config.staff_role_ids for role in member.roles)


def is_banned(member: discord.Member, config: VoiceConfig) -> bool:
    """
    Check if user is banned from creating a voice channel
    """
    return (any(role.id in config.banned_role_ids for role in member.roles)
            or member.id in config.banned_user_ids)


async def handle_voice_channel_selection(interaction: discord.Interaction):
    voice_state = interaction.user.voice
    if not voice_state or not voice_state.channel:
        await interaction.response.send_message("You are not in a voice channel.", ephemeral=True)
        return None, None

    voice_config = create_or_update_voice_config(interaction.guild.id)
    if not voice_config.is_enabled:
        await interaction.response.send_message("Voice system is currently disabled.", ephemeral=True)
        return None, None

    if is_banned(interaction.user, voice_config):
        await interaction.response.send_message("You are not allowed to use this system.", ephemeral=True)
        return None, None

    voice_channel = interaction.user.voice.channel
    voice = get_voice_by_channel(interaction.guild.id, voice_channel.id)
    if not voice:
        await interaction.response.send_message("You must be in a managed voice channel.", ephemeral=True)
        return None, None

    if not is_controller(interaction.user, voice_config, voice):
        await interaction.response.send_message("You are not allowed to manage this channel.", ephemeral=True)
        return None, None

    return voice_channel, voice
