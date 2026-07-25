"""Config flow for the Panda Jetpack integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PandaJetpackApi, PandaJetpackError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


class PandaJetpackConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Panda Jetpack."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            api = PandaJetpackApi(host, async_get_clientsession(self.hass))
            try:
                state = await api.get_state()
            except PandaJetpackError:
                _LOGGER.exception("Cannot connect to Panda Jetpack at %s", host)
                errors["base"] = "cannot_connect"
            else:
                # AP-SSID bevat het MAC-adres en is dus een stabiele unique_id
                unique_id = state.get("ap_ssid") or host
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=state.get("hostname") or "Panda Jetpack",
                    data={CONF_HOST: host},
                )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
