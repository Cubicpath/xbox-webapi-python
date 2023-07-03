"""
Clubs

Manage clubs and club information.
"""
from collections.abc import Sequence
from datetime import datetime
import json
from typing import Dict, List, Optional, Union
from uuid import UUID

from xbox.webapi.api.provider.baseprovider import BaseProvider
from xbox.webapi.api.provider.clubs.models import (
    Club,
    ClubGenre,
    ClubPresence,
    ClubReservation,
    ClubRole,
    ClubRootSettings,
    ClubRoster,
    ClubSettingsContract,
    ClubSummary,
    ClubSuspension,
    ClubType,
    ClubUserPresenceRecord,
    GetPresenceResponse,
    OwnedClubsResponse,
    SearchClubsResponse,
    SuggestedClubsResponse,
    UpdateRolesResponse,
)
from xbox.webapi.common.models import to_pascal

_NULL_UUID = UUID(int=0)


class ClubProvider(BaseProvider):
    CLUBACCOUNTS_URL = "https://clubaccounts.xboxlive.com"
    CLUBHUB_URL = "https://clubhub.xboxlive.com"
    CLUBPRESENCE_URL = "https://clubpresence.xboxlive.com"
    CLUBPROFILE_URL = "https://clubprofile.xboxlive.com"
    CLUBROSTER_URL = "https://clubroster.xboxlive.com"
    # CLUBSEARCH_URL = 'https://clubsearch.xboxlive.com'

    _HEADERS_COMMON = {
        "Accept": "application/json",
        "Accept-Language": "en-US, en, en-AU, en, en-GB, en, en-CA, en, en-AS, en, en-AT, en, en-BB, en",
    }
    HEADERS_CLUBACCOUNTS = _HEADERS_COMMON | {"x-xbl-contract-version": "1"}
    HEADERS_CLUBHUB = _HEADERS_COMMON | {"x-xbl-contract-version": "5"}
    HEADERS_CLUBPRESENCE = _HEADERS_COMMON | {"x-xbl-contract-version": "1"}
    HEADERS_CLUBPROFILE = _HEADERS_COMMON | {"x-xbl-contract-version": "2"}
    HEADERS_CLUBROSTER = _HEADERS_COMMON | {"x-xbl-contract-version": "4"}
    # HEADERS_CLUBSEARCH = {'x-xbl-contract-version': '2'}

    SEPARATOR = ","

    # CLUB ACCOUNTS
    # ---------------------------------------------------------------------------

    async def get_club_summary(self, club_id: str, **kwargs) -> ClubSummary:
        """
        Get a summary of a given club's information and suspensions.

        You must own the club to use this method.

        XLE error codes:
            200 - Successfully obtained club summary.
            1001 - A requested object was not found by the service.
            1016 - Query parameter was malformed or invalid.

        Args:
            club_id: Club ID

        Returns:
            :class:`ClubSummary`: Club Summary
        """
        url = self.CLUBACCOUNTS_URL + f"/clubs/clubid({club_id})"

        resp = await self.client.session.get(
            url, headers=self.HEADERS_CLUBACCOUNTS, **kwargs
        )
        resp.raise_for_status()

        return ClubSummary.parse_raw(resp.text)

    async def get_clubs_owned(self, **kwargs) -> OwnedClubsResponse:
        """
        Get list of clubs owned by the caller, along with how many clubs you can own.

        XLE error codes:
            200 - Successfully obtained owned clubs.

        Returns:
            :class:`OwnedClubsResponse`: Owned Clubs Response
        """
        headers = self.HEADERS_CLUBACCOUNTS | {"x-xbl-contract-version": "2"}

        url = self.CLUBACCOUNTS_URL + f"/users/xuid({self.client.xuid})/clubsowned"

        resp = await self.client.session.get(url, headers=headers, **kwargs)
        resp.raise_for_status()

        return OwnedClubsResponse.parse_raw(resp.text)

    async def claim_club_name(self, name: str, **kwargs) -> ClubReservation:
        """
        Reserve a club name for use in create_club().

        XLE error codes:
            200 - Successfully claimed club.
            1005 - The requested club name was too long.
            1007 - The requested club name contains invalid characters.
                    Club names must only use letter, numbers, and spaces.
            1010 - The requested club name is not available.
            1023 - The requested club name was rejected.

        Args:
            name: Club name to claim

        Returns:
            :class:`ClubReservation`: Club Reservation
        """
        data = {"name": name}

        url = self.CLUBACCOUNTS_URL + f"/clubs/reserve"

        resp = await self.client.session.post(
            url, headers=self.HEADERS_CLUBACCOUNTS, json=data, **kwargs
        )
        resp.raise_for_status()

        return ClubReservation.parse_raw(resp.text)

    async def create_club(
        self,
        name: str,
        club_type: ClubType,
        genre: ClubGenre = ClubGenre.SOCIAL,
        title_family_id: UUID = _NULL_UUID,
        **kwargs,
    ) -> ClubSummary:
        """
        Create a club with the given name and visibility.

        If creating a non-hidden club, you must first call claim_club_name() with the name you want to use.

        XLE error codes:
            201 - Successfully created club.
            1000 - A parallel write operation took precedence over your request.
            1005 - The requested club name was too long.
            1007 - The requested club name contains invalid characters.
                    Club names must only use letter, numbers, and spaces.
            1014 - The club name has not been reserved by the calling user.
                    This happens when club_type is not HIDDEN and you have not
                    called claim_club_name().
            1023 - The requested club name was rejected.
            1038 - A TitleFamilyId value must be specified when requesting a TitleClub
                    (genre is ClubGenre.TITLE but title_family_id is not provided).
            1040 - An invalid TitleFamilyId value was specified.
            1041 - The calling title is not authorized to perform the requested action with the requested TitleFamilyId.
            1042 - The club genre is not valid.

        Args:
            name: Club name
            club_type: Club visibility
            genre: Club genre, e.g. social or title
            title_family_id: ID used to create titleclub with

        Returns:
            :class:`ClubSummary`: Club Summary
        """
        data = {"name": name, "type": club_type, "genre": genre}
        if title_family_id.int:
            data["titleFamilyId"] = str(title_family_id)

        url = self.CLUBACCOUNTS_URL + f"/clubs/create"

        resp = await self.client.session.post(
            url, headers=self.HEADERS_CLUBACCOUNTS, json=data, **kwargs
        )
        resp.raise_for_status()

        return ClubSummary.parse_raw(resp.text)

    async def transfer_club_ownership(
        self, club_id: str, xuid: str, **kwargs
    ) -> ClubSummary:
        """
        Transfer club ownership to the given xuid.

        XLE error codes:
            200 - Successfully transferred ownership.
            1015 - The requested club is not available.
            1033 - The target user for the ownership transfer must already be a moderator of the club.

        Args:
            club_id: Club ID
            xuid: User to transfer ownership to

        Returns:
            :class:`ClubSummary`: Club Summary
        """
        data = {"method": "TransferOwnership", "user": xuid}

        url = self.CLUBACCOUNTS_URL + f"/clubs/clubid({club_id})"

        resp = await self.client.session.post(
            url, headers=self.HEADERS_CLUBACCOUNTS, json=data, **kwargs
        )
        resp.raise_for_status()

        return ClubSummary.parse_raw(resp.text)

    async def rename_club(self, club_id: str, name: str, **kwargs) -> ClubSummary:
        """
        Rename a club with the given name.

        A club can only be renamed once.

        XLE error codes:
            201 - Successfully created club.
            1007 - The requested club name contains invalid characters.
                    Club names must only use letter, numbers, and spaces.
            1014 - The club name has not been reserved by the calling user.
                    This happens when club_type is not HIDDEN and you have not
                    called claim_club_name().
            1015 - The requested club is not available.
            1023 - The requested club name was rejected.
            1035 - The name cannot be changed for the requested club. All available name changes have been used.

        Args:
            club_id: Club ID
            name: Club name to use

        Returns:
            :class:`ClubSummary`: Club Summary
        """
        data = {"method": "ChangeName", "name": name}

        url = self.CLUBACCOUNTS_URL + f"/clubs/clubid({club_id})"

        resp = await self.client.session.post(
            url, headers=self.HEADERS_CLUBACCOUNTS, json=data, **kwargs
        )
        resp.raise_for_status()

        return ClubSummary.parse_raw(resp.text)

    async def delete_club(self, club_id: str, **kwargs) -> Union[ClubSummary, ClubReservation, None]:
        """
        Delete the club with the given id.

        If a club is not hidden and is older than one week you will receive a reservation for the club name,
        and it will be suspended for 7 days before being automatically deleted.

        The reservation should last for 1 day after the club is deleted, but you can double check in the ClubSummary
        reservation_duration_after_suspension_in_hours field.

        XLE error codes:
            200 - Successfully deleted club with name reservation.
            202 - Successfully started suspension process.
            204 - Successfully deleted club.
            1015 - The requested club is not available.
            1053 - Another pending operation in progress.

        Args:
            club_id: Club ID

        Returns:
            :class:`Union[ClubSummary, ClubReservation, None]`: Club Summary if a suspension process is started,
            else Club Reservation if club is a non-hidden club that is successfully deleted, else None.
        """
        url = self.CLUBACCOUNTS_URL + f"/clubs/clubid({club_id})"

        resp = await self.client.session.delete(
            url, headers=self.HEADERS_CLUBACCOUNTS, **kwargs
        )
        resp.raise_for_status()

        if resp.status_code == 200:
            return ClubReservation.parse_raw(resp.text)
        elif resp.status_code == 202:
            return ClubSummary.parse_raw(resp.text)
        else:
            return None

    async def suspend_club(
        self, club_id: str, delete_date: datetime, **kwargs
    ) -> ClubSuspension:
        """
        Delete the club with the given id after the given date.

        The club is suspended in the meantime and can be restored through unsuspend_club().

        XLE error codes:
            200 - Successfully started suspension process.
            1015 - The requested club is not available.
            1018 - The caller is not permitted to perform the requested action.
            1021 - The actor specified for the suspension record is not valid.

        Args:
            club_id: Club ID
            delete_date: Date to end suspension and delete the club. Minimum is 168 hours (7 days) from the current time

        Returns:
            :class:`ClubSuspension`: Club Suspension
        """
        suspension = ClubSuspension.parse_obj(
            {"deleteAfter": delete_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}
        )

        url = self.CLUBACCOUNTS_URL + f"/clubs/clubid({club_id})/suspension/owner"

        resp = await self.client.session.put(
            url,
            headers=self.HEADERS_CLUBACCOUNTS,
            json=json.loads(suspension.json()),
            **kwargs,
        )
        resp.raise_for_status()

        return ClubSuspension.parse_raw(resp.text)

    async def unsuspend_club(self, club_id: str, **kwargs) -> None:
        """
        Stop the club suspension & deletion process.

        XLE error codes:
            204 - Successfully unsuspended club.
            1015 - The requested club is not available.
            1018 - The caller is not permitted to perform the requested action.
            1021 - The actor specified for the suspension record is not valid.

        Args:
            club_id: Club ID
        """
        url = self.CLUBACCOUNTS_URL + f"/clubs/clubid({club_id})/suspension/owner"
        resp = await self.client.session.delete(
            url, headers=self.HEADERS_CLUBACCOUNTS, **kwargs
        )
        resp.raise_for_status()

    # CLUB HUB
    # ---------------------------------------------------------------------------

    @staticmethod
    def _create_search_params(query: str, **kwargs) -> Dict[str, str]:
        if not query:
            raise ValueError("Query must not be empty.")

        params = {"q": query}

        for key, arg in kwargs.items():
            if not isinstance(arg, str) and isinstance(arg, Sequence):
                params[key] = ",".join(arg)
            elif arg is not None:
                params[key] = str(arg)

        return params

    def _create_clubhub_id_endpoint(
        self,
        ids: Union[str, List[str]],
        is_xuid: bool = False,
        decorations: Optional[List[str]] = None,
    ) -> str:
        if isinstance(ids, str):
            ids = [ids]

        if decorations is None:
            decorations = []

        if len(ids) > 10:
            raise ValueError("Endpoint has more ids than the supported maximum (10)")

        id_subpath = "Ids" if not is_xuid else "Xuid"
        endpoint = self.CLUBHUB_URL + f"/clubs/{id_subpath}({self.SEPARATOR.join(ids)})"
        if decorations:
            endpoint += f"/decoration/{(','.join(decorations))}"

        return endpoint

    async def _send_clubhub_decoration_request(
        self, club_ids: Union[str, List[str]], decorations: List[str], **kwargs
    ) -> SearchClubsResponse:
        """
        Send a clubhub request with the given decorations and return the response.

        XLE error codes:
            200 - Successfully got Clubs.
            1018 - User not permitted to perform the requested action.

        Args:
            club_ids: List of club IDs
            decorations: URI decorations to specify extra information to request.

        Returns:
            :class:`List[Club]`: List of Clubs
        """

        url = self._create_clubhub_id_endpoint(club_ids, decorations=decorations)

        resp = await self.client.session.get(
            url, headers=self.HEADERS_CLUBHUB, **kwargs
        )
        resp.raise_for_status()

        return SearchClubsResponse.parse_raw(resp.text)

    async def get_club(
        self, club_id: str, decorations: Optional[List[str]] = None, **kwargs
    ) -> Club:
        """
        Get a club through its id.

        Args:
            club_id: Club ID
            decorations: URI decorations to specify extra information to request.

        Returns:
            :class:`List[Club]`: List of Clubs
        """
        return (await self.get_clubs([club_id], decorations, **kwargs))[0]

    async def get_clubs(
        self, club_ids: List[str], decorations: Optional[List[str]] = None, **kwargs
    ) -> List[Club]:
        """
        Get clubs through their ids.

        Args:
            club_ids: List of club IDs
            decorations: URI decorations to specify extra information to request.

        Returns:
            :class:`List[Club]`: List of Clubs
        """

        if decorations is None:
            decorations = [
                "detail",
                "clubPresence",
                "roster(member moderator requestedToJoin banned recommended)",
                "settings",
            ]

        return [
            club
            for club in (
                await self._send_clubhub_decoration_request(
                    club_ids, decorations=decorations, **kwargs
                )
            ).clubs
        ]

    async def get_club_associations(
        self, xuid: Optional[str] = None, **kwargs
    ) -> List[Club]:
        """
        Get clubs associated with the given xuid.

        XLE error codes:
            200 - Successfully obtained club associations.
            1018 - User not permitted to perform the requested action.

        Args:
            xuid: User to get clubs for, defaults to caller.

        Returns:
            :class:`List[Club]`: List of Clubs
        """
        xuid = xuid or self.client.xuid

        url = self._create_clubhub_id_endpoint(
            xuid, is_xuid=True, decorations=["detail"]
        )
        resp = await self.client.session.get(
            url, headers=self.HEADERS_CLUBHUB, **kwargs
        )
        resp.raise_for_status()

        return [club for club in SearchClubsResponse.parse_raw(resp.text).clubs]

    async def get_club_recommendations(
        self, title_id: Optional[str] = None, **kwargs
    ) -> List[Club]:
        """
        Get clubs recommendations for the caller.

        XLE error codes:
            200 - Successfully obtained club recommendations.
            1023 - Failed to get club recommendations.

        Args:
            title_id: If provided, get recommendation for the given title

        Returns:
            :class:`List[Club]`: List of Clubs
        """

        method = self.client.session.post
        endpoint = "/clubs/recommendations"
        if title_id:
            method = self.client.session.get
            endpoint += f"ByTitle({title_id})"
        endpoint += "/decoration/detail"

        url = self.CLUBHUB_URL + endpoint
        resp = await method(url, headers=self.HEADERS_CLUBHUB, **kwargs)
        resp.raise_for_status()

        return [club for club in SearchClubsResponse.parse_raw(resp.text).clubs]

    async def search_clubs(
        self,
        query: str,
        titles: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        count: Optional[int] = None,
        **kwargs,
    ) -> SearchClubsResponse:
        """
        Search for clubs with the given query.

        XLE error codes:
            200 - Successful obtained club search results.
            1024 - Failed to get club search results.

        Args:
            query: Search query that looks at club names/descriptions
            titles: Title IDs that clubs must be associated with
            tags: Tags that clubs must have
            count: How many clubs to obtain

        Returns:
            :class:`SearchClubsResponse`: Search Clubs Response
        """
        params = self._create_search_params(
            query, titles=titles, tags=tags, count=count
        )

        url = self.CLUBHUB_URL + f"/clubs/search"
        resp = await self.client.session.get(
            url, headers=self.HEADERS_CLUBHUB, params=params or None, **kwargs
        )
        resp.raise_for_status()

        return SearchClubsResponse.parse_raw(resp.text)

    # CLUB PRESENCE
    # ---------------------------------------------------------------------------

    async def get_presence_counts(self, club_id: str, **kwargs) -> GetPresenceResponse:
        """
        Get presence counts for the given club id.

        XLE error codes:
            200 - Successful obtained club presence counts.
            1005 - ClubId is malformed or not within the valid range.

        Args:
            club_id: Club ID

        Returns:
            :class:`GetPresenceResponse`: Get Presence Response
        """
        url = self.CLUBPRESENCE_URL + f"/clubs/{club_id}/users/count"
        resp = await self.client.session.get(
            url, headers=self.HEADERS_CLUBPRESENCE, **kwargs
        )
        resp.raise_for_status()

        return GetPresenceResponse.parse_raw(resp.text)

    async def set_presence_within_club(
        self, club_id: str, xuid: str, presence: ClubPresence, **kwargs
    ) -> bool:
        """Set your presence in a clubs to the given ClubPresence value.

        Codes:
            204 - Successfully changed presence.
            1004 - The claims are invalid.
            1005 - ClubId is malformed or not within the valid range.
            1006 - Request payload was not understood by the service.
            1006 - Identity used in the request URL was malformed

        Args:
            club_id: Club ID
            xuid: Xbox user ID to use
            presence: Presence to set; InGame and InParty do not seem to work through this API
        """
        # Microsoft.Xbox.Services.dll --- xbox::services::clubs::clubs::set_presence_within_club
        data = {"userPresenceState": presence}

        url = self.CLUBPRESENCE_URL + f"/clubs/{club_id}/users/xuid({xuid})"
        resp = await self.client.session.post(
            url, headers=self.HEADERS_CLUBPRESENCE, json=data, **kwargs
        )

        return resp.status == 204

    # CLUB PROFILE
    # ---------------------------------------------------------------------------

    async def update_club_profile(self, club_id: str, **setting_values) -> None:
        """Update club profile settings.

        Settings are passed in as kwarg pairs.

        XLE error codes:
            200 - Successfully updated club profile.
            413 - Description is too large (500 char max).
            1004 - Unable to parse the request.
            1006 - Text Moderation Failed to validate setting.
            1100 - Insufficient permissions for write request.

        Args:
            club_id: Club ID
            setting_values: Each setting name must be a valid ClubSettingsContract field
                All values that fail are passed in as an HTTP kwarg
        """
        contract = ClubSettingsContract()
        modified_fields = []
        request_kwargs = {}

        for key, value in setting_values.items():
            # Skip if not valid setting name.
            if key not in ClubSettingsContract.__fields__:
                request_kwargs[key] = value
                continue

            # Update contract fields with new values.
            # If a value is None, omit it in the contract.
            if value is not None:
                setattr(contract, key, value)

            # Ensure modifiedFields are PascalCase.
            modified_fields.append(to_pascal(key))

        data = {
            "requestContract": json.loads(contract.json()),
            "modifiedFields": modified_fields,
        }

        url = self.CLUBPROFILE_URL + f"/clubs/{club_id}/profile"
        resp = await self.client.session.post(
            url, headers=self.HEADERS_CLUBPROFILE, json=data, **request_kwargs
        )
        resp.raise_for_status()

    # CLUB ROSTER
    # ---------------------------------------------------------------------------

    async def _update_users_club_roles(
        self, club_id: str, xuid: str, advance: bool, **kwargs
    ) -> UpdateRolesResponse:
        """
        Add or remove an xuid from a club id.

        Affects the following roles:
            ClubRole.MEMBER
            ClubRole.REQUESTED_TO_JOIN
            ClubRole.RECOMMENDED
            ClubRole.INVITED

        XLE error codes:
            200 - Successfully updated user's club role.
            1013 - Cannot remove owner from the clubs.
            1016 - Club has disabled join requests or the club is secret.
            1019 - Target Club has been suspended.

        Args:
            club_id: Club ID
            xuid: Xbox user ID
            advance: Whether to add or remove to club

        Returns:
            :class:`UpdateRolesResponse`: Update Roles Response
        """
        url = self.CLUBROSTER_URL + f"/clubs/{club_id}/users/xuid({xuid})"
        if advance:
            method = self.client.session.put
        else:
            method = self.client.session.delete

        resp = await method(url, headers=self.HEADERS_CLUBROSTER, **kwargs)
        resp.raise_for_status()

        return UpdateRolesResponse.parse_raw(resp.text)

    async def _set_users_club_roles(
        self, club_id: str, xuid: str, role: ClubRole, add_role: bool, **kwargs
    ) -> UpdateRolesResponse:
        """
        Add or remove a club role from an xuid.

        Can only modify the following roles:
            ClubRole.MODERATOR
            ClubRole.BANNED
            ClubRole.FOLLOWER

        XLE error codes:
            1001 - Caller role insufficient to perform the requested action.
            1003 - Target club does not exist.
            1008 - Request payload was not understood by the service.
            1011 - Requested roles cannot be explicitly modified.
            1012 - Cannot modify ban status due to permissions or request format.
            1015 - Cannot modify follow status due to permissions or request format.

        Args:
            club_id: Club ID
            xuid: Xbox user ID
            role: Club role to modify
            add_role: Whether to add or remove role from user

        Returns:
            :class:`UpdateRolesResponse`: Update Roles Response
        """
        data = {}
        url = self.CLUBROSTER_URL + f"/clubs/{club_id}/users/xuid({xuid})/roles"
        if add_role:
            method = self.client.session.post
            data["roles"] = [role]
        else:
            method = self.client.session.delete
            url += f"/{role}"

        resp = await method(url, headers=self.HEADERS_CLUBROSTER, json=data, **kwargs)
        resp.raise_for_status()

        return UpdateRolesResponse.parse_raw(resp.text)

    async def add_user_to_club(
        self, club_id: str, xuid: Optional[str] = None, **kwargs
    ) -> UpdateRolesResponse:
        """Add user to the given club.

        This can result in the following roles being modified:
            ClubRole.FOLLOWER - Given after joining
            ClubRole.MEMBER - Given after joining
            ClubRole.REQUESTED_TO_JOIN - Given after requesting to join a club
            ClubRole.RECOMMENDED - Given after being recommended by a club member
            ClubRole.INVITED - Given after being invited by a club member or moderator

        Args:
            club_id: Club ID
            xuid: Xbox user ID. If not provided, defaults to caller xuid

        Returns:
            :class:`UpdateRolesResponse`: Update Roles Response
        """
        xuid = xuid or self.client.xuid

        return await self._update_users_club_roles(
            club_id, xuid, advance=True, **kwargs
        )

    async def remove_user_from_club(
        self, club_id: str, xuid: Optional[str] = None, **kwargs
    ) -> UpdateRolesResponse:
        """Remove user from the given club.

        Args:
            club_id: Club ID
            xuid: Xbox user ID. If not provided, defaults to caller xuid

        Returns:
            :class:`UpdateRolesResponse`: Update Roles Response
        """
        xuid = xuid or self.client.xuid

        return await self._update_users_club_roles(
            club_id, xuid, advance=False, **kwargs
        )

    async def follow_club(self, club_id: str, **kwargs) -> UpdateRolesResponse:
        return await self._set_users_club_roles(
            club_id, self.client.xuid, ClubRole.FOLLOWER, True, **kwargs
        )

    async def unfollow_club(self, club_id: str, **kwargs) -> UpdateRolesResponse:
        return await self._set_users_club_roles(
            club_id, self.client.xuid, ClubRole.FOLLOWER, False, **kwargs
        )

    async def ban_user_from_club(
        self, club_id: str, xuid: str, **kwargs
    ) -> UpdateRolesResponse:
        return await self._set_users_club_roles(
            club_id, xuid, ClubRole.BANNED, True, **kwargs
        )

    async def unban_user_from_club(
        self, club_id: str, xuid: str, **kwargs
    ) -> UpdateRolesResponse:
        return await self._set_users_club_roles(
            club_id, xuid, ClubRole.BANNED, False, **kwargs
        )

    async def add_club_moderator(
        self, club_id: str, xuid: str, **kwargs
    ) -> UpdateRolesResponse:
        return await self._set_users_club_roles(
            club_id, xuid, ClubRole.MODERATOR, True, **kwargs
        )

    async def remove_club_moderator(
        self, club_id: str, xuid: str, **kwargs
    ) -> UpdateRolesResponse:
        return await self._set_users_club_roles(
            club_id, xuid, ClubRole.MODERATOR, False, **kwargs
        )
