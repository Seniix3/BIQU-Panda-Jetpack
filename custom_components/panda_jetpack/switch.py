"""Switch platform for the Panda Jetpack integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import PandaJetpackEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    unique_id = entry.unique_id or entry.data["host"]
    async_add_entities(
        [
            PandaJetpackFollowSwitch(data["coordinator"], data["api"], unique_id),
            PandaJetpackWarningSwitch(data["coordinator"], data["api"], unique_id),
        ]
    )


class _PandaJetpackToggle(PandaJetpackEntity, SwitchEntity):
    """Basis voor toggles die als settings-key op het apparaat bestaan."""

    _state_key: str  # key in coordinator.data én in het settings-commando

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data[self._state_key])

    async def _set(self, value: int) -> None:
        # De webinterface stuurt de actieve mode altijd mee; wij dus ook
        await self.api.send_settings(
            rgb_info_mode=self.coordinator.data["mode"],
            **{self._state_key: value},
        )
        new_data = dict(self.coordinator.data)
        new_data[self._state_key] = bool(value)
        self.coordinator.async_set_updated_data(new_data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._set(1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._set(0)


class PandaJetpackFollowSwitch(_PandaJetpackToggle):
    """Volg de verlichting van de printer (Follow Printer Light)."""

    _attr_name = "Follow printer light"
    _attr_icon = "mdi:printer-3d"
    _state_key = "follow"

    def __init__(self, coordinator, api, unique_id: str) -> None:
        super().__init__(coordinator, api, unique_id)
        self._attr_unique_id = f"{unique_id}_follow"


class PandaJetpackWarningSwitch(_PandaJetpackToggle):
    """Waarschuwingskleuren laten voorgaan op het gekozen effect (Warning Override)."""

    _attr_name = "Warning override"
    _attr_icon = "mdi:alert-outline"
    _state_key = "warning_override"

    def __init__(self, coordinator, api, unique_id: str) -> None:
        super().__init__(coordinator, api, unique_id)
        self._attr_unique_id = f"{unique_id}_warning"
