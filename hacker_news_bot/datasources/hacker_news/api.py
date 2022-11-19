import logging
from collections.abc import Iterable

import arrow
import requests

from hacker_news_bot.datasources.hacker_news.definitions import API_BASE_URL, Item, ItemType

logger = logging.getLogger(__name__)


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

    def _fetch(self, url: str) -> requests.Response:
        response = self.session.get(url)
        logger.debug("Response from API: %r", response)
        response.raise_for_status()
        return response

    def _fetch_objects(self, object_name: str) -> requests.Response:
        url = f"{API_BASE_URL}{object_name}.json"
        return self._fetch(url)

    def _fetch_object_by_id(self, object_name: str, object_id: str) -> requests.Response:
        url = f"{API_BASE_URL}{object_name}/{object_id}.json"
        return self._fetch(url)

    def _get_item(self, item_id: str) -> Item:
        response = self._fetch_object_by_id("item", item_id)
        item = _transform_response(response)
        logger.debug("Resulting item: %r", item)
        return item

    def top_stories(self, limit: int | None = None) -> Iterable[Item]:
        item_ids: list[int] = self._fetch_objects("topstories").json()
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
