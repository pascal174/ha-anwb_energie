# ANWB Energie Tarieven — Home Assistant Integratie

Haalt actuele en volgende uur stroomprijzen op via de ANWB Energie API.

## Sensoren

| Sensor | Beschrijving |
|--------|-------------|
| `sensor.anwb_energie_marktprijs` | Marktprijs huidig uur (ct/kWh) |
| `sensor.anwb_energie_all_in_prijs` | All-in prijs huidig uur (ct/kWh) |
| `sensor.anwb_energie_volgend_uur_marktprijs` | Marktprijs volgend uur (ct/kWh) |
| `sensor.anwb_energie_volgend_uur_all_in` | All-in prijs volgend uur (ct/kWh) |

Alle sensoren horen bij één apparaat **ANWB Energie**. Als ANWB voor het volgende uur nog geen prijs heeft, staan de "volgend uur"-sensoren op *niet beschikbaar*.

### Attributen

De sensoren voor het huidige uur (`marktprijs` en `all_in_prijs`) hebben extra attributen, handig voor grafieken en automatiseringen:

| Attribuut | Beschrijving |
|-----------|-------------|
| `prijzen` | Lijst met `start` (lokale tijd) en `prijs` voor vandaag en, zodra gepubliceerd, morgen |
| `goedkoopste_uur_vandaag` / `goedkoopste_prijs_vandaag` | Goedkoopste uur van vandaag |
| `duurste_uur_vandaag` / `duurste_prijs_vandaag` | Duurste uur van vandaag |

Het attribuut `prijzen` wordt niet in de recorder-database opgeslagen.

## Installatie via HACS

1. Ga naar HACS → Integraties → ⋮ → Aangepaste repositories
2. Voeg jouw GitHub URL toe als **Integratie**
3. Zoek "ANWB Energie" en installeer
4. Herstart Home Assistant
5. Ga naar Instellingen → Apparaten & Diensten → Integratie toevoegen → **ANWB Energie Tarieven**

## Handmatige installatie

Kopieer de map `custom_components/anwb_energie` naar je Home Assistant `config/custom_components/` map en herstart.
