from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Union
from uuid import UUID

from xbox.webapi.api.provider.clubs.models import ClubRole
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
    ACHIEVEMENT_LEGACY = "LegacyAchievement"
    SCREENSHOT = "Screenshot"
    GAME_DVR = "GameDVR"
    BROADCAST_START = "BroadcastStart"
    BROADCAST_END = "BroadcastEnd"
    GAMERTAG_CHANGED = "GamertagChanged"
    CONTAINER = "Container"


class AuthorType(str, Enum):
    UNKNOWN = "Unknown"
    USER = "User"
    TITLE = "TitleUser"


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
    TEXT = "Text"
    LINK = "Link"
    LINK_XBOX = "XboxLink"


class LinkType(str, Enum):
    UNKNOWN = "Unknown"
    DEFAULT = "Default"


class PathType(str, Enum):
    UNKNOWN = "Unknown"
    ACHIEVEMENT = "Achievement"
    ACTIVITY_FEED_ITEM = "ActivityFeedItem"
    USER_POST_TIMELINE = "UserPostTimeline"


class TimelineType(str, Enum):
    UNKNOWN = "Unknown"
    USER = "User"
    CLUB = "Club"


class RarityCategory(str, Enum):
    UNKNOWN = "Unknown"
    COMMON = "Common"
    RARE = "Rare"


class ItemSource(str, Enum):
    UNKNOWN = "Unknown"
    TRENDING = "Trending"


class Platform(str, Enum):
    UNKNOWN = "Unknown"
    XBOX_360 = "Xenon"  # Not observed
    XBOX_ONE_OG = "Durango"
    XBOX_ONE = "XboxOne"
    XBOX_ONE_S = "Edmonton"
    XBOX_ONE_X = "Scorpio"
    XBOX_SERIES_S = "Lockhart"  # Not observed
    XBOX_SERIES_X = "Scarlett"
    WINDOWS = "Win32"
    WINDOWS_ONE_CORE = "WindowsOneCore"


class Title(CamelCaseModel):
    title_id: int
    title_name: str


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


class BaseAuthorInfo(CamelCaseModel):
    name: str
    second_name: str
    image_url: str
    color: PreferredColor
    show_as_avatar: str
    author_type: AuthorType
    id: str


class UserAuthorInfo(BaseAuthorInfo):
    modern_gamertag: str
    modern_gamertag_suffix: str


class TitleAuthorInfo(BaseAuthorInfo):
    title_id: str
    title_name: str
    title_image: str
    unfollowable_titles: List[Title]


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


class PostTimeline(CamelCaseModel):
    timeline_type: TimelineType
    timeline_owner: str
    date: Optional[datetime]
    timeline_uri: str


class Timeline(CamelCaseModel):
    timeline_id: str
    timeline_type: TimelineType
    timeline_name: str
    timeline_image: str


class ClubTimeline(Timeline):
    is_official_club: bool  # Only for official clubs
    unfollowable_titles: Optional[List[Title]]  # Only for official clubs
    author_roles: List[ClubRole]
    is_public: bool


class UserTimeline(Timeline):
    timeline_owner: str
    date: datetime
    timeline_uri: str


class PathSummary(CamelCaseModel):
    type: PathType
    path: str
    like_count: int
    comment_count: int
    share_count: int


class Comment(CamelCaseModel):
    text: str
    root_type: PathType
    root_path: str
    path: str
    xuid: str
    gamertag: str
    date: datetime
    id: str
    parent_path: str


class GameMediaContentLocator(CamelCaseModel):
    expiration: Optional[datetime]
    file_size: Optional[int]
    locator_type: Optional[LocatorType]
    uri: Optional[str]


class BaseActivityItem(CamelCaseModel):
    description: str
    has_ugc: bool
    activity_item_type: ActivityItemType
    short_description: str
    item_text: str
    has_liked: bool


class ActivityItem(BaseActivityItem):
    bing_id: Optional[UUID]
    content_image_uri: Optional[str]
    content_title: Optional[str]
    game_media_content_locators: Optional[List[GameMediaContentLocator]]
    platform: Optional[Platform]  # System item was posted from
    title_id: Optional[str]
    upload_title_id: Optional[str]
    date: datetime
    content_type: ContentType
    ugc_caption: Optional[str]
    item_image: Optional[str]
    trusted_item_image: Optional[bool]
    share_root: str
    feed_item_id: str
    item_root: str
    view_count: Optional[int]
    num_likes: Optional[int]
    num_comments: Optional[int]
    num_shares: Optional[int]
    num_views: Optional[int]
    author_info: Union[UserAuthorInfo, TitleAuthorInfo]
    user_xuid: str
    pinned: Optional[bool]

    class Config:
        smart_union = True


class AchievementActivityItem(ActivityItem):
    achievement_scid: UUID
    achievement_id: str
    achievement_type: AchievementType
    achievement_icon: str
    achievement_name: str
    rarity_category: str
    rarity_percentage: int
    gamerscore: int
    achievement_description: str
    is_secret: bool
    has_app_award: bool
    has_art_award: bool


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


class ContainerActivityItem(BaseActivityItem):
    item_source: ItemSource
    feed_items: List[
        Union[
            AchievementActivityItem,
            ScreenshotActivityItem,
            ClipActivityItem,
            UserPostActivityItem,
            ActivityItem,
        ]
    ]


class ActivityResponse(CamelCaseModel):
    num_items: int
    activity_items: List[
        Union[
            AchievementActivityItem,
            ScreenshotActivityItem,
            ClipActivityItem,
            UserPostActivityItem,
            ContainerActivityItem,
            ActivityItem,
        ]
    ]
    cont_token: Optional[str]
    max_pins: Optional[int]
    polling_interval_seconds: Optional[str]
    polling_token: Optional[str]

    class Config:
        smart_union = True


class MessageResponse(CamelCaseModel):
    message: Message


class MessagesResponse(CamelCaseModel):
    messages: List[Message]


class ReportedItemsResponse(CamelCaseModel):
    reportedItems: List[ReportedItem]


class PostResponse(CamelCaseModel):
    post_uri: str
    post_type: PostType
    post_author: str
    post_id: UUID
    post_text: str
    timelines: List[PostTimeline]
    post_date: datetime
    post_content_locators: Optional[List[GameMediaContentLocator]]


class SummariesResponse(CamelCaseModel):
    summaries: List[PathSummary]


class PathCommentsResponse(CamelCaseModel):
    comments: List[Comment]
    continuation_token: Optional[str]
    type: PathType
    path: str
    like_count: int
    comment_count: int
    share_count: int
