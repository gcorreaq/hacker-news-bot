import argparse
import os
from collections.abc import Iterable

from hacker_news_bot.configure import setup_logger
from hacker_news_bot.datasources.hacker_news import HackerNews, Item
from hacker_news_bot.datasources.mastodon import Mastodon
from hacker_news_bot.translator import prepare_toot_message

setup_logger(os.environ.get("LOGLEVEL", "ERROR").upper())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gets the latest top stories from HN and posts them to Mastodon",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=10, help="Number of stories to retrieve from Hacker News"
    )
    parser.add_argument("--dry-run", action="store_true", help="Runs, but do not post to Mastodon")
    args = parser.parse_args()

    hn = HackerNews()
    mastodon = Mastodon()
    stories: Iterable[Item] = hn.get_new_top_stories(limit=args.limit)
    for story in stories:
        print(f"{prepare_toot_message(story)=}\n\n-----\n")
        if not args.dry_run:
            mastodon.create_toot(story)
