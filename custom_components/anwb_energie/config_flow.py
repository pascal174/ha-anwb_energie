"""Config flow voor ANWB Energie."""
from __future__ import annotations

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN


class ANWBEnergieConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow voor ANWB Energie Tarieven."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        # Voorkom dubbele installatie
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title="ANWB Energie Tarieven", data={})

        return self.async_show_form(step_id="user")
