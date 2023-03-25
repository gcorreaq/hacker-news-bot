from datetime import datetime
from enum import StrEnum, auto, unique
from typing import TypedDict


@unique
class TootVisibility(StrEnum):
    public = auto()
    unlisted = auto()
    private = auto()
    direct = auto()


class Toot(TypedDict):
    # Numerical id of this toot
    id: int
    # Descriptor for the toot
    # EG 'tag:mastodon.social,2016-11-25:objectId=<id>:objectType=Status'
    uri: str
    # URL of the toot
    url: str
    # User dict for the account which posted the status
    # account:
    # Numerical id of the toot this toot is in response to
    in_reply_to_id: int
    # Denotes whether the toot is a reblog. If so, set to the original toot dict.
    reblog: dict[str, str] | None
    # Content of the toot, as HTML: '<p>Hello from Python</p>'
    content: str
    # Creation time
    created_at: datetime
    # Number of reblogs
    reblogs_count: int
    # Number of favourites
    favourites_count: int
    # Denotes whether the logged in user has boosted this toot
    reblogged: bool
    # Denotes whether the logged in user has favourited this toot
    favourited: bool
    # Denotes whether media attachments to the toot are marked sensitive
    sensitive: bool
    # Warning text that should be displayed before the toot content
    spoiler_text: str
    # Toot visibility ('public', 'unlisted', 'private', or 'direct')
    visibility: TootVisibility
    # A list of users dicts mentioned in the toot, as Mention dicts
    # mentions:
    # A list of media dicts of attached files
    # media_attachments:
    # A list of custom emojis used in the toot, as Emoji dicts
    # emojis:
    # A list of hashtag used in the toot, as Hashtag dicts
    # tags:
    # True if the status is bookmarked by the logged in user, False if not.
    bookmarked: bool
    # Application dict for the client used to post the toot (Does not federate and is therefore
    # always None for remote toots, can also be None for local toots for some legacy applications).
    # application:
    # The language of the toot, if specified by the server, as ISO 639-1 (two-letter) language code.
    language: str
    # Boolean denoting whether the user has muted this status by way of conversation muting
    muted: bool
    # Boolean denoting whether or not the status is currently pinned for the associated account.
    pinned: bool
    # The number of replies to this status.
    replies_count: int
    # A preview card for links from the status, if present at time of delivery, as card dict.
    # card:
    # A poll dict if a poll is attached to this status.
    # poll:
