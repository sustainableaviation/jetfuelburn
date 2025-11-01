# EU Flight Emissions Label (FEL)

## Overview

The EU Flight Emissions Label (FEL) is a voluntary environmental labelling scheme established under Article 14 of Regulation (EU) 2023/2405 (ReFuelEU Aviation). It enables transparent, standardized disclosure of verified CO₂-equivalent emissions for commercial flights departing from or arriving at EU airports, covering all flights operated by participating airlines.

Once an operator becomes a label-holder, the FEL must be displayed for all flights in scope, ensuring consistent and non-selective reporting across its network.

The FEL is implemented by EASA through its Sustainability Portal and integrates verified operational data such as fuel burn, passenger load, and SAF share to generate per-flight emissions metrics. Participation is voluntary, but once an operator opts in, labels must cover every applicable flight included within the scheme's scope.

## Purpose

- Provide trusted, comparable flight-level CO₂ data to passengers  
- Support consumer transparency and counter greenwashing  
- Highlight verified operational performance (fuel burn + SAF usage)  
- Complement ReFuelEU Aviation sustainable-fuel obligations

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
| **Article 14**, Reg. (EU) 2023/2405 | Establishes voluntary Flight Emissions Label scheme |
| **Annex II**, Reg. (EU) 2024/3170 | Defines official methodology for calculating flight emissions |
| **Article 9 (1)** | Prohibits duplicate SAF claims across EU ETS, CORSIA and FEL |
| **Article 14 (9)** | Requires operators to pay a fee to EASA for label issuance |
| **Article 17 (7)** | Commission review by July 2027 to assess making FEL mandatory |

## Regulation Texts

The following extracts provide the legal foundation for the Flight Emissions Label (FEL). They are quoted directly from EU law with context for application within JetFuelBurn.

### Article 14 — Establishment of the Flight Emissions Label
> **Regulation (EU) 2023/2405 — ReFuelEU Aviation**  
> [📘 Full text on EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32023R2405#art_14)

*Article 14 formally establishes the voluntary Flight Emissions Label scheme and designates EASA as its administrator.*

!!! quote "Article 14 – Voluntary Environmental Labelling Scheme"
    > “A voluntary environmental labelling scheme enabling the environmental performance of flights to be measured is hereby established.”  
    >  
    > “Labels issued pursuant to this Article shall apply to aircraft operators falling within the scope of this Regulation for flights covered by this Regulation departing from Union airports. Where an aircraft operator requests the issuance of a label under this Article, it shall request such a label for all its flights covered by this Regulation departing from Union airports.”  
    >  
    > “Aircraft operators may request the issuance of labels under this Article also for their flights covered by this Regulation arriving at Union airports. Where an aircraft operator requests the issuance of a label under this subparagraph, it shall request such a label for all its flights arriving at Union airports.”

??? info "Summary and Relevance"
    - Establishes the Flight Emissions Label (FEL) under the ReFuelEU Aviation framework  
    - Applies to flights departing from or arriving at EU airports  
    - Participation is voluntary but must cover *all flights in scope* once opted in  
    - EASA implements and verifies all labels under a unified EU methodology

### Annex II — Flight Emissions Calculation Methodology
> **Commission Implementing Regulation (EU) 2024/3170**  
> [📘 Full text on EUR-Lex](https://eur-lex.europa.eu/eli/reg_impl/2024/3170/oj/eng#anx_II)

*Annex II of the Implementing Regulation defines the detailed methodology and calculation steps that EASA must follow for estimating flight emissions under the FEL scheme.*

!!! quote "Annex II – Methodology for Estimating Flight Emissions"
    > “This Annex lays down the methodology and the necessary steps that the Agency shall follow for the estimation of flight emissions.”  
    >  
    > “Flight emissions shall be calculated by multiplying the estimated consumption of aviation fuels for the flight in question by the weighted average of lifecycle emissions of the aviation fuels uplifted at the departure airport. At the same time, flight emissions are equal to the sum of cabin and freight emissions.”  
    >  
    > “If primary data for the scheduled flights does not exist, is insufficient, cannot be verified or exists only for operating conditions significantly differing from those reported, the estimated aviation fuels consumption shall be calculated by approximation using the Breguet-Range equation.”  
    >  
    > “Flight emissions shall be attributed to the cabin and to freight on the basis of the respective apportionment of cabin and freight mass.”

??? info "Summary and Relevance"
    - Defines the scientific and procedural methodology for EASA’s FEL calculations  
    - Combines primary airline data with fallback Breguet-range estimations when needed  
    - Specifies allocation rules between cabin and freight, and subsequent breakdown by cabin class  
    - Serves as the quantitative foundation for all official FEL labels published by EASA

!!! reference "See Also"
    - [EASA Flight Emissions Portal](https://www.flightemissions.eu/en)  
    - [Commission Implementing Regulation (EU) 2024/3170](https://eur-lex.europa.eu/eli/reg_impl/2024/3170/oj/eng)  
    - [ReFuelEU Aviation Regulation (EU) 2023/2405](https://eur-lex.europa.eu/eli/reg/2023/2405/oj/eng)

!!! note "Integration with Google’s Travel Impact Model"
    The **Travel Impact Model (TIM)** integrates the **EU Flight Emissions Label (FEL)** through its distribution network, ensuring interoperability between the two methodologies. For flights with FEL data issued by EASA, these verified values **replace TIM estimates** and are clearly marked as “EASA” to indicate the source. For more information, see the [Flight Emissions Label section of the Travel Impact Model documentation](https://github.com/google/travel-impact-model?tab=readme-ov-file#flight-emissions-label).