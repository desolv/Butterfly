import datetime
from collections import defaultdict
from typing import List, Optional

_logs = defaultdict(list)


def log_error(guild_id: Optional[int], error: Exception, ctx_info: str = "") -> None:
    """
    Store an error log for a guild or globally
    """
    timestamp = datetime.datetime.utcnow().isoformat()
    entry = {
        "time": timestamp,
        "guild_id": guild_id,
        "error": str(error),
        "context": ctx_info,
    }
    _logs[guild_id].append(entry)


def get_logs_for_guild(guild_id: int) -> List[dict]:
    """
    Retrieve all logs for a specific guild
    """
    return list(_logs.get(guild_id, []))


def get_all_logs() -> List[dict]:
    """
    Retrieve all logs across all guilds
    """
    result = []
    for entries in _logs.values():
        result.extend(entries)
    return result
