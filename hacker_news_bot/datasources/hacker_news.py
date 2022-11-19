import enum
import logging
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime

import arrow
import requests

logger = logging.getLogger(__name__)
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


def _transform_response(response: requests.Response) -> Item:
    json_response = response.json()
    logger.debug("Transforming JSON response: %r", json_response)
    json_response["item_id"] = str(json_response["id"])
    json_response["item_type"] = ItemType(json_response["type"])
    json_response["author"] = json_response["by"]
    json_response["creation_date"] = arrow.get(json_response["time"])

    forbidden_keys = ["id", "type", "by", "time"]
    for key in forbidden_keys:
        try:
            del json_response[key]
        except KeyError:
            pass

    return Item(**json_response)


class Api:
    session: requests.Session

    def __init__(self) -> None:
        self.session = requests.Session()

    def _fetch(self, object_name: str, object_id: str | None = None) -> requests.Response:
        url = object_name
        if object_id:
            url = f"{url}/{object_id}"
        final_url = f"{API_BASE_URL}{url}.json"
        response = self.session.get(final_url)
        logger.debug("Response from API: %r", response)
        response.raise_for_status()
        return response

    def _get_item(self, item_id: str) -> Item:
        response = self._fetch("item", item_id)
        item = _transform_response(response)
        logger.debug("Resulting item: %r", item)
        return item

    def top_stories(self, limit: int | None = None) -> Iterable[Item]:
        item_ids: list[int] = self._fetch("topstories").json()
        story_count = 0
        for item_id in item_ids:
            item = self._get_item(str(item_id))
            if item.item_type != ItemType.story:
                continue
            story_count += 1
            yield item

            if limit and story_count >= limit:
                break

    # TODO: Do we need updates?


class HackerNews:
    api: Api
    db: sqlite3.Connection

    def __init__(self) -> None:
        self.api = Api()
        self.db = sqlite3.connect(":memory:")
        with self.db:
            self.db.execute(
                """CREATE TABLE IF NOT EXISTS hn_posts(
                    id PRIMARY_KEY,
                    stored_at,
                    created_at,
                    updated_at
                )"""
            )

    def story_already_posted(self, story: Item) -> bool:
        results = self.db.execute(
            "SELECT id FROM hn_posts WHERE id = :id LIMIT 1", {"id": story.item_id}
        )
        return len(list(results)) > 0

    def store_new_story(self, story: Item) -> None:
        with self.db:
            self.db.execute(
                "INSERT INTO hn_posts VALUES (:id, :stored_at, :created_at, :updated_at)",
                {
                    "id": story.item_id,
                    "stored_at": arrow.utcnow().timestamp(),
                    "created_at": story.creation_date.timestamp(),
                    "updated_at": story.creation_date.timestamp(),
                },
            )

    def get_new_top_stories(self, limit: int | None = None) -> Iterable[Item]:
        """Recover top stories with an optional limit

        :param limit: The number of top stories to return. Note that this will not
            reduce the number of items that are fecth from the API, but when the
            iterator will stop returning results.
        """
        top_stories = self.api.top_stories(limit=limit)
        for story in top_stories:
            if self.story_already_posted(story):
                continue

            self.store_new_story(story)
            yield story
