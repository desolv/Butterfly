from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


@dataclass
class Embed:
    """
    Reference structure for storing embeds in the database (JSONB).
    """
    title: Optional[str] = None
    description: Optional[str] = None
    color: Optional[int] = None
    fields: List[Dict[str, Any]] = field(default_factory=list)
    footer: Optional[str] = None
    thumbnail_url: Optional[str] = None
    image_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a plain dict for JSONB storage.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Embed":
        """
        Rebuild DTO from DB JSONB.
        """
        return cls(**data)
