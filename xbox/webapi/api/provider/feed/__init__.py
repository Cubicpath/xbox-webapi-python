"""
Feed

Manage activity & chat feeds.
"""
from calendar import monthrange
from datetime import datetime
import json
import math
from typing import List, Optional
from urllib.parse import quote

from xbox.webapi.api.provider.baseprovider import BaseProvider
from xbox.webapi.api.provider.feed.models import (
    ActivityItemType,
    ActivityResponse,
    ContentType,
    Message,
    MessageResponse,
    MessagesResponse,
    PathSummary,
    PostResponse,
    PostType,
    ReportedItem,
    ReportedItemsResponse,
    SummariesResponse,
    TimelineType,
)


class FeedProvider(BaseProvider):
    ACTIVITY_URL = "https://avty.xboxlive.com"
    USERPOSTS_URL = "https://userposts.xboxlive.com"
    COMMENTS_URL = "https://comments.xboxlive.com"
    CHATFEED_URL = "https://chatfd.xboxlive.com"
    CLUBMODERATION_URL = "https://clubmoderation.xboxlive.com"

    HEADERS_ACTIVITY = {"x-xbl-contract-version": "12"}
    HEADERS_USERPOSTS = {"x-xbl-contract-version": "2"}
    HEADERS_COMMENTS = {"x-xbl-contract-version": "3"}
    HEADERS_CHATFEED = {"x-xbl-contract-version": "1"}
    HEADERS_CLUBMODERATION = {"x-xbl-contract-version": "1"}

    async def delete_feed_item(self, feed_item_id: str, **kwargs) -> None:
        headers = {"x-xbl-contract-version": "2"}

        url = f"https://{feed_item_id}"

        resp = await self.client.session.delete(url, headers=headers, **kwargs)
        resp.raise_for_status()

    # ACTIVITY
    # ---------------------------------------------------------------------------

    @staticmethod
    def _feed_start_date_time(months_ago: int, end_of_month: bool) -> datetime:
        years_ago = math.floor(months_ago / 12)
        months_ago = months_ago % 12

        now = datetime.utcnow()
        year = now.year if now.month > months_ago else now.year - (years_ago + 1)
        month = now.month - months_ago if now.month > months_ago else 12
        return now.replace(
            year=year, month=month, day=monthrange(year, month)[int(end_of_month)]
        )

    async def _send_activity_request(
        self, url: str, **activity_params
    ) -> ActivityResponse:
        params = {}

        num_items = activity_params.pop("num_items", None)
        if num_items is not None:
            params["numItems"] = str(num_items)

        include_self = activity_params.pop("include_self", None)
        if include_self is not None:
            params["includeSelf"] = str(num_items).lower()

        activity_types = activity_params.pop("activity_types", None)
        if activity_types:
            params["activityTypes"] = ";".join(activity_types)

        exclude_types = activity_params.pop("exclude_types", None)
        if exclude_types:
            params["excludeTypes"] = ";".join(exclude_types)

        start_date_time = activity_params.pop("start_date_time", None)
        if start_date_time:
            params["startDateTime"] = quote(
                start_date_time.strftime("%m/%d/%Y+%H:%M:%S"), safe=""
            )

        # All leftover "params" are assumed to be request kwargs
        request_kwargs = activity_params

        resp = await self.client.session.get(
            url, headers=self.HEADERS_ACTIVITY, params=params, **request_kwargs
        )
        resp.raise_for_status()

        return ActivityResponse.parse_raw(resp.text)

    async def get_user_activity_history(
        self,
        xuid: Optional[str],
        **activity_params,
    ) -> ActivityResponse:
        if activity_params.get("num_items") is None:
            activity_params["num_items"] = 20

        if (
            activity_params.get("activity_types") is None
            and activity_params.get("exclude_types") is None
        ):
            activity_params["activity_types"] = [
                ActivityItemType.GAME_DVR,
                ActivityItemType.ACHIEVEMENT_LEGACY,
                ActivityItemType.SCREENSHOT,
            ]

        url = f"{self.ACTIVITY_URL}/users/xuid({xuid or self.client.xuid})/Activity/History"
        if xuid is None:
            url += "/UnShared"

        return await self._send_activity_request(url, **activity_params)

    async def get_club_activity_feed(
        self,
        club_id: str,
        **activity_params,
    ) -> ActivityResponse:
        if activity_params.get("num_items") is None:
            activity_params["num_items"] = 50

        if (
            activity_params.get("activity_types") is None
            and activity_params.get("exclude_types") is None
        ):
            activity_params["exclude_types"] = [
                ActivityItemType.BROADCAST_START,
                ActivityItemType.BROADCAST_END,
            ]

        url = self.ACTIVITY_URL + f"/clubs/clubId({club_id})/activity/feed"

        return await self._send_activity_request(url, **activity_params)

    async def get_title_activity_feed(
        self,
        title_id: str,
        **activity_params,
    ) -> ActivityResponse:
        if (
            activity_params.get("activity_types") is None
            and activity_params.get("exclude_types") is None
        ):
            activity_params["exclude_types"] = [
                ActivityItemType.FOLLOWED,
                ActivityItemType.GAMERTAG_CHANGED,
                ActivityItemType.PLAYED,
            ]

        # Default start date is 2-3 months ago
        if activity_params.get("start_date_time") is None:
            activity_params["start_date_time"] = self._feed_start_date_time(
                months_ago=3, end_of_month=True
            )

        url = self.ACTIVITY_URL + f"/titles/titleId({title_id})/activity/feed"

        return await self._send_activity_request(url, **activity_params)

    async def get_xbox_activity_feed(
        self,
        **activity_params,
    ) -> ActivityResponse:
        if activity_params.get("num_items") is None:
            activity_params["num_items"] = 50

        if activity_params.get("include_self") is None:
            activity_params["include_self"] = True

        if (
            activity_params.get("activity_types") is None
            and activity_params.get("exclude_types") is None
        ):
            activity_params["exclude_types"] = [
                ActivityItemType.PLAYED,
                ActivityItemType.BROADCAST_START,
                ActivityItemType.BROADCAST_END,
            ]

        url = self.ACTIVITY_URL + f"/users/xuid({self.client.xuid})/XboxFeed"

        return await self._send_activity_request(url, **activity_params)

    async def get_user_pins(
        self, xuid: Optional[str] = None, **kwargs
    ) -> ActivityResponse:
        xuid = xuid or self.client.xuid

        url = self.ACTIVITY_URL + f"/timelines/User/{xuid}/pins"

        resp = await self.client.session.get(
            url, headers=self.HEADERS_ACTIVITY, **kwargs
        )
        resp.raise_for_status()

        return ActivityResponse.parse_raw(resp.text)

    # USER POSTS
    # ---------------------------------------------------------------------------

    async def post_text(self, text: str, **kwargs) -> PostResponse:
        data = {
            "postType": PostType.TEXT,
            "postText": text,
            "timelines": [
                {
                    "timelineType": TimelineType.USER,
                    "timelineOwner": self.client.xuid,
                }
            ],
        }

        url = self.USERPOSTS_URL + f"/users/me/posts"

        resp = await self.client.session.post(
            url, headers=self.HEADERS_USERPOSTS, json=data, **kwargs
        )
        resp.raise_for_status()

        return PostResponse.parse_raw(resp.text)

    async def share_item(
        self,
        feed_item_id: str,
        text: Optional[str] = None,
        parent_id: Optional[str] = None,
        **kwargs,
    ) -> PostResponse:
        post_type_data = {"locator": feed_item_id}
        if parent_id:
            post_type_data["parentId"] = parent_id

        data = {
            "postType": PostType.LINK_XBOX,
            "postText": text or "",
            "postTypeData": post_type_data,
            "timelines": [
                {
                    "timelineType": TimelineType.USER,
                    "timelineOwner": self.client.xuid,
                }
            ],
        }

        url = self.USERPOSTS_URL + f"/users/me/posts"

        resp = await self.client.session.post(
            url, headers=self.HEADERS_USERPOSTS, json=data, **kwargs
        )
        resp.raise_for_status()

        return PostResponse.parse_raw(resp.text)

    # COMMENTS
    # ---------------------------------------------------------------------------

    async def get_post_summaries(
        self, post_paths: List[str], **kwargs
    ) -> List[PathSummary]:
        data = {"rootPaths": post_paths}

        url = self.COMMENTS_URL + f"/summaries/batch"

        resp = await self.client.session.post(
            url, headers=self.COMMENTS_URL, json=data, **kwargs
        )
        resp.raise_for_status()

        return SummariesResponse.parse_raw(resp.text).summaries

    # CHAT FEED
    # ---------------------------------------------------------------------------

    async def get_club_message_history(
        self, club_id: str, message_id: str, max_items: int = 100, **kwargs
    ) -> List[Message]:
        params = {"messageId": message_id, "maxItems": str(max_items)}

        url = self.CHATFEED_URL + f"/channel/Club/{club_id}/messages/history"

        resp = await self.client.session.get(
            url, headers=self.HEADERS_CHATFEED, params=params, **kwargs
        )
        resp.raise_for_status()

        return MessagesResponse.parse_raw(resp.text).messages

    async def delete_club_message(
        self, club_id: str, message_id: str, **kwargs
    ) -> None:
        url = self.CHATFEED_URL + f"/channel/Club/{club_id}/messages/{message_id}"

        resp = await self.client.session.delete(
            url, headers=self.HEADERS_CHATFEED, **kwargs
        )
        resp.raise_for_status()

    async def get_club_motd(self, club_id: str, **kwargs) -> Message:
        url = self.CHATFEED_URL + f"/channel/Club/{club_id}/motd"

        resp = await self.client.session.get(
            url, headers=self.HEADERS_CHATFEED, **kwargs
        )
        resp.raise_for_status()

        return MessageResponse.parse_raw(resp.text).message

    async def set_club_motd(self, club_id: str, motd: str, **kwargs) -> None:
        data = {"newMotd": motd}

        url = self.CHATFEED_URL + f"/channel/Club/{club_id}/motd"

        resp = await self.client.session.put(
            url, headers=self.HEADERS_CHATFEED, json=data, **kwargs
        )
        resp.raise_for_status()

    # CLUB MODERATION
    # ---------------------------------------------------------------------------

    async def get_club_reported_items(
        self, club_id: str, **kwargs
    ) -> List[ReportedItem]:
        url = self.CLUBMODERATION_URL + f"/clubs/{club_id}/reportedItems"

        resp = await self.client.session.get(
            url, headers=self.HEADERS_CLUBMODERATION, **kwargs
        )
        resp.raise_for_status()

        return ReportedItemsResponse.parse_raw(resp.text).reportedItems

    async def send_club_report(
        self,
        club_id: str,
        content_id: str,
        content_type: ContentType,
        target_xuid: str,
        reason: str,
        **kwargs,
    ) -> str:
        data = {
            "contentId": content_id,
            "contentType": content_type,
            "targetXuid": target_xuid,
            "textReason": reason,
        }

        url = self.CLUBMODERATION_URL + f"/clubs/{club_id}/reportedItems"

        resp = await self.client.session.post(
            url, headers=self.HEADERS_CLUBMODERATION, json=data, **kwargs
        )
        resp.raise_for_status()

        return json.loads(resp.text)["reportId"]
