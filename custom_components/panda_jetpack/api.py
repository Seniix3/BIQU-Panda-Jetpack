"""WebSocket API client for the BTT Panda Jetpack (Bifrost Engine).

Het apparaat heeft geen HTTP API; alle bediening loopt via een WebSocket
op ws://<host>/ws. Direct na het verbinden stuurt het apparaat een JSON-dump
met de volledige status. Commando's zijn JSON-berichten van de vorm:

    {"settings": {"rgb_info_mode": 9, "on": 1}}
    {"settings": {"rgb_info_brightness": 50}}
    {"settings": {"rgb_info_speed": 50}}
    {"settings": {"rgb_info_mode": 3}}          # effect wisselen

Het apparaat pusht geen status-updates na wijzigingen; daarom gebruiken we
korte verbindingen (connect -> lezen/sturen -> sluiten) en pollen we periodiek.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any

import aiohttp


class PandaJetpackError(Exception):
    """Raised when communication with the device fails."""


class PandaJetpackApi:
    """Minimal async client for the Panda Jetpack WebSocket API."""

    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        self._host = host
        self._session = session
        self._lock = asyncio.Lock()

    @property
    def host(self) -> str:
        return self._host

    @property
    def ws_url(self) -> str:
        return f"ws://{self._host}/ws"

    async def _connect(self) -> aiohttp.ClientWebSocketResponse:
        try:
            return await self._session.ws_connect(
                self.ws_url, receive_timeout=10, heartbeat=None
            )
        except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as err:
            raise PandaJetpackError(f"Cannot connect to {self.ws_url}: {err}") from err

    async def _read_initial_dump(
        self, ws: aiohttp.ClientWebSocketResponse
    ) -> dict[str, Any]:
        """Read the full state dump the device sends right after connecting."""
        try:
            msg = await ws.receive(timeout=10)
        except asyncio.TimeoutError as err:
            raise PandaJetpackError("Timeout waiting for device state") from err
        if msg.type != aiohttp.WSMsgType.TEXT:
            raise PandaJetpackError(f"Unexpected WebSocket message: {msg.type}")
        try:
            return json.loads(msg.data)
        except ValueError as err:
            raise PandaJetpackError("Device sent invalid JSON") from err

    @staticmethod
    def parse_state(raw: dict[str, Any]) -> dict[str, Any]:
        """Reduce the raw device dump to the fields we care about."""
        settings = raw.get("settings", {})
        mode = int(settings.get("current_mode", 0))

        # Per-effect instellingen staan in list2; pak die van de actieve mode
        active: dict[str, Any] = {}
        for item in settings.get("list2", []):
            if int(item.get("rgb_info_mode", -1)) == mode:
                active = item
                break

        return {
            "on": bool(int(settings.get("on", 0))),
            "mode": mode,
            "brightness": int(active.get("brightness", 50)),
            "speed": int(active.get("speed", 50)),
            "fw_version": settings.get("fw_version"),
            "hostname": raw.get("sta", {}).get("hostname"),
            "ap_ssid": raw.get("ap", {}).get("ssid"),
        }

    async def get_state(self) -> dict[str, Any]:
        """Connect, read the state dump, disconnect."""
        async with self._lock:
            ws = await self._connect()
            try:
                return self.parse_state(await self._read_initial_dump(ws))
            finally:
                await ws.close()

    async def send_settings(self, **settings: Any) -> None:
        """Send a settings command, e.g. send_settings(rgb_info_mode=9, on=1)."""
        async with self._lock:
            ws = await self._connect()
            try:
                # Eerst de initiële dump weglezen, dan het commando sturen
                await self._read_initial_dump(ws)
                await ws.send_str(json.dumps({"settings": settings}))
                # Het apparaat even de tijd geven het frame te verwerken
                await asyncio.sleep(0.2)
            except (aiohttp.ClientError, OSError) as err:
                raise PandaJetpackError(f"Failed to send command: {err}") from err
            finally:
                await ws.close()
