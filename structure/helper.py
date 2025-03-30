from datetime import datetime, timezone
import pytz
import time


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
