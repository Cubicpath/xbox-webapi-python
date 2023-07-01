"""Web API Constants."""

from typing import Dict, Final, Union

from xbox.webapi.api.provider.clubs.models import ClubRole

DEFAULT_SETTINGS_OPEN: Final[Dict[str, Union[str, bool]]] = {
    "preferred_locale": "en-US",
    "request_to_join_enabled": True,
    "who_can_post_to_feed": ClubRole.MEMBER,
    "who_can_invite": ClubRole.MODERATOR,
    "who_can_chat": ClubRole.MEMBER,
    "who_can_create_lfg": ClubRole.MEMBER,
    "who_can_join_lfg": ClubRole.NONMEMBER,
    "mature_content_enabled": True,
    "watch_club_titles_only": False,
}

DEFAULT_SETTINGS_CLOSED: Final[
    Dict[str, Union[str, bool]]
] = DEFAULT_SETTINGS_OPEN.copy()

DEFAULT_SETTINGS_SECRET: Final[Dict[str, Union[str, bool]]] = DEFAULT_SETTINGS_OPEN | {
    "request_to_join_enabled": False,
    "who_can_join_lfg": ClubRole.MEMBER,
}


COMMUNICATION_TAGS: Final[frozenset] = frozenset(
    (
        "kidfriendlycontentonly",
        "allcontentok",
        "textchatrequired",
        "nomic",
        "micoptional",
        "micrequired",
        "notrashtalking",
        "trashtalkingok",
        "noswearing",
        "swearingok",
    )
)

PLAY_STYLE_TAGS: Final[frozenset] = frozenset(
    (
        "newplayerswelcome",
        "willhelpnewplayers",
        "experiencedplayersonly",
        "casual",
        "competitive",
        "cooperative",
        "playervsplayer",
        "achievementhunting",
        "tournament",
    )
)

PEOPLE_TAGS: Final[frozenset] = frozenset(
    (
        "adultsonly",
        "allages",
        "everyoneiswelcome",
    )
)

CLUB_TAGS: Final[frozenset] = frozenset.union(
    COMMUNICATION_TAGS, PLAY_STYLE_TAGS, PEOPLE_TAGS
)
