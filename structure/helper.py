from datetime import datetime
import pytz


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
