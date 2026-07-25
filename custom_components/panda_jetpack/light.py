"""Light platform for the Panda Jetpack integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, EFFECTS
from .entity import PandaJetpackEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    unique_id = entry.unique_id or entry.data["host"]
    async_add_entities(
        [PandaJetpackLight(data["coordinator"], data["api"], unique_id)]
    )


class PandaJetpackLight(PandaJetpackEntity, LightEntity):
    """De LED-strip van de Panda Jetpack als light-entiteit."""

    _attr_name = None  # gebruik de apparaatnaam
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = EFFECTS

    def __init__(self, coordinator, api, unique_id: str) -> None:
        super().__init__(coordinator, api, unique_id)
        self._attr_unique_id = f"{unique_id}_light"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data["on"])

    @property
    def brightness(self) -> int:
        # Apparaat: 0-100, Home Assistant: 0-255
        return round(self.coordinator.data["brightness"] * 255 / 100)

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        return self.coordinator.data["rgb"]

    @property
    def effect(self) -> str | None:
        mode = self.coordinator.data["mode"]
        if 0 <= mode < len(EFFECTS):
            return EFFECTS[mode]
        return None

    def _optimistic(self, **changes: Any) -> None:
        """Werk de coordinator-data direct bij zonder op de poll te wachten."""
        new_data = dict(self.coordinator.data)
        new_data.update(changes)
        self.coordinator.async_set_updated_data(new_data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        data = self.coordinator.data
        mode = data["mode"]
        changes: dict[str, Any] = {}

        if ATTR_EFFECT in kwargs:
            mode = EFFECTS.index(kwargs[ATTR_EFFECT])
            await self.api.send_settings(rgb_info_mode=mode)
            changes["mode"] = mode

        if not data["on"]:
            await self.api.send_settings(rgb_info_mode=mode, on=1)
            changes["on"] = True

        if ATTR_RGB_COLOR in kwargs:
            r, g, b = kwargs[ATTR_RGB_COLOR]
            await self.api.send_settings(
                rgb_info_mode=mode, rgb_rgba=f"#{r:02X}{g:02X}{b:02X}FF"
            )
            changes["rgb"] = (r, g, b)

        if ATTR_BRIGHTNESS in kwargs:
            pct = max(0, min(100, round(kwargs[ATTR_BRIGHTNESS] * 100 / 255)))
            await self.api.send_settings(rgb_info_brightness=pct)
            changes["brightness"] = pct

        self._optimistic(**changes)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.api.send_settings(
            rgb_info_mode=self.coordinator.data["mode"], on=0
        )
        self._optimistic(on=False)
