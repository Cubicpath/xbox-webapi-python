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

    async def get_club_summary(
        self, club_id: str, actor: Optional[str] = None, **kwargs
    ) -> ClubSummary:
        """Get a summary of a given club's information.

        You must own the club to use this method.

        Codes
            - 1021: The actor specified for the suspension record is not valid.
        """
        url = self.CLUBACCOUNTS_URL + f"/clubs/clubid({club_id})"
        if actor:
            url += f"/suspension/{actor}"

        resp = await self.client.session.get(
            url, headers=self.HEADERS_CLUBACCOUNTS, **kwargs
        )
        resp.raise_for_status()

        return ClubSummary.parse_raw(resp.text)

    async def get_clubs_owned(self, **kwargs) -> OwnedClubsResponse:
        """Get list of clubs owned by the caller."""
        headers = self.HEADERS_CLUBACCOUNTS | {"x-xbl-contract-version": "2"}

        url = self.CLUBACCOUNTS_URL + f"/users/xuid({self.client.xuid})/clubsowned"

        resp = await self.client.session.get(url, headers=headers, **kwargs)
        resp.raise_for_status()

        return OwnedClubsResponse.parse_raw(resp.text)

    async def claim_club_name(self, name: str, **kwargs) -> ClubReservation:
        """Reserve a club name for use in create_club().

        Codes
            - 200: Successfully claimed club.
            - 1000: A parallel write operation took precedence over your request.
            - 1007: The requested club name contains invalid characters.
                    Club names must only use letter, numbers, and spaces.
            - 1010: The requested club name is not available.
            - 1023: The requested club name was rejected.
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
        """Create a club with the given name and visibility.

        If creating a public club, you must first call claim_club_name() with the name you want to use.

        Codes
            - 201: Successfully created club.
            - 409: Another pending operation in progress.
            - 1007: The requested club name contains invalid characters.
                    Club names must only use letter, numbers, and spaces.
            - 1014: The club name has not been reserved by the calling user.
                    This happens when club_type is not HIDDEN and you have not
                    called claim_club_name().
            - 1023: The requested club name was rejected.
            - 1038: A TitleFamilyId value must be specified when requesting a TitleClub
                    (genre is ClubGenre.TITLE but title_family_id is not provided).
            - 1041: The calling title is not authorized to perform the requested action with the requested TitleFamilyId
            - 1042: The club genre is not valid.
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
        """Transfer club ownership to the given xuid.

        Codes
            - 1015: The requested club is not available.
        """
        data = {"method": "TransferOwnership", "user": xuid}

        url = self.CLUBACCOUNTS_URL + f"/clubs/clubid({club_id})"

        resp = await self.client.session.post(
            url, headers=self.HEADERS_CLUBACCOUNTS, json=data, **kwargs
        )
        resp.raise_for_status()

        return ClubSummary.parse_raw(resp.text)

    async def rename_club(self, club_id: str, name: str, **kwargs) -> ClubSummary:
        """Rename a club with the given name.

        A club can only be renamed once.

        Codes
            - 201: Successfully created club.
            - 409: Another pending operation in progress.
            - 1007: The requested club name contains invalid characters.
                    Club names must only use letter, numbers, and spaces.
            - 1014: The club name has not been reserved by the calling user.
                    This happens when club_type is not HIDDEN and you have not
                    called claim_club_name().
            - 1023: The requested club name was rejected.
            - 1035: The name cannot be changed for the requested club. All available name changes have been used.
        """
        data = {"method": "ChangeName", "name": name}

        url = self.CLUBACCOUNTS_URL + f"/clubs/clubid({club_id})"

        resp = await self.client.session.post(
            url, headers=self.HEADERS_CLUBACCOUNTS, json=data, **kwargs
        )
        resp.raise_for_status()

        return ClubSummary.parse_raw(resp.text)

    async def delete_club(self, club_id: str, **kwargs) -> Optional[ClubSummary]:
        """Delete the club with the given id.

        If a club is not hidden and is older than one week you will receive a reservation for the club name,
        and it will be suspended for 7 days before being automatically deleted.

        The reservation should last for 1 day after the club is deleted, but you can double check in the ClubSummary
        reservation_duration_after_suspension_in_hours field.

        Codes
            - 202: Successfully started suspension process.
            - 204: Successfully deleted club.
            - 409: Another pending operation in progress.
        """
        url = self.CLUBACCOUNTS_URL + f"/clubs/clubid({club_id})"

        resp = await self.client.session.delete(
            url, headers=self.HEADERS_CLUBACCOUNTS, **kwargs
        )
        resp.raise_for_status()

        if resp.text:
            return ClubSummary.parse_raw(resp.text)

    async def suspend_club(self, club_id: str, delete_date: datetime, **kwargs) -> None:
        """Delete the club with the given id after the given date.

        The club is suspended in the meantime and can be restored through unsuspend_club().

        Codes
            - 204: Successfully deleted club.
            - 1021: The actor specified for the suspension record is not valid.
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

    async def unsuspend_club(self, club_id: str, **kwargs) -> None:
        """Stop the club deletion & suspension process.

        Codes
            - 204: Successfully unsuspended club.
            - 1021: The actor specified for the suspension record is not valid.
        """
        url = self.CLUBACCOUNTS_URL + f"/clubs/clubid({club_id})/suspension/owner"

        resp = await self.client.session.delete(
            url, headers=self.HEADERS_CLUBACCOUNTS, **kwargs
        )
        resp.raise_for_status()

        return resp

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

        url = self._create_clubhub_id_endpoint(club_ids, decorations=decorations)
        resp = await self.client.session.get(
            url, headers=self.HEADERS_CLUBHUB, **kwargs
        )
        resp.raise_for_status()
        return SearchClubsResponse.parse_raw(resp.text)

    async def get_club(
        self, club_id: str, decorations: Optional[List[str]] = None, **kwargs
    ) -> Club:
        """Get a club through its id."""
        return (await self.get_clubs([club_id], decorations, **kwargs))[0]

    async def get_clubs(
        self, club_ids: List[str], decorations: Optional[List[str]] = None, **kwargs
    ) -> List[Club]:
        """Get club through their ids."""

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
        """Get clubs associated with the given xuid."""
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
        """Get clubs recommendations for the caller."""

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
            - 204: Successfully changed presence.
            - 1004: The claims are invalid.
        """
        # Microsoft.Xbox.Services.dll --- xbox::services::clubs::clubs::set_presence_within_club
        data = {"userPresenceState": presence}

        url = self.CLUBPRESENCE_URL + f"/clubs/{club_id}/users/xuid({xuid})"
        resp = await self.client.session.post(
            url, headers=self.HEADERS_CLUBPRESENCE, json=data, **kwargs
        )
        resp.raise_for_status()
        return resp.status == 204

    # CLUB PROFILE
    # ---------------------------------------------------------------------------
    async def update_club_profile(self, club_id: str, **setting_values) -> None:
        """Update club profile settings.

        Settings are passed in as kwarg pairs. Each setting name must be a valid ClubSettingsContract field.
        All kwargs that fail are passed in as an HTTP kwarg.

        Codes
            - 413: Description is too large (500 char max).
            - 1100: Insufficient permissions for write request.
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
        """Add or remove a xuid from a club id.

        Codes
            - 1013: Cannot remove owner from the clubs.
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
        """Add or remove a club role from a xuid.

        Codes
            - 1001: Caller role insufficient to perform the requested action.
            - 1005: Contract version header was missing or invalid.
            - 1008: Request payload was not understood by the service.
            - 1011: Requested roles cannot be explicitly modified.
            - 1012: Cannot modify ban status due to permissions or request format.
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
        xuid = xuid or self.client.xuid

        return await self._update_users_club_roles(
            club_id, xuid, advance=True, **kwargs
        )

    async def remove_user_from_club(
        self, club_id: str, xuid: Optional[str] = None, **kwargs
    ) -> UpdateRolesResponse:
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
