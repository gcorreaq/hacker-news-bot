import os
from collections.abc import Iterable

from configure import setup_logger
from datasources.hacker_news import HackerNews, Item
from toot_formatter import prepare_toot_message

setup_logger(os.environ.get("LOGLEVEL", "ERROR").upper())


if __name__ == "__main__":
    hn = HackerNews()
    stories: Iterable[Item] = hn.get_new_top_stories(limit=4)
    for story in stories:
        print(f"{prepare_toot_message(story)}\n\n-----\n")
