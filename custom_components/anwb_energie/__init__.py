"""ANWB Energie Tarieven integratie."""
from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_URL, SCAN_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = ANWBEnergieCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class ANWBEnergieCoordinator(DataUpdateCoordinator):
    """Haalt tariefdata op van de ANWB API."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict:
        from datetime import datetime, timezone, timedelta as td

        nl_tz = timezone(td(hours=2))
        now_utc = datetime.now(timezone.utc)
        start = now_utc
        end = now_utc + td(days=1)

        params = {
            "startDate": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "endDate":   end.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "interval":  "HOUR",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    API_URL,
                    params=params,
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    resp.raise_for_status()
                    json_data = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Fout bij ophalen ANWB data: {err}") from err

        data = json_data.get("data", [])
        if not data:
            raise UpdateFailed("Geen data ontvangen van ANWB API")

        nu_uur = now_utc.strftime("%Y-%m-%dT%H")
        volgend_uur = (now_utc + td(hours=1)).strftime("%Y-%m-%dT%H")

        huidig  = next((d for d in data if d["date"][:13] == nu_uur), data[0])
        volgend = next((d for d in data if d["date"][:13] == volgend_uur), None)

        return {
            "huidig":  huidig,
            "volgend": volgend,
        }
