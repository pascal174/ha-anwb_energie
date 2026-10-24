"""Sensoren voor ANWB Energie Tarieven."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import ANWBEnergieCoordinator
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: ANWBEnergieCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        ANWBSensor(coordinator, entry, "marktprijs", "huidig",  "Marktprijs",           "mdi:lightning-bolt"),
        ANWBSensor(coordinator, entry, "allInPrijs", "huidig",  "All-in prijs",         "mdi:lightning-bolt-circle"),
        ANWBSensor(coordinator, entry, "marktprijs", "volgend", "Volgend uur marktprijs", "mdi:lightning-bolt-outline"),
        ANWBSensor(coordinator, entry, "allInPrijs", "volgend", "Volgend uur all-in",   "mdi:clock-fast"),
    ])


class ANWBSensor(CoordinatorEntity, SensorEntity):
    """Sensor voor een ANWB energietarief."""

    # ct/kWh heeft geen passende SensorDeviceClass (MONETARY eist een valuta-eenheid).
    _attr_native_unit_of_measurement = "ct/kWh"
    _attr_state_class = SensorStateClass.MEASUREMENT
    # De prijslijst is groot en hoeft niet in de recorder-database.
    _unrecorded_attributes = frozenset({"prijzen"})

    def __init__(
        self,
        coordinator: ANWBEnergieCoordinator,
        entry: ConfigEntry,
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
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="ANWB Energie",
            manufacturer="ANWB",
            entry_type=DeviceEntryType.SERVICE,
        )

    def _entry(self) -> dict | None:
        data = self.coordinator.data
        return data.get(self._periode) if data else None

    @property
    def available(self) -> bool:
        """Niet beschikbaar als de API voor deze periode geen prijs levert."""
        entry = self._entry()
        return (
            super().available
            and entry is not None
            and entry["values"].get(self._prijstype) is not None
        )

    @property
    def native_value(self) -> float | None:
        entry = self._entry()
        if not entry:
            return None
        val = entry["values"].get(self._prijstype)
        return round(val, 4) if val is not None else None

    @property
    def extra_state_attributes(self) -> dict:
        entry = self._entry()
        if not entry:
            return {}
        attrs = {
            "tijdstip": dt_util.as_local(dt_util.parse_datetime(entry["date"])).strftime("%d-%m-%Y %H:%M"),
            "periode":  self._periode,
        }
        if self._periode == "huidig":
            attrs.update(self._dagprijzen())
        return attrs

    def _dagprijzen(self) -> dict:
        """Prijslijst en goedkoopste/duurste uur van vandaag voor dit prijstype."""
        prijzen = []
        for d in self.coordinator.data.get("alle", []):
            val = d["values"].get(self._prijstype)
            if val is None:
                continue
            prijzen.append({
                "start": dt_util.as_local(dt_util.parse_datetime(d["date"])).isoformat(),
                "prijs": round(val, 4),
            })

        vandaag = dt_util.now().date().isoformat()
        vandaag_prijzen = [p for p in prijzen if p["start"][:10] == vandaag]

        attrs = {"prijzen": prijzen}
        if vandaag_prijzen:
            laagste = min(vandaag_prijzen, key=lambda p: p["prijs"])
            hoogste = max(vandaag_prijzen, key=lambda p: p["prijs"])
            attrs.update({
                "goedkoopste_uur_vandaag": laagste["start"],
                "goedkoopste_prijs_vandaag": laagste["prijs"],
                "duurste_uur_vandaag": hoogste["start"],
                "duurste_prijs_vandaag": hoogste["prijs"],
            })
        return attrs
