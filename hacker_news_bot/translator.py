from hacker_news_bot.datasources.hacker_news import Item


def prepare_toot_message(item: Item) -> str:
    message = f"{item.title}\n\n"
    if item.url:
        message = f"{message}Site: {item.url}\n"
    message = f"{message}Discussion: {item.item_url}"
    return message
