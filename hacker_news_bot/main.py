import os
from collections.abc import Iterable

from hacker_news_bot.configure import setup_logger
from hacker_news_bot.datasources.hacker_news import HackerNews, Item
from hacker_news_bot.translator import prepare_toot_message

setup_logger(os.environ.get("LOGLEVEL", "ERROR").upper())


if __name__ == "__main__":
    hn = HackerNews()
    stories: Iterable[Item] = hn.get_new_top_stories(limit=4)
    for story in stories:
        print(f"{prepare_toot_message(story)}\n\n-----\n")
