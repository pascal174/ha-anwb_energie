"""Sensoren voor ANWB Energie Tarieven."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ANWBEnergieCoordinator
from .const import DOMAIN

NL_TZ = timezone(timedelta(hours=2))


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ANWBEnergieCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        ANWBSensor(coordinator, "marktprijs",          "huidig",  "Marktprijs",          "mdi:lightning-bolt"),
        ANWBSensor(coordinator, "allInPrijs",          "huidig",  "All-in prijs",         "mdi:lightning-bolt-circle"),
        ANWBSensor(coordinator, "marktprijs",          "volgend", "Volgend uur marktprijs","mdi:lightning-bolt-outline"),
        ANWBSensor(coordinator, "allInPrijs",          "volgend", "Volgend uur all-in",   "mdi:clock-fast"),
    ])


class ANWBSensor(CoordinatorEntity, SensorEntity):
    """Sensor voor een ANWB energietarief."""

    _attr_native_unit_of_measurement = "ct/kWh"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: ANWBEnergieCoordinator,
        prijstype: str,
        periode: str,
        naam: str,
        icon: str,
    ) -> None:
        super().__init__(coordinator)
        self._prijstype = prijstype
        self._periode   = periode
        self._attr_name = f"ANWB Energie {naam}"
        self._attr_unique_id = f"anwb_energie_{periode}_{prijstype}"
        self._attr_icon = icon

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data
        if not data:
            return None
        entry = data.get(self._periode)
        if not entry:
            return None
        val = entry["values"].get(self._prijstype)
        return round(val, 4) if val is not None else None

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data
        if not data:
            return {}
        entry = data.get(self._periode)
        if not entry:
            return {}
        datum_nl = datetime.fromisoformat(entry["date"]).astimezone(NL_TZ)
        return {
            "tijdstip": datum_nl.strftime("%d-%m-%Y %H:%M"),
            "periode":  self._periode,
        }
