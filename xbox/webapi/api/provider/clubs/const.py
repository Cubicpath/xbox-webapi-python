"""Web API Constants."""

from typing import Final

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
