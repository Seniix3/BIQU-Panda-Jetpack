"""Number platform for the Panda Jetpack integration (effect speed)."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
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
            PandaJetpackSpeed(data["coordinator"], data["api"], unique_id),
            PandaJetpackBrightness(data["coordinator"], data["api"], unique_id),
        ]
    )


class PandaJetpackSpeed(PandaJetpackEntity, NumberEntity):
    """Snelheid van het actieve lichteffect.

    Alleen relevant voor bewegende effecten (Breathing, Wave, Marquee, etc.);
    bij Static en H2D Style doet deze waarde niets.
    """

    _attr_name = "Effect speed"
    _attr_icon = "mdi:speedometer"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, api, unique_id: str) -> None:
        super().__init__(coordinator, api, unique_id)
        self._attr_unique_id = f"{unique_id}_speed"

    @property
    def native_value(self) -> int:
        return int(self.coordinator.data["speed"])

    async def async_set_native_value(self, value: float) -> None:
        await self.api.send_settings(rgb_info_speed=int(value))
        new_data = dict(self.coordinator.data)
        new_data["speed"] = int(value)
        self.coordinator.async_set_updated_data(new_data)


class PandaJetpackBrightness(PandaJetpackEntity, NumberEntity):
    """Helderheid (0-100%) als losse slider op de apparaatpagina.

    Stuurt dezelfde rgb_info_brightness als de light-entiteit; beide blijven
    synchroon via de coordinator. Let op: het apparaat bewaart de helderheid
    per lichteffect.
    """

    _attr_name = "Brightness"
    _attr_icon = "mdi:brightness-6"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator, api, unique_id: str) -> None:
        super().__init__(coordinator, api, unique_id)
        self._attr_unique_id = f"{unique_id}_brightness"

    @property
    def native_value(self) -> int:
        return int(self.coordinator.data["brightness"])

    async def async_set_native_value(self, value: float) -> None:
        await self.api.send_settings(rgb_info_brightness=int(value))
        new_data = dict(self.coordinator.data)
        new_data["brightness"] = int(value)
        self.coordinator.async_set_updated_data(new_data)
