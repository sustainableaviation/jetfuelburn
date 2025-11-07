# EU Flight Emissions Label (FEL)

## Overview

The [EU Flight Emissions Label (FEL)](https://www.flightemissions.eu/en) is a voluntary environmental labelling scheme established under [Article 14 of Regulation (EU) 2023/2405 (ReFuelEU Aviation)](https://eur-lex.europa.eu/eli/reg/2023/2405/oj/eng). The label discloses CO₂-equivalent emissions for commercial flights departing from or arriving at EU airports, covering all flights operated by participating airlines.

As of now, participation is voluntary. Once an operator chooses to take part, the FEL must be displayed for all flights in scope, ensuring consistent and non-selective reporting across its network.

The FEL is implemented by EASA through its [Sustainability Portal](https://www.easa.europa.eu/en/domains/environment/sustainability-portal) and uses verified operational data such as fuel burn, passenger load, and SAF share to generate per-flight emissions metrics.

## Label Structure

Each FEL record represents a unique combination:  
`(operator, aircraft_type, configuration, route, season, year)`  

| Metric | Unit | Description |
|:--|:--|:--|
| **CO₂e footprint** | *kg CO₂e / passenger* | Total well-to-wake emissions per passenger |
| **CO₂e efficiency** | *g CO₂e / pax km* | Emissions per passenger-kilometre (great-circle distance basis) |
| **fuel LCE intensity** | *g CO₂e / MJ* | Weighted life-cycle carbon intensity of all fuels uplifted (Jet A-1 + SAF) |

## Regulatory References

### Regulatory Overview
| Reference | Description |
|:--|:--|
| [**§ 14**, Reg. (EU) 2023/2405 (ReFuelEU Aviation)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R2405#art_14) | Establishes the voluntary Flight Emissions Label scheme |
| [**Annex II**, Implementing Reg. (EU) 2024/3170](https://eur-lex.europa.eu/eli/reg_impl/2024/3170/oj/eng#anx_II) | Defines the official methodology for calculating flight emissions |
| [**§ 9 (1)**, Reg. (EU) 2023/2405](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R2405#art_9) | Prohibits duplicate SAF claims across EU ETS, CORSIA and FEL |
| [**§ 14 (9)**, Reg. (EU) 2023/2405](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R2405#art_14) | Requires operators to pay a charge to EASA for label issuance |
| [**§ 14 (12)**, Reg. (EU) 2023/2405](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R2405#art_14) | Mandates Commission review by 1 July 2027 to assess a mandatory label scheme |

## Regulation Texts

The following extracts provide the legal foundation for the Flight Emissions Label (FEL). They are quoted directly from EU law with context for application within JetFuelBurn.

### § 14 — Establishment of the Flight Emissions Label

> (1) “A voluntary environmental labelling scheme enabling the environmental performance of flights to be measured is hereby established.”  
>  
> (2) “Labels issued pursuant to this Article shall apply to aircraft operators falling within the scope of this Regulation for flights covered by this Regulation departing from Union airports. Where an aircraft operator requests the issuance of a label under this Article, it shall request such a label for all its flights covered by this Regulation departing from Union airports.”  
>  
> “Aircraft operators may request the issuance of labels under this Article also for their flights covered by this Regulation arriving at Union airports. Where an aircraft operator requests the issuance of a label under this subparagraph, it shall request such a label for all its flights arriving at Union airports.” (...)
>  
> (9) “In order to finance the costs of the service provided by the Agency, the issuing of a label at the request of an aircraft operator shall be subject to the payment of a charge … The amount of the charge shall be defined pursuant to Article 126(4) of Regulation (EU) 2018/1139.” (...) 
>  
> (12) “By 1 July 2027, the Commission shall identify and assess … with a view in particular to establish a compulsory environmental labelling scheme … The Commission shall present a report … to the European Parliament and to the Council.”  
>
> — [*§ 14 (1)–(2), (9), (12) Reg. (EU) 2023/2405 (ReFuelEU Aviation), OJ L 2023/2405, 31 Oct 2023.*](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R2405#art_14)


### Annex II — Flight Emissions Calculation Methodology

> (Preamble) “This Annex lays down the methodology and the necessary steps that the Agency shall follow for the estimation of flight emissions.”  
>  
> § 1 Abs. 1 “Flight emissions shall be calculated by multiplying the estimated consumption of aviation fuels … by the weighted average of lifecycle emissions of the aviation fuels uplifted at the departure airport. At the same time, flight emissions are equal to the sum of cabin and freight emissions.”  (...)
>  
> § 1 Abs. 3 lit. b) “If primary data for the scheduled flights does not exist, is insufficient, cannot be verified or exists only for operating conditions significantly differing from those reported, the estimated aviation fuels consumption shall be calculated by approximation using the Breguet-Range equation.” (...)
>  
> § 2 Abs. 1 “Flight emissions shall be attributed to the cabin and to freight on the basis of the respective apportionment of cabin and freight mass.”  
>
— [*Annex II § 1 Abs. 1, § 1 Abs. 3 lit. b), § 2 Abs. 1 Implementing Reg. (EU) 2024/3170, OJ L 2024/3170, 12 Nov 2024.*](https://eur-lex.europa.eu/eli/reg_impl/2024/3170/oj/eng#anx_II)

!!! reference "See Also"
    - [EASA Flight Emissions Portal](https://www.flightemissions.eu/en)  
    - [Commission Implementing Regulation (EU) 2024/3170](https://eur-lex.europa.eu/eli/reg_impl/2024/3170/oj/eng)  
    - [ReFuelEU Aviation Regulation (EU) 2023/2405](https://eur-lex.europa.eu/eli/reg/2023/2405/oj/eng)

!!! note "Integration with Google’s Travel Impact Model"
    The Travel Impact Model (TIM) integrates the EU Flight Emissions Label (FEL) through its distribution network, ensuring interoperability between the two methodologies. For flights with FEL data issued by EASA, these verified values replace TIM estimates and are clearly marked as “EASA” to indicate the source. For more information, see the [Flight Emissions Label section of the Travel Impact Model documentation](https://github.com/google/travel-impact-model?tab=readme-ov-file#flight-emissions-label).