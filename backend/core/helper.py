import json
import random
import re
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Sequence, Type
from urllib.parse import urlparse

import discord
import pytz
from dateutil.parser import isoparse
from discord.ext import commands


def get_current_time(format: str = "%d %B %Y %H:%M", timezone: str = "Europe/London") -> str:
    """
    Return the current time formatted according to the given format and timezone
    """
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    return now.strftime(format)


def format_time_in_zone(time: datetime, format: str = "%d/%m/%y %H:%M", timezone: str = "Europe/London") -> str:
    """
    Render a datetime in the given timezone. Naive inputs are treated as UTC.
    """
    target_tz = pytz.timezone(timezone)
    if time.tzinfo is None:
        aware = pytz.utc.localize(time)
    else:
        aware = time.astimezone(pytz.utc)
    return aware.astimezone(target_tz).strftime(format)


def get_time_now(timezone: str = "Europe/London") -> datetime:
    """
    Return the current datetime in the specified timezone
    """
    tz = pytz.timezone(timezone)
    return datetime.now(tz)


def load_json_data(path: str) -> dict:
    """
    Load and return JSON data from a file in the io directory
    """
    file_path = Path(f"io/{path}.json")
    if not file_path.exists():
        raise FileNotFoundError(f"IO file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_time_window(input_str: str) -> datetime:
    """
    Parse a duration string (e.g., '1d', '3h', '30m') and return a future UTC datetime.
    """
    match = re.match(r"(\d+)([dhm])", input_str.strip().lower())
    if not match:
        raise ValueError("Invalid time format. Use like '1d', '7d', or '3h'.")

    value, unit = match.groups()
    value = int(value)
    now = get_time_now()

    if unit == "d":
        return now + timedelta(days=value)
    if unit == "h":
        return now + timedelta(hours=value)
    if unit == "m":
        return now + timedelta(minutes=value)

    raise ValueError("Only 'd' (days), 'h' (hours) and 'm' (minutes) are supported.")


def format_time_window(target: datetime) -> str:
    """
    Given a UTC datetime (naive or aware), return a duration string like '1d', '3h', or '30m'.
    If the target is in the past or now, returns '0m'.
    """
    if target.tzinfo is None:
        target = target.replace(tzinfo=timezone.utc)
    else:
        target = target.astimezone(timezone.utc)

    now = get_time_now()

    delta: timedelta = target - now
    total_seconds = int(delta.total_seconds())

    if total_seconds <= 0:
        return "0s"

    days = total_seconds // 86400
    if days >= 1:
        return f"{days}d"

    hours = total_seconds // 3600
    if hours >= 1:
        return f"{hours}h"

    minutes = (total_seconds % 3600) // 60
    if minutes >= 1:
        return f"{minutes}m"

    seconds = total_seconds % 60
    return f"{seconds}s"


def format_duration(start: datetime, end: datetime) -> str:
    """
    Given two UTC datetimes return the difference as
    'Xd', 'Xh', or 'Xm'
    """

    def ensure_utc(dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    start_utc = ensure_utc(start)
    end_utc = ensure_utc(end)

    delta: timedelta = end_utc - start_utc
    total_seconds = int(delta.total_seconds())

    if total_seconds <= 0:
        return "0s"

    days = total_seconds // 86400
    if days >= 1:
        return f"{days}d"

    hours = total_seconds // 3600
    if hours >= 1:
        return f"{hours}h"

    minutes = (total_seconds % 3600) // 60
    if minutes >= 1:
        return f"{minutes}m"

    seconds = total_seconds % 60
    return f"{seconds}s"


def get_commands_help_messages(
        bot: commands.Bot,
        cog_classes: Sequence[Type[commands.Cog]],
        is_admin: bool
) -> List[str]:
    """
    Given a list of Cog classes and a command context, return a flat list of
    help lines (usage + description) for every command and subcommand in each
    loaded instance. Hidden commands/groups are only shown if ctx.author is
    a guild administrator, and are marked with a '*' prefix.
    """
    lines: List[str] = []

    def recurse(group: commands.Group, prefix: str):
        if group.hidden and not is_admin:
            return

        for sub in group.commands:
            if sub.hidden and not is_admin:
                continue

            star_sub = "*" if sub.hidden else ""
            params = " ".join(f"<{p}>" for p in sub.clean_params)
            usage = f"{star_sub}{prefix}{sub.name} {params}".strip()
            desc = sub.help or sub.description or "No description"

            if isinstance(sub, commands.Group):
                if getattr(sub, "invoke_without_command", False):
                    lines.append(f"`{usage}` – {desc}")
                recurse(sub, f"{prefix}{sub.name} ")
            else:
                lines.append(f"`{usage}` – {desc}")

    for cog_cls in cog_classes:
        cog = bot.get_cog(cog_cls.__name__)
        if not cog:
            continue

        for cmd in cog.get_commands():
            if cmd.hidden and not is_admin:
                continue

            star_cmd = "*" if cmd.hidden else ""
            if isinstance(cmd, commands.Group):
                if getattr(cmd, "invoke_without_command", False):
                    recurse(cmd, f"{star_cmd}{cmd.name} ")
                else:
                    recurse(cmd, f"{star_cmd}{cmd.name} ")
            else:
                params = " ".join(f"<{p}>" for p in cmd.clean_params)
                usage = f"{star_cmd}{cmd.name} {params}".strip()
                desc = cmd.help or cmd.description or "No description"
                lines.append(f"`{usage}` – {desc}")

    return lines


def generate_id(length: int = 12, symbols: bool = True) -> str:
    """
    Generate a random identifier string of given length, optionally including symbols.
    """
    chars = string.ascii_letters + string.digits
    if symbols:
        chars += "#@$&"
    return ''.join(random.choices(chars, k=length))


async def send_private_dm(member: discord.Member, message: str, ctx=None) -> bool:
    """
    Attempt to send a private DM to a member; notify context on failure.
    """
    try:
        await member.send(message)
        return True
    except Exception:
        if ctx:
            await ctx.reply(f"Wasn't able to message **{member}**.")
        return False


def is_valid_url(url: str) -> bool:
    """
    Validate a URL string ensuring it has a proper scheme and netloc.
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def parse_iso(iso_str: str) -> datetime:
    """
    Parse an ISO string to a naive local datetime.
    """
    dt_aware = isoparse(iso_str)
    dt_local = dt_aware.astimezone()
    return dt_local.replace(tzinfo=None)


def is_valid_command(bot: commands.Bot, name: str) -> bool:
    """
    Determine whether a given command name is registered on the bot.
    """
    return bot.get_command(name) is not None


def get_all_command_names(bot: commands.Bot, include_hidden: bool = False) -> List[str]:
    """
    Gather every command’s qualified_name, including subcommands.
    """
    names: List[str] = []

    def recurse(group: commands.Command, prefix: str = ""):
        if getattr(group, "hidden", False) and not include_hidden:
            return

        qualified = f"{prefix}{group.name}"
        names.append(qualified)

        if isinstance(group, commands.Group):
            for sub in group.commands:
                recurse(sub, prefix=f"{qualified} ")

    for cmd in bot.commands:
        recurse(cmd)

    seen = set()
    unique = []
    for n in names:
        if n not in seen:
            seen.add(n)
            unique.append(n)

    return unique
