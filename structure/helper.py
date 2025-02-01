from datetime import datetime
import pytz


def get_time():
    london_tz = pytz.timezone('Europe/London')
    london_time = datetime.now(london_tz)
    return london_time.strftime('%d %B %Y %H:%M %Z')
