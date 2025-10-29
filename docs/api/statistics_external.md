# Statistics Models (External)

## Travel Impact Model (Google)

The Google [Travel Impact Model (TIM)](https://travelimpactmodel.org) estimates flight fuel consumption and associated emissions using the Tier 3A methodology (flight-specific, Origin-Destination approach) defined in the EMEP/EEA Annex 1.A.3.a Aviation 2023. For each scheduled flight, fuel consumption is calculated by combining data from standard databases for two phases:

- **LTO phase (Taxi, Takeoff, Landing):** Fixed fuel burn calculated using [ICAO Aircraft Engine Emissions Databank (AEED)](https://www.easa.europa.eu/en/domains/environment/icao-aircraft-engine-emissions-databank) standards (LTO cycle fuel flow/emission indices).
- **CCD phase (Climb, Cruise, Descent):** Variable fuel burn derived from EUROCONTROL Advanced Emission Model (AEM)/Base of Aircraft Data (BADA) performance modeling, adjusted for real-world routing and calculated via linear interpolation/extrapolation for stage length.

Total fuel is converted to CO₂-equivalent using [ISO 14083](https://www.iso.org/standard/78864.html)-compliant Well-to-Wake (WTW) life-cycle factors (3.8359 kg CO₂e/kg fuel). The final passenger estimate is derived via a three-step apportionment process: allocating total emissions between cargo and passenger payloads using the mass-based approach, normalizing passenger count via statistical load factors, and applying cabin class weightings based on actual or median seat configuration data.

This model is integrated into the Google Flights interface and displays the CO₂-equivalent values to users searching for flight options:

![Google Flights showing Travel Impact Model emissions](../_static/screenshots/google_flights_tim.png)
*Example of CO₂ emissions displayed in Google Flights search results.*

!!! note
    The Travel Impact Model can also be accessed via a free, publicly available API provided by Google. The API allows developers to retrieve flight-level CO₂e emission estimates by specifying the following parameters: origin, destination, operating carrier, flight number, and departure date. For more information, see the [Google Travel Impact Model API documentation](https://developers.google.com/travel/impact-model).

!!! note
    The Travel Impact Model in Google Flights only shows emissions for _future_ flights (which can still be booked). It does not provide emissions data for past flights.

!!! reference "See Also"
    - [Google Travel Impact Model Website](https://travelimpactmodel.org)
    - [Google Travel Impact Model API Documentation](https://developers.google.com/travel/impact-model)

!!! reference "References"
    [EMEP/EEA Air Pollutant Emission Inventory Guidebook 2023 (Annex 1.A.3.a Aviation)](https://www.eea.europa.eu/en/analysis/publications/emep-eea-guidebook-2023)
