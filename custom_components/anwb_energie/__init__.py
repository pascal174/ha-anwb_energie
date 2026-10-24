"""ANWB Energie Tarieven integratie."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import DOMAIN, API_URL

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = ANWBEnergieCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Trigger elke keer 1 seconde na een heel uur
    @callback
    def handle_hour_change(now):
        hass.async_create_task(coordinator.async_refresh())

    entry.async_on_unload(
        async_track_time_change(hass, handle_hour_change, minute=0, second=1)
    )

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
            # Geen automatisch interval, wordt aangestuurd door async_track_time_change
            update_interval=None,
        )

    async def _async_update_data(self) -> dict:
        now_utc = datetime.now(timezone.utc)
        # Hele lokale dag van vandaag tot en met morgen, zodat een dagprijslijst
        # (goedkoopste/duurste uur) mogelijk is.
        start = dt_util.start_of_local_day()
        end = dt_util.start_of_local_day(dt_util.now().date() + timedelta(days=2))

        params = {
            "startDate": dt_util.as_utc(start).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "endDate":   dt_util.as_utc(end).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "interval":  "HOUR",
        }

        try:
            session = async_get_clientsession(self.hass)
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

        # Uren waarvoor ANWB (nog) geen prijs heeft, komen terug met lege waarden.
        data = [
            d for d in json_data.get("data", [])
            if any(v is not None for v in d.get("values", {}).values())
        ]
        if not data:
            raise UpdateFailed("Geen data ontvangen van ANWB API")

        # De API levert lokale tijd met offset (bijv. +02:00); vergelijk op
        # echte tijdstippen zodat zomer/wintertijd correct verloopt.
        uur = timedelta(hours=1)
        huidig = next(
            (
                d for d in data
                if (start_uur := dt_util.parse_datetime(d["date"])) is not None
                and start_uur <= now_utc < start_uur + uur
            ),
            None,
        )
        if huidig is None:
            raise UpdateFailed("Geen prijs gevonden voor het huidige uur")

        volgend_start = dt_util.parse_datetime(huidig["date"]) + uur
        volgend = next(
            (d for d in data if dt_util.parse_datetime(d["date"]) == volgend_start),
            None,
        )

        return {
            "huidig":  huidig,
            "volgend": volgend,
            "alle":    data,
        }
