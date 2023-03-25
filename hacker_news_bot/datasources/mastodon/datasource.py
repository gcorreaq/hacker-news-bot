import logging
import os
import sqlite3

from mastodon.Mastodon import Mastodon as MastodonClient  # type: ignore

from hacker_news_bot.datasources.db import init_db
from hacker_news_bot.datasources.hacker_news.definitions import Item
from hacker_news_bot.translator import prepare_toot_message

from .definitions import Toot

logger = logging.getLogger(__name__)


class Mastodon:
    client: MastodonClient
    db: sqlite3.Connection

    def __init__(self) -> None:
        self.client = MastodonClient(
            api_base_url="https://mastodon.social",
            access_token=os.environ["MASTODON_ACCESS_TOKEN"],
        )
        self.db = init_db()

    def _update_item_record(self, item: Item, toot: Toot) -> None:
        with self.db:
            self.db.execute(
                "UPDATE hn_posts SET toot_id = :toot_id, tooted_at = :tooted_at WHERE id = :id",
                {
                    "toot_id": toot["id"],
                    "tooted_at": toot["created_at"],
                    "id": item.item_id,
                },
            )

    def create_toot(self, item: Item) -> Toot:
        message = prepare_toot_message(item=item)
        toot: Toot = self.client.status_post(
            status=message,
            visibility="unlisted",
            language="en",
            idempotency_key=item.item_id,
        )
        self._update_item_record(item=item, toot=toot)
        logger.debug(f"Toot {toot}")
        return toot
