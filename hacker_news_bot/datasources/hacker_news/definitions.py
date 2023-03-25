import enum
from dataclasses import dataclass, field
from datetime import datetime

API_BASE_URL: str = "https://hacker-news.firebaseio.com/v0/"
SITE_BASE_URL: str = "https://news.ycombinator.com"


@enum.unique
class ItemType(enum.StrEnum):
    job = enum.auto()
    story = enum.auto()
    comment = enum.auto()
    poll = enum.auto()
    pollopt = enum.auto()


@dataclass
class Item:
    # From the `id` field
    item_id: int
    # From the `type` field
    item_type: ItemType
    # From the `by` field
    author: str
    # From the `time` field
    creation_date: datetime
    score: int
    title: str
    descendants: int | None = None
    text: str | None = None
    url: str | None = None
    deleted: bool = False
    dead: bool = False
    kids: list[int] = field(default_factory=list)
    # Custom property where we set the URL to HN
    item_url: str = field(init=False)

    def __post_init__(self) -> None:
        self.item_url = f"{SITE_BASE_URL}/item?id={self.item_id}"
