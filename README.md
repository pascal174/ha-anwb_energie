# ANWB Energie Tarieven — Home Assistant Integratie

Haalt actuele en volgende uur stroomprijzen op via de ANWB Energie API.

## Sensoren

| Sensor | Beschrijving |
|--------|-------------|
| `sensor.anwb_energie_marktprijs` | Marktprijs huidig uur (ct/kWh) |
| `sensor.anwb_energie_all_in_prijs` | All-in prijs huidig uur (ct/kWh) |
| `sensor.anwb_energie_volgend_uur_marktprijs` | Marktprijs volgend uur (ct/kWh) |
| `sensor.anwb_energie_volgend_uur_all_in` | All-in prijs volgend uur (ct/kWh) |

## Installatie via HACS

1. Ga naar HACS → Integraties → ⋮ → Aangepaste repositories
2. Voeg jouw GitHub URL toe als **Integratie**
3. Zoek "ANWB Energie" en installeer
4. Herstart Home Assistant
5. Ga naar Instellingen → Apparaten & Diensten → Integratie toevoegen → **ANWB Energie Tarieven**

## Handmatige installatie

Kopieer de map `custom_components/anwb_energie` naar je Home Assistant `config/custom_components/` map en herstart.
