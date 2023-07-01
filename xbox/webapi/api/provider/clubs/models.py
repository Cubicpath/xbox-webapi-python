from datetime import datetime
from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID

from xbox.webapi.common.models import CamelCaseModel


class ClubType(str, Enum):
    # From xbox::services::clubs::clubs_service_impl::convert_club_type_to_string
    # In Microsoft.Xbox.Services.dll
    UNKNOWN = "unknown"
    PUBLIC = "open"  # Anyone can Find, Ask to Join, and Play.
    PRIVATE = "closed"  # Anyone can Find and Ask to Join.
    HIDDEN = "secret"  # Only invited people can Ask to Join.


class ClubRole(str, Enum):
    # From xbox::services::clubs::clubs_service_impl::convert_club_role_to_string
    # In Microsoft.Xbox.Services.dll
    NONMEMBER = "Nonmember"  # Used exclusively for permissions/settings
    MEMBER = "Member"
    MODERATOR = "Moderator"
    OWNER = "Owner"
    REQUESTED_TO_JOIN = "RequestedToJoin"
    RECOMMENDED = "Recommended"
    INVITED = "Invited"
    BANNED = "Banned"  # A user cannot have any other role with a club if they are banned from it
    FOLLOWER = "Follower"


class ClubPresence(str, Enum):
    # From xbox::services::clubs::clubs_service_impl::convert_user_presence_to_string
    # In Microsoft.Xbox.Services.dll
    NOT_IN_CLUB = "NotInClub"  # User is no longer on a club page.
    IN_CLUB = "InClub"  # User is viewing the club, but not on any specific page.
    CHAT = "Chat"
    FEED = "Feed"
    ROSTER = "Roster"
    PLAY = "Play"  # User is on the play tab in the club (not actually playing).
    IN_GAME = "InGame"  # User is playing the associated game.

    # Extra value in modern club implementation
    IN_PARTY = "InParty"


class ClubGenre(str, Enum):
    UNKNOWN = "unknown"
    SOCIAL = "social"  # User club
    TITLE = "title"  # Official game club


class ClubJoinability(str, Enum):
    UNKNOWN = "Unknown"
    OPEN = "OpenJoin"
    REQUEST_TO_JOIN = "RequestToJoin"
    INVITE_ONLY = "InviteOnly"


class ClubState(str, Enum):
    NONE = "None"
    SUSPENDED = "Suspended"


class PreferredColor(CamelCaseModel):
    primary_color: Optional[str]
    secondary_color: Optional[str]
    tertiary_color: Optional[str]


class DeepLink(CamelCaseModel):
    page_name: str
    uri: str


class DeepLinks(CamelCaseModel):
    xbox: Optional[List[DeepLink]]
    pc: Optional[List[DeepLink]]
    iOS: Optional[List[DeepLink]]
    android: Optional[List[DeepLink]]


class ClubSettingsContract(CamelCaseModel):
    description: Optional[str]
    creation_date_utc: datetime = datetime.strptime(
        "0001-01-01T00:00:00.000Z", "%Y-%m-%dT%H:%M:%S.%fZ"
    )
    background_image_url: Optional[str]
    display_image_url: Optional[str]
    preferred_color: Optional[PreferredColor]
    activity_feed_enabled: Optional[bool]  # Permanent change
    chat_enabled: Optional[bool]  # Permanent change
    lfg_enabled: Optional[bool]  # Cannot be modified
    preferred_locale: Optional[str]
    request_to_join_enabled: Optional[bool]
    leave_enabled: Optional[bool]
    transfer_ownership_enabled: Optional[bool]
    is_promoted_club: Optional[bool]  # Cannot be modified
    tags: Optional[List[str]]
    titles: Optional[List[str]]
    who_can_post_to_feed: Optional[ClubRole]
    who_can_invite: Optional[ClubRole]
    who_can_chat: Optional[ClubRole]
    who_can_create_lfg: Optional[ClubRole]
    who_can_join_lfg: Optional[ClubRole]
    mature_content_enabled: Optional[bool]  # Streams marked as mature
    watch_club_titles_only: Optional[bool]  # Streams of club games only
    get_recommendation_enabled: Optional[bool]  # Permanent change
    search_enabled: Optional[bool]  # Permanent change
    delete_enabled: Optional[bool]  # Cannot be modified
    rename_enabled: Optional[bool]
    joinability: Optional[ClubJoinability]


class ClubSearchFacetResult(CamelCaseModel):
    count: int
    value: str


class ClubSearchFacetResults(CamelCaseModel):
    titles: Optional[List[ClubSearchFacetResult]]
    tags: Optional[List[ClubSearchFacetResult]]


class ClubsSuggestResult(CamelCaseModel):
    title_family_id: UUID
    score: int
    languages: List[str]
    language_regions: List[str]
    preferred_color: Optional[PreferredColor]
    tags: List[str]
    titles: List[str]
    title_tags: List[str]
    short_name: Optional[str]
    name: str
    id: str
    display_image_url: str
    description: str


class ClubsSuggestResultWithText(CamelCaseModel):
    result: ClubsSuggestResult
    text: str


class ClubTypeContainer(CamelCaseModel):
    type: ClubType
    genre: ClubGenre
    localized_title_family_name: Optional[str]
    title_family_id: UUID


class ClubRoleRecord(CamelCaseModel):
    actor_xuid: str  # Actor Xuid that was responsible for user belonging to the role.
    xuid: Optional[str]  # Null if same as actor_xuid.
    role: Optional[ClubRole]
    created_date: datetime  # When the user was added to the role.
    localized_role: Optional[ClubRole]


class ClubRoster(CamelCaseModel):
    moderator: Optional[List[ClubRoleRecord]]  # Includes Owner, null if suspended.
    requested_to_join: Optional[List[ClubRoleRecord]]
    recommended: Optional[List[ClubRoleRecord]]
    banned: Optional[List[ClubRoleRecord]]


class TargetRoleRecords(CamelCaseModel):
    roles: Optional[List[ClubRoleRecord]]
    localized_role: Optional[ClubRoleRecord]


class ClubRecommendationReason(CamelCaseModel):
    localized_text: str


class ClubRecommendation(CamelCaseModel):
    reasons: List[ClubRecommendationReason]
    criteria: str
    title_ids: List[str]


class ClubReservation(CamelCaseModel):
    name: str
    owner: str
    expires: datetime


class ClubSuspension(CamelCaseModel):
    actor: str = 'owner'
    delete_after: datetime


class ClubSummary(CamelCaseModel):
    name: str
    owner: str
    id: str
    type: ClubType
    created: datetime
    suspensions: Optional[List[ClubSuspension]]
    free_name_change: Optional[bool]
    can_delete_immediately: bool
    suspension_required_after: Optional[datetime]
    reservation_duration_after_suspension_in_hours: Optional[int]
    genre: ClubGenre


class ClubUserPresenceRecord(CamelCaseModel):
    xuid: str
    last_seen_timestamp: datetime
    last_seen_state: ClubPresence


_VT = TypeVar("_VT")  # Setting Value Generic


class Setting(CamelCaseModel, Generic[_VT]):
    value: _VT
    allowed_values: Optional[List[_VT]]
    can_viewer_change_setting: bool


class ClubActionSetting(Setting[str]):
    can_viewer_act: bool
    allowed_values: List[str]


class ClubFeedSettings(CamelCaseModel):
    post: ClubActionSetting
    pin_post: ClubActionSetting
    post_media_from_device: ClubActionSetting
    post_media_from_xbl_library: ClubActionSetting
    post_store_link: ClubActionSetting
    post_web_link: ClubActionSetting
    schedule_post: ClubActionSetting
    view: ClubActionSetting


class ClubChatSettings(CamelCaseModel):
    write: ClubActionSetting
    set_chat_topic: ClubActionSetting
    view: ClubActionSetting


class ClubLfgSettings(CamelCaseModel):
    join: ClubActionSetting
    create: ClubActionSetting
    view: ClubActionSetting


class ClubRosterSettings(CamelCaseModel):
    invite_or_accept: ClubActionSetting
    kick_or_ban: ClubActionSetting
    view: ClubActionSetting
    joinability: ClubActionSetting


class ClubProfileSettings(CamelCaseModel):
    update: ClubActionSetting
    delete: ClubActionSetting
    view: ClubActionSetting
    view_analytics: ClubActionSetting


class ClubViewerRoleSettings(CamelCaseModel):
    roles: List[ClubRole]
    localized_role: Optional[Any]


class ClubRootSettings(CamelCaseModel):
    feed: ClubFeedSettings
    chat: ClubChatSettings
    lfg: ClubLfgSettings
    roster: ClubRosterSettings
    profile: ClubProfileSettings
    viewer_roles: ClubViewerRoleSettings


class ClubProfile(CamelCaseModel):
    description: Setting[Optional[str]]
    rules: Setting[Any]  # Unknown.
    name: Setting[str]
    short_name: Setting[str]
    is_searchable: Setting[bool]  # Should the club show up in search results.
    is_recommendable: Setting[bool]  # Should the club show up in recommendations.
    leave_enabled: Setting[bool]
    transfer_ownership_enabled: Setting[bool]
    mature_content_enabled: Setting[bool]
    watch_club_titles_only: Setting[bool]  # Unknown.
    display_image_url: Setting[str]  # Icon image URL.
    background_image_url: Setting[str]
    preferred_locale: Setting[str]  # The club language.
    tags: Setting[List[str]]  # See xbox/webapi/api/provider/clubs/const.py for tags.
    associated_titles: Setting[List[str]]  # List of titles associated with the club.
    primary_color: Setting[str]
    secondary_color: Setting[str]
    tertiary_color: Setting[str]


class Club(CamelCaseModel):
    id: str
    club_type: ClubTypeContainer  # Type of club, including genre.
    creation_date_utc: datetime
    glyph_image_url: Optional[str]  # Icon image URL.
    banner_image_url: Optional[str]  # Background image url.
    settings: Optional[ClubRootSettings]  # Dictates what actions roles can take.
    followers_count: int
    members_count: int
    moderators_count: int  # Includes owner.
    recommended_count: int
    requested_to_join_count: int
    club_presence_count: int  # Amount of members currently in club.
    club_presence_today_count: int  # Amount of members who were in club today.
    club_presence_in_game_count: int
    roster: Optional[ClubRoster]
    target_roles: Optional[TargetRoleRecords]
    recommendation: Optional[ClubRecommendation]
    club_presence: Optional[List[ClubUserPresenceRecord]]
    state: ClubState
    suspended_until_utc: Optional[datetime]  # Null if not suspended.
    report_count: int  # Number of reports for the club.
    reported_items_count: int
    max_members_per_club: int
    max_members_in_game: int
    owner_xuid: Optional[str]  # Null if suspended.
    founder_xuid: str
    title_deep_links: Optional[DeepLinks]
    profile: ClubProfile  # Configurable club attributes
    is_official_club: bool
    club_deep_links: Optional[DeepLinks]


class OwnedClubsResponse(CamelCaseModel):
    owner: str
    clubs: Optional[List[ClubSummary]]
    remaining_open_and_closed_clubs: str
    remaining_secret_clubs: str
    maximum_open_and_closed_clubs: str
    maximum_secret_clubs: str


class SearchClubsResponse(CamelCaseModel):
    clubs: List[Club]

    # Facets can be used to further narrow down search results.
    # The return map maps a facet (ie. tag or title) to a collection of search facet result objects.
    # A search facet result object describes how often a particular value of that facet occurred.
    search_facet_results: Optional[ClubSearchFacetResults]
    recommendation_counts: Optional[Any]
    club_deep_links: Optional[DeepLinks]


class SuggestedClubsResponse(CamelCaseModel):
    results: List[ClubsSuggestResultWithText]


class UpdateRolesResponse(CamelCaseModel):
    user_id: str
    roles: List[ClubRole]
    channel_follow_quota_max: Optional[int]
    channel_follow_quota_remaining: Optional[int]
    follow_quota_max: Optional[int]
    follow_quota_remaining: Optional[int]
    member_quota_max: Optional[int]
    member_quota_remaining: Optional[int]


class GetPresenceResponse(CamelCaseModel):
    club_id: str
    total_count: int
    active_count: int
    here_today_count: int
    in_game_count: int
