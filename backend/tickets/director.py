from typing import Sequence, Optional

import discord
from discord import Interaction, PermissionOverwrite, SelectOption, TextChannel
from sqlalchemy.orm import Session

from backend.core.database import Engine
from backend.core.helper import get_time_now, format_time_in_zone, fmt_user, fmt_roles
from backend.core.select_menu import SelectActionList
from backend.tickets.models.ticket import Ticket
from backend.tickets.models.ticket_config import TicketConfig
from backend.tickets.models.ticket_panel import TicketPanel


def create_ticket(
        guild_id: int,
        user_id: int,
        channel_id: int,
        panel_id: str
):
    """
    Create and save a new ticket record
    """
    with Session(Engine) as session:
        ticket = Ticket(
            guild_id=guild_id,
            user_id=user_id,
            channel_id=channel_id,
            panel_id=panel_id
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        return ticket


def create_ticket_panel(guild_id: int, panel_id: str) -> bool:
    """
    Create and save a new ticket panel record.
    """
    panel_id = panel_id.lower()

    with Session(Engine) as session:
        if session.get(TicketPanel, panel_id) is not None:
            return False

        panel = TicketPanel(guild_id=guild_id, panel_id=panel_id)
        session.add(panel)
        session.commit()
        session.refresh(panel)

        return True


def update_or_retrieve_ticket_panel(
        guild_id: int,
        panel_id: str,
        **kwargs
):
    """
        Apply updates for a ticket panel
    """
    panel_id = panel_id.lower()

    panel_keys_map = {
        "panel_name": "name",
        "panel_description": "description",
        "panel_emoji": "emoji",
        "panel_author_url": "author_url",
    }
    ticket_keys_map = {
        "ticket_title": "title",
        "ticket_description": "description"
    }

    with Session(Engine) as session:
        panel = (
            session.query(TicketPanel)
            .filter_by(guild_id=guild_id, panel_id=panel_id)
            .first()
        )
        if panel is None:
            return None

        pe_current = dict(panel.panel_embed or {})
        pe_updates = {}

        if "panel_embed" in kwargs and kwargs["panel_embed"] is not None:
            try:
                pe_updates.update(dict(kwargs["panel_embed"]))
            except Exception:
                pass

        for k, inner in panel_keys_map.items():
            if k in kwargs and kwargs[k] is not None:
                pe_updates[inner] = kwargs[k]

        if pe_updates:
            merged = pe_current.copy()
            merged.update(pe_updates)
            panel.panel_embed = merged

        te_current = dict(panel.ticket_embed or {})
        te_updates = {}

        if "ticket_embed" in kwargs and kwargs["ticket_embed"] is not None:
            try:
                te_updates.update(dict(kwargs["ticket_embed"]))
            except Exception:
                pass

        for k, inner in ticket_keys_map.items():
            if k in kwargs and kwargs[k] is not None:
                te_updates[inner] = kwargs[k]

        if te_updates:
            merged = te_current.copy()
            merged.update(te_updates)
            panel.ticket_embed = merged

        handled = {"panel_embed", "ticket_embed"}
        handled.update(panel_keys_map.keys())
        handled.update(ticket_keys_map.keys())

        for field, value in kwargs.items():
            if field in handled:
                continue
            if value is not None and hasattr(panel, field):
                setattr(panel, field, value)

        session.add(panel)
        session.commit()
        session.refresh(panel)
        return panel


def delete_ticket_panel(guild_id: int, panel_id: str) -> bool:
    """
    Delete a ticket panel
    """
    panel_id = panel_id.lower()

    with Session(Engine) as session:
        panel = session.query(TicketPanel).filter_by(guild_id=guild_id, panel_id=panel_id).first()

        if panel is None:
            return False

        session.delete(panel)
        session.commit()
        return True


def get_user_open_ticket(guild: discord.Guild, user_id: int):
    """
    Check if the user has an open ticket. If a channel is missing, auto-close the ticket and return None.
    """
    with Session(Engine) as session:
        ticket = session.query(Ticket).filter_by(
            guild_id=guild.id,
            user_id=user_id,
            is_closed=False
        ).first()

        if ticket is None:
            return None

        if guild is not None and guild.get_channel(ticket.channel_id) is None:
            ticket.is_closed = True
            ticket.closed_at = get_time_now()
            session.add(ticket)
            session.commit()
            return None

        return ticket


def get_user_tickets(guild_id: int, user_id: int):
    """
    Retrieve a tickets for a user.
    """
    with Session(Engine) as session:
        return session.query(Ticket).filter_by(
            guild_id=guild_id,
            user_id=user_id
        ).all()


def get_ticket_by_channel(guild_id: int, channel_id: int) -> Ticket | None:
    """
    Retrieve a ticket for a given channel.
    """
    with Session(Engine) as session:
        return session.query(Ticket).filter_by(
            guild_id=guild_id,
            channel_id=channel_id
        ).first()


def get_ticket_by_id(guild_id: int, ticket_id: int) -> Ticket | None:
    """
    Retrieve a ticket for a given ID.
    """
    with Session(Engine) as session:
        return session.query(Ticket).filter_by(
            guild_id=guild_id,
            ticket_id=ticket_id
        ).first()


def mark_ticket_closed(guild_id: int, channel_id: int, closed_by: int):
    """
    Mark a ticket as closed and return a refreshed, detached instance.
    """
    with Session(Engine) as session:
        ticket = session.query(Ticket).filter_by(
            guild_id=guild_id,
            channel_id=channel_id
        ).first()

        if ticket is None:
            return None

        if not ticket.is_closed:
            ticket.is_closed = True
            ticket.closed_at = get_time_now()
            ticket.closed_by = closed_by
            session.add(ticket)
            session.commit()

        session.refresh(ticket)
        session.expunge(ticket)
        return ticket


def get_panels_for_guild(guild_id: int):
    """
    Retrieve all panel entries for the given guild.
    """
    with Session(Engine) as session:
        return session.query(TicketPanel).filter_by(guild_id=guild_id).all()


def update_or_retrieve_ticket_config(guild_id: int, **kwargs):
    """
        Apply updates for a ticket config
    """
    with Session(Engine) as session:
        config = session.query(TicketConfig).filter_by(guild_id=guild_id).first()

        if not config:
            config = TicketConfig(guild_id=guild_id)

            session.add(config)
            session.commit()
            session.refresh(config)

        embed_updates = {}
        if "embed_title" in kwargs or "embed_description" in kwargs:
            embed_updates["title"] = kwargs.get("embed_title", config.panel_embed.get("title"))
            embed_updates["description"] = kwargs.get("embed_description", config.panel_embed.get("description"))
            config.panel_embed = embed_updates

        for field, value in kwargs.items():
            if field in ("embed_title", "embed_description"):
                continue
            if value is not None and hasattr(config, field):
                setattr(config, field, value)

        session.add(config)
        session.commit()
        session.refresh(config)

        return config


def build_panel_list_view(guild_id: int, panels: list[TicketPanel]) -> SelectActionList:
    """
    Build the dropdown that lists all panels
    """
    options = [
        SelectOption(
            label=panel.panel_embed.get("name") or panel.panel_id,
            value=f"tickets.open:{panel.panel_id}",
            description=panel.panel_embed.get("description"),
            emoji=panel.panel_embed.get("emoji")
        )
        for panel in panels
    ]

    async def on_select(interaction: Interaction, values: Sequence[str]) -> None:
        await handle_ticket_panel_selection(interaction, values)

    panel_embed = update_or_retrieve_ticket_config(guild_id).panel_embed

    return SelectActionList(
        embed_title=panel_embed.get("title"),
        embed_description=panel_embed.get("description"),
        options=options,
        on_select=on_select,
        timeout=None,
        custom_id="tickets.menu"
    )


async def handle_ticket_panel_selection(interaction: Interaction, values: Sequence[str]):
    if not values:
        return await interaction.followup.send("No options selected...", ephemeral=True)

    try:
        action, panel_id = values[0].split(":", 1)
    except ValueError:
        return await interaction.followup.send("Invalid selection!", ephemeral=True)

    if action != "tickets.open":
        return await interaction.followup.send("Unknown action!", ephemeral=True)

    panel = update_or_retrieve_ticket_panel(interaction.guild.id, panel_id)
    if not panel or not panel.is_enabled:
        return await interaction.followup.send("That panel is not available!", ephemeral=True)

    if any(role.id in panel.staff_role_ids for role in interaction.user.roles):
        return await interaction.followup.send("Staff is not allowed to open own ticket!", ephemeral=True)

    if not any(role.id in panel.required_role_ids for role in interaction.user.roles):
        return await interaction.followup.send("You are not allowed to open this ticket!", ephemeral=True)

    has_ticket = get_user_open_ticket(interaction.guild, interaction.user.id)
    if has_ticket:
        has_channel = interaction.guild.get_channel(has_ticket.channel_id)
        has_channel = has_channel.mention if has_channel else has_ticket.channel_id
        return await interaction.followup.send(f"You currently have an open ticket at {has_channel}!", ephemeral=True)

    try:
        channel = await create_ticket_channel(interaction.guild, interaction.user, panel)
        if channel is None:
            return await interaction.followup.send(
                "Something went wrong while creating the ticket. I'm missing the category id!",
                ephemeral=True)

        await send_ticket_embed(interaction, channel, panel)
    except Exception as e:
        print(f"Something went wrong while creating ticket <{interaction.guild.id} - {interaction.user.id}> -> {e}")
        return await interaction.followup.send(
            "Something went wrong while creating the ticket. Contact an administrator!",
            ephemeral=True)

    ticket = create_ticket(
        guild_id=interaction.guild.id,
        user_id=interaction.user.id,
        channel_id=channel.id,
        panel_id=panel_id
    )

    await send_ticket_logging(interaction.guild, ticket)


async def create_ticket_channel(guild: discord.Guild, user: discord.Member | discord.User,
                                panel: Optional[TicketPanel]) -> TextChannel | None:
    overwrites: dict[discord.Role | discord.Member, discord.PermissionOverwrite] = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        )
    }

    member = guild.get_member(user.id) or user
    overwrites[member] = PermissionOverwrite(
        view_channel=True,
        send_messages=True,
        read_message_history=True
    )

    for role_id in (panel.staff_role_ids or []):
        role = guild.get_role(int(role_id))
        if role:
            overwrites[role] = PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

    parent = None
    if panel.category_id:
        category = guild.get_channel(panel.category_id)
        if category and category.type is discord.ChannelType.category:
            parent = category

    channel_name = f"ticket-{user.name}".lower().replace(" ", "-")

    if parent:
        return await parent.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            reason="Open ticket"
        )
    return None


async def send_ticket_embed(interaction: Interaction, channel: discord.TextChannel,
                            panel: Optional[TicketPanel]) -> None:
    embed_title = panel.ticket_embed.get("title").replace("user%", interaction.user.mention)
    author_url = panel.ticket_embed.get("author_url")

    embed = discord.Embed(
        title=embed_title if not author_url else "",
        description=panel.ticket_embed.get("description"),
        color=0x393A41,
        timestamp=get_time_now(),
    )

    if author_url:
        avatar_url = interaction.user.avatar.url if interaction.user.avatar is not None else "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_author(name=embed_title or panel.panel_id, icon_url=avatar_url)

    from backend.tickets.models.ticket_close_button import TicketCloseButton
    await channel.send(embed=embed, view=TicketCloseButton())

    await channel.send(f"{fmt_roles(panel.mention_role_ids)}{interaction.user.mention}", delete_after=1)
    await interaction.followup.send(f"Created a new ticket at {channel.mention}!", ephemeral=True)


async def send_ticket_logging(guild: discord.Guild, ticket: Ticket):
    """
    Send a ticket log embed to the panels logging channel
    """
    if ticket is None:
        return

    panel = update_or_retrieve_ticket_panel(guild.id, ticket.panel_id)

    if not panel or not panel.logging_channel_id:
        return

    logging_channel = guild.get_channel(panel.logging_channel_id)

    if logging_channel is None:
        return

    description = (
        f"**ᴛɪᴄᴋᴇᴛ ɪᴅ**: **{ticket.ticket_id}**\n"
        f"**ᴘᴀɴᴇʟ ɪᴅ**: **{panel.panel_id}**\n"
        f"**ᴄʜᴀɴɴᴇʟ ɪᴅ**: {ticket.channel_id}\n"
        f"**ᴄʀᴇᴀᴛᴇᴅ ᴀᴛ**: {format_time_in_zone(ticket.created_at)}\n\n"
    )

    if ticket.is_closed:
        description += (
            f"**ᴄʟᴏѕᴇᴅ ᴀᴛ**: {format_time_in_zone(ticket.closed_at)}\n"
            f"**ᴄʟᴏѕᴇᴅ ʙʏ**: {fmt_user(ticket.closed_by)}\n"
        )

    member = guild.get_member(ticket.user_id)
    embed_color, embed_status = (discord.Color.red(), "ᴄʟᴏѕᴇᴅ") if ticket.is_closed else (discord.Color.green(),
                                                                                          "ᴏᴘᴇɴᴇᴅ")

    embed = discord.Embed(
        title=f"ᴛɪᴄᴋᴇᴛ {embed_status} ꜰᴏʀ @{member if member else ticket.user_id}",
        description=description,
        color=embed_color,
        timestamp=get_time_now(),
    )

    avatar_url = member.avatar.url if member.avatar is not None else "https://cdn.discordapp.com/embed/avatars/0.png"
    embed.set_thumbnail(url=avatar_url)

    await logging_channel.send(embed=embed)
