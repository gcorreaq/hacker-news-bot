import os

from mastodon.Mastodon import Mastodon as MastodonClient  # type: ignore

from hacker_news_bot.datasources.hacker_news.definitions import Item
from hacker_news_bot.translator import prepare_toot_message

from .definitions import Toot


class Mastodon:
    client: MastodonClient

    def __init__(self) -> None:
        self.client = MastodonClient(
            api_base_url="https://mastodon.social",
            access_token=os.environ["MASTODON_ACCESS_TOKEN"],
        )

    def create_toot(self, item: Item) -> Toot:
        message = prepare_toot_message(item=item)
        toot: Toot = self.client.status_post(
            status=message,
            visibility="unlisted",
            language="en",
            idempotency_key=item.item_id,
        )
        print(f"Toot {toot}")
        return toot
