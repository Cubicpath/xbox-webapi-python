from datetime import datetime
from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from xbox.webapi.api.provider.clubs import ClubRole
from xbox.webapi.common.models import CamelCaseModel


class AchievementType(str, Enum):
    UNKNOWN = "Unknown"
    PERSISTENT = "Persistent"


class ActivityItemType(str, Enum):
    UNKNOWN = "Unknown"
    PLAYED = "Played"
    FOLLOWED = "Followed"
    TEXT_POST = "TextPost"
    USER_POST = "UserPost"
    ACHIEVEMENT = "Achievement"
    SCREENSHOT = "Screenshot"
    CLIP = "GameDVR"
    BROADCAST_START = "BroadcastStart"
    BROADCAST_END = "BroadcastEnd"
    GAMERTAG_CHANGED = "GamertagChanged"


class AuthorType(str, Enum):
    UNKNOWN = "Unknown"
    USER = "User"


class ContentType(str, Enum):
    UNKNOWN = "Unknown"
    SYSTEM = "System"
    CHAT = "Chat"
    GAME = "Game"


class LocatorType(str, Enum):
    UNKNOWN = "Unknown"
    DOWNLOAD = "Download"
    THUMBNAIL_SMALL = "Thumbnail_Small"
    THUMBNAIL_LARGE = "Thumbnail_Large"


class MessageStatus(str, Enum):
    UNKNOWN = "Unknown"
    OK = "Ok"
    DELETED = "Deleted"  # flag 1


class MessageType(str, Enum):
    UNKNOWN = "Unknown"
    BASIC_TEXT = "BasicText"  # flag 0
    RICH_TEXT = "RichText"  # flag 16
    DIRECT_MENTION = "DirectMention"  # flag 20
    MOTD = "MessageOfTheDay"  # flag 0


class PostType(str, Enum):
    UNKNOWN = "Unknown"
    LINK = "Link"


class LinkType(str, Enum):
    UNKNOWN = "Unknown"
    DEFAULT = "Default"


class TimelineType(str, Enum):
    UNKNOWN = "Unknown"
    CLUB = "Club"


class RarityCategory(str, Enum):
    UNKNOWN = "Unknown"
    RARE = "Rare"


class Report(CamelCaseModel):
    reporting_xuid: str
    text_reason: str


class ReportedItem(CamelCaseModel):
    content_id: str
    content_type: ContentType
    last_reported: datetime
    report_count: int
    report_id: str
    reports: List[Report]


class UserPostDetails(CamelCaseModel):
    link: str
    display_link: str
    title: str
    description: str
    link_type: LinkType
    link_data: Optional[Any]


class PreferredColor(CamelCaseModel):
    primary_color: Optional[str]
    secondary_color: Optional[str]
    tertiary_color: Optional[str]


class AuthorInfo(CamelCaseModel):
    author_type: AuthorType
    color: PreferredColor
    image_url: str
    modern_gamertag: str
    modern_gamertag_suffix: str
    name: str
    second_name: str
    show_as_avatar: str


class Message(CamelCaseModel):
    protocol_version: int
    message_id: str
    message_time: datetime
    message_type: MessageType
    sender_xuid: str
    sender_gamertag: str
    client_seq_num: int
    message: str
    message_status: MessageStatus
    flags: int


class Timeline(CamelCaseModel):
    timeline_id: str
    timeline_type: TimelineType
    timeline_name: str
    timeline_image: str


class ClubTimeline(Timeline):
    is_official_club: bool
    author_roles: List[ClubRole]
    is_public: bool


class GameMediaContentLocator(CamelCaseModel):
    expiration: Optional[datetime]
    file_size: Optional[int]
    locator_type: Optional[LocatorType]
    uri: Optional[str]


class ActivityItem(CamelCaseModel):
    bing_id: Optional[UUID]
    content_image_uri: Optional[str]
    content_title: Optional[str]
    game_media_content_locators: Optional[List[GameMediaContentLocator]]
    platform: Optional[str]  # Platform item was posted from
    title_id: Optional[str]
    upload_title_id: Optional[str]
    description: str
    date: datetime
    has_ugc: bool
    activity_item_type: ActivityItemType
    content_type: ContentType
    short_description: str
    ugc_caption: Optional[str]
    item_text: str
    item_image: str
    trusted_item_image: Optional[bool]
    share_root: str
    feed_item_id: str
    item_root: str
    view_count: Optional[int]
    num_likes: Optional[int]
    num_comments: Optional[int]
    num_shares: Optional[int]
    num_views: Optional[int]
    has_liked: bool
    author_info: AuthorInfo
    user_xuid: str


class AchievementActivityItem(ActivityItem):
    achievement_description: str
    achievement_icon: str
    achievement_id: str
    achievement_name: str
    achievement_scid: UUID
    achievement_type: str
    gamerscore: int
    has_app_award: bool
    has_art_award: bool
    is_secret: bool
    rarity_category: str
    rarity_percentage: str


class ClipActivityItem(ActivityItem):
    clip_caption: str
    clip_id: UUID
    clip_name: str
    clip_scid: UUID
    clip_thumbnail: str
    date_recorded: datetime
    duration_in_seconds: str


class ScreenshotActivityItem(ActivityItem):
    screenshot_id: UUID
    screenshot_name: str
    screenshot_scid: UUID
    screenshot_thumbnail: str
    screenshot_uri: str


class UserPostActivityItem(ActivityItem):
    post_type: PostType
    post_details: UserPostDetails
    timeline: ClubTimeline


class FeedResponse(CamelCaseModel):
    num_items: int
    activity_items: List[
        Union[
            AchievementActivityItem,
            ScreenshotActivityItem,
            ClipActivityItem,
            UserPostActivityItem,
        ]
    ]
    cont_token: str
    polling_interval_seconds: Optional[str]
    polling_token: str

    class Config:
        smart_union = True


class MessageResponse(CamelCaseModel):
    message: Message


class MessagesResponse(CamelCaseModel):
    messages: List[Message]


class ReportedItemsResponse(CamelCaseModel):
    reportedItems: List[ReportedItem]
