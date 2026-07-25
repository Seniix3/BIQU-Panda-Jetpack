"""Select platform for the Panda Jetpack integration (light effect)."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
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
        [PandaJetpackEffectSelect(data["coordinator"], data["api"], unique_id)]
    )


class PandaJetpackEffectSelect(PandaJetpackEntity, SelectEntity):
    """Het actieve lichteffect als dropdown, direct zichtbaar op de apparaatpagina.

    Dezelfde keuze is ook beschikbaar via de effect-lijst van de light-entiteit;
    beide sturen rgb_info_mode en blijven automatisch synchroon via de coordinator.
    """

    _attr_name = "Light effect"
    _attr_icon = "mdi:palette"
    _attr_options = EFFECTS

    def __init__(self, coordinator, api, unique_id: str) -> None:
        super().__init__(coordinator, api, unique_id)
        self._attr_unique_id = f"{unique_id}_effect"

    @property
    def current_option(self) -> str | None:
        mode = self.coordinator.data["mode"]
        if 0 <= mode < len(EFFECTS):
            return EFFECTS[mode]
        return None

    async def async_select_option(self, option: str) -> None:
        mode = EFFECTS.index(option)
        await self.api.send_settings(rgb_info_mode=mode)
        new_data = dict(self.coordinator.data)
        new_data["mode"] = mode
        self.coordinator.async_set_updated_data(new_data)
