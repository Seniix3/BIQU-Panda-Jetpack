"""Base entity for the Panda Jetpack integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .api import PandaJetpackApi
from .const import DOMAIN


class PandaJetpackEntity(CoordinatorEntity[DataUpdateCoordinator]):
    """Common base: koppelt entiteiten aan één apparaat in het device register."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api: PandaJetpackApi,
        unique_id: str,
    ) -> None:
        super().__init__(coordinator)
        self.api = api
        self._device_unique_id = unique_id
        data = coordinator.data or {}
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=data.get("hostname") or "Panda Jetpack",
            manufacturer="BIGTREETECH",
            model="Panda Jetpack",
            sw_version=data.get("fw_version"),
            configuration_url=f"http://{api.host}/",
        )
