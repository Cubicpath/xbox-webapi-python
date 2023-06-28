from datetime import datetime
from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID

from xbox.webapi.common.models import CamelCaseModel


class ClubType(str, Enum):
    # From xbox::services::clubs::clubs_service_impl::convert_club_type_to_string
    # In Microsoft.Xbox.Services.dll
    UNKNOWN = "unknown"  # Unknown club type
    PUBLIC = "open"  # Open club
    PRIVATE = "closed"  # Closed club
    HIDDEN = "secret"  # Secret club


class ClubRole(str, Enum):
    # From xbox::services::clubs::clubs_service_impl::convert_club_role_to_string
    # In Microsoft.Xbox.Services.dll
    NONMEMBER = "Nonmember"  # Not a member of the club. Used exclusively for permissions/settings
    MEMBER = "Member"  # Member of a club
    MODERATOR = "Moderator"  # Moderator of a club
    OWNER = "Owner"  # Owner of a club
    REQUESTED_TO_JOIN = "RequestedToJoin"  # User has requested to join a club
    RECOMMENDED = "Recommended"  # User has been recommended for a club
    INVITED = "Invited"  # User has been invited to a club
    BANNED = "Banned"  # User has been banned from all interaction with a club.
    # A user cannot have any other role with a club if they are banned from it
    FOLLOWER = "Follower"  # Follower of a club


class ClubPresence(str, Enum):
    # From xbox::services::clubs::clubs_service_impl::convert_user_presence_to_string
    # In Microsoft.Xbox.Services.dll
    NOT_IN_CLUB = "NotInClub"  # User is no longer on a club page.
    IN_CLUB = "InClub"  # User is viewing the club, but not on any specific page.
    CHAT = "Chat"  # User is on the chat page.
    FEED = "Feed"  # User is viewing the club feed.
    ROSTER = "Roster"  # User is viewing the club roster/presence.
    PLAY = (
        "Play"  # User is on the play tab in the club (not actually playing anything).
    )
    IN_GAME = "InGame"  # User is playing the associated game.

    # Extra value in modern club implementation
    IN_PARTY = "InParty"  # UNDOCUMENTED -- UNCONFIRMED ENUM VALUE


class ClubJoinability(str, Enum):
    UNKNOWN = "Unknown"
    REQUEST_TO_JOIN = "OpenJoin"
    INVITE_ONLY = "InviteOnly"


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
    creation_date_utc: datetime
    background_image_url: Optional[str]
    display_image_url: Optional[str]
    preferred_color: Optional[PreferredColor]
    activity_feed_enabled: Optional[bool]
    chat_enabled: Optional[bool]
    lfg_enabled: Optional[bool]
    preferred_locale: Optional[str]
    request_to_join_enabled: Optional[bool]
    leave_enabled: Optional[bool]
    transfer_ownership_enabled: Optional[bool]
    is_promoted_club: Optional[bool]
    tags: Optional[List[str]]
    titles: Optional[List[str]]
    who_can_post_to_feed: Optional[ClubRole]
    who_can_invite: Optional[ClubRole]
    who_can_chat: Optional[ClubRole]
    who_can_create_lfg: Optional[ClubRole]
    who_can_join_lfg: Optional[ClubRole]
    mature_content_enabled: Optional[bool]
    watch_club_titles_only: Optional[bool]
    get_recommendation_enabled: Optional[bool]
    search_enabled: Optional[bool]
    delete_enabled: Optional[bool]
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
    genre: str
    localized_title_family_name: Optional[str]
    title_family_id: UUID


class ClubRoleRecord(CamelCaseModel):
    actor_xuid: str  # Actor Xuid that was responsible for user belonging to the role.
    xuid: Optional[str]  # Xuid that belongs to the role. Empty if same as actor_xuid.
    role: Optional[ClubRole]
    created_date: datetime  # When the user was added to the role.
    localized_role: Optional[ClubRole]  # Role of the user.


class ClubRoster(CamelCaseModel):
    moderator: List[ClubRoleRecord]  # Club moderators
    requested_to_join: Optional[
        List[ClubRoleRecord]
    ]  # Users who've requested to join the club
    recommended: Optional[
        List[ClubRoleRecord]
    ]  # Users who've been recommended for the club
    banned: Optional[List[ClubRoleRecord]]  # Users who've been banned from the club


class TargetRoleRecords(CamelCaseModel):
    roles: Optional[List[ClubRoleRecord]]
    localized_role: Optional[ClubRoleRecord]


class ClubRecommendationReason(CamelCaseModel):
    localized_text: str  # Localized string giving the reason the club is recommended


class ClubRecommendation(CamelCaseModel):
    reasons: List[ClubRecommendationReason]
    criteria: str
    title_ids: List[str]


class ClubReservation(CamelCaseModel):
    name: str
    owner: str
    expires: datetime


class ClubSummary(CamelCaseModel):
    name: str
    owner: str
    id: str
    type: ClubType
    created: datetime
    free_name_change: Optional[bool]
    can_delete_immediately: bool
    suspension_required_after: Optional[datetime]
    genre: str


class ClubUserPresenceRecord(CamelCaseModel):
    xuid: str  # Xuid of the user who was present at the club.
    last_seen_timestamp: datetime  # Time when the user was last present within the club.
    last_seen_state: ClubPresence  # User's state when they were last seen.


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
    description: Setting[Optional[str]]  # Description of the club
    rules: Setting[Any]
    name: Setting[str]  # Name of the club
    short_name: Setting[str]  # Club short name
    is_searchable: Setting[bool]  # Should the club show up in search results
    is_recommendable: Setting[bool]  # Should the club show up in recommendations
    leave_enabled: Setting[bool]  # Can users leave the club
    transfer_ownership_enabled: Setting[
        bool
    ]  # Can ownership of the club be transferred
    mature_content_enabled: Setting[bool]  # Is mature content enabled within the club
    watch_club_titles_only: Setting[bool]
    display_image_url: Setting[str]  # URL for display image
    background_image_url: Setting[str]  # URL for background image
    preferred_locale: Setting[str]  # The club's preferred locale
    tags: Setting[
        List[str]
    ]  # Tags associated with the club (ex. "Hate-Free", "Women only")
    associated_titles: Setting[List[str]]  # List of titles associated with the club
    primary_color: Setting[str]  # Primary color of the club
    secondary_color: Setting[str]  # Secondary color of the club
    tertiary_color: Setting[str]  # Tertiary color of the club


class Club(CamelCaseModel):
    id: str  # ClubId
    club_type: ClubTypeContainer  # Type (visibility) of club
    creation_date_utc: datetime  # When the club was created.
    glyph_image_url: Optional[str]  # Club's display image url
    banner_image_url: Optional[str]  # Club's background image url
    settings: Optional[
        ClubRootSettings
    ]  # Settings dictating what actions users can take
    # within the club depending on their role.
    followers_count: int  # Number of followers of the club.
    members_count: int  # Number of club members.
    moderators_count: int  # Number of club moderators.
    recommended_count: int  # Configurable club attributes
    requested_to_join_count: int  # Number of users requesting to join the club.
    club_presence_count: int  # Count of members present in the club.
    club_presence_today_count: int  # Count of members present in the club.
    club_presence_in_game_count: int
    roster: Optional[ClubRoster]
    target_roles: Optional[TargetRoleRecords]
    recommendation: Optional[ClubRecommendation]
    club_presence: Optional[List[ClubUserPresenceRecord]]
    state: str
    suspended_until_utc: Optional[
        datetime
    ]  # When the club remains suspended until. Null if not suspended
    report_count: int  # Number of reports for the club.
    reported_items_count: int  # Number of reported items for the club.
    max_members_per_club: int
    max_members_in_game: int
    owner_xuid: Optional[str]
    founder_xuid: str  # Club founder's Xuid.
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
    clubs: List[Club]  # List of clubs that match the search query
    search_facet_results: Optional[
        ClubSearchFacetResults
    ]  # Facets can be used to further narrow down search results.
    # The return map maps a facet (ie. tag or title) to a collection of search facet result objects.
    # A search facet result object describes how often a particular value of that facet occurred.
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
