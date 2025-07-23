import json
import random
import re
import string
import time
from datetime import datetime, timedelta
from datetime import timezone
from pathlib import Path
from typing import List

import discord
import pytz
from discord.ext import commands


def get_time(format: str = "%d %B %Y %H:%M %Z", timezone: str = "Europe/London"):
    tz = pytz.timezone(timezone)
    time = datetime.now(tz)
    return time.strftime(format)


def get_uptime(bot, format: str = "%d %B %Y %H:%M %Z", timezone: str = "Europe/London"):
    master_cog = bot.get_cog("MasterCog")
    if not master_cog:
        return "MasterCog not loaded."

    start_time = master_cog.get_uptime()
    tz = pytz.timezone(timezone)
    localized_start = tz.localize(start_time)

    return localized_start.strftime(format)


def get_formatted_time(time, format: str = "%d %B %Y %H:%M %Z", timezone: str = "Europe/London"):
    tz = pytz.timezone(timezone)
    localized_start = tz.localize(time)

    return localized_start.strftime(format)


def get_millis() -> int:
    return int(time.time() * 1000)


def convert_millis_to_formatted(ms: int, format: str, zone: str) -> str:
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    return get_formatted_time(dt, format, zone)


def load_json_data(path: str) -> dict:
    path = Path(f"io/{path}.json")

    if not path.exists():
        raise FileNotFoundError(f"IO file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_time_window(input_str: str) -> datetime:
    match = re.match(r"(\d+)([dhm])", input_str.strip().lower())
    if not match:
        raise ValueError("Invalid time format. Use like '1d', '7d', or '3h'.")

    value, unit = match.groups()
    value = int(value)

    now = datetime.utcnow()
    if unit == "d":
        return now - timedelta(days=value)
    elif unit == "h":
        return now - timedelta(hours=value)
    elif unit == "m":
        return now - timedelta(minutes=value)
    else:
        raise ValueError("Only 'd' (days), 'h' (hours) and 'm' (minutes) are supported.")


def format_subcommands(bot, group_name: str) -> List[str]:
    cmd_obj = bot.get_command(group_name)
    if not cmd_obj or not isinstance(cmd_obj, commands.Group):
        return []

    lines: List[str] = []
    for sub in cmd_obj.commands:
        if sub.hidden:
            continue

        params = " ".join(f"<{name}>" for name in sub.clean_params)
        usage = f"{sub.name} {params}".strip()

        lines.append(f"`{usage}` – {sub.description or 'No description'}")

    return lines


def generate_id(length=9, symbols=True):
    chars = string.ascii_letters + string.digits
    if symbols:
        chars += "#@$&"

    return ''.join(random.choices(chars, k=length))


async def send_private_dm(member: discord.Member, message, ctx = None):
    try:
        await member.send(message)
        return True
    except Exception:
        if ctx is not None:
            await ctx.send(f"Wasn't able to message **{member}**.")
        return False