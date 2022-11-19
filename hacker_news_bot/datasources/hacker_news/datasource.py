import logging
import sqlite3
from collections.abc import Iterable

import arrow

from hacker_news_bot.datasources.hacker_news.api import Api
from hacker_news_bot.datasources.hacker_news.definitions import Item

logger = logging.getLogger(__name__)


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
        return any(results)

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
