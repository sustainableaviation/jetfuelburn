# New reduced-order fuel burn model candidates for jetfuelburn

The systematic review turned up **six genuinely new tier-i candidates** worth implementing, one **critical revision** to a prior assessment (CORSIA CERT is license-blocked, not a strong candidate), and a comprehensive tier-iii catalog. The reduced-order regression field is thinner than the target-author list suggests: once the exclusion list is applied, the surviving space is dominated by (a) simple hourly-fuel tables in the tourism/private-jet literature, (b) a handful of appendix-backed regression papers, and (c) foundational historical datasets. Post-2020 the field has shifted almost entirely toward deep neural networks whose weights are non-transcribable, and toward full trajectory pipelines that call BADA or Piano-X under license — both dead ends for a redistributable MIT package.

Below, tier-i recommendations are ranked by value-to-effort. A critical licensing finding on CORSIA CERT should be treated as a correction to prior scoping. Two policy-tier factor sets (DEFRA OGL, ADEME Licence Ouverte) are the cleanest new additions on the licensing axis but add only class-aggregated resolution.

## Prioritized tier-i shortlist (implementable in `reducedorder`)

### 1. Förster, Yildiz, Feuerle, Hecker (2022) — top pick

**Citation:** Förster, S.; Yildiz, K.; Feuerle, T.; Hecker, P. (2022). "Approach for Cost Functions for the Use in Trade-Off Investigations Assessing the Environmental Impact of Future Aircraft Concepts." *Aerospace* 9(3):167. DOI: 10.3390/aerospace9030167. **CC-BY 4.0 (MDPI).**

**Model form:** Closed-form regression of block fuel as a function of great-circle distance and seat load factor per aircraft type — with **explicit SLF dependence** in the regression, which distinguishes it from `seymour_etal`, `yanto_etal`, and `myclimate` (all of which fold load into constants). Also provides MRO cost and ANS-charge coefficients as bonus outputs.

**Coefficients:** Appendix B "Fuel Burn Coefficients" tabulates all fitted parameters. **9 aircraft types** representative of European traffic, plus a 10th all-electric short-range concept (SE²A). Directly transcribable.

**Provenance:** BADA-3 simulations over EUROCONTROL "so6" flight-plan waypoints under standard-atmosphere weather. Upstream is BADA (license-restricted), but the fitted regression coefficients are the authors' own derivative product under CC-BY — legally analogous to the `lee_etal` case already in the package.

**Adds:** European-focused, load-factor-parametrized alternative to Seymour/Yanto with a fully MIT-compatible license. Best-in-class effort-to-value on the shortlist.

### 2. Gössling, Humpe & Leitão (2024) — private-jet gap-filler

**Citation:** Gössling, S.; Humpe, A.; Leitão, J. (2024). "Private aviation is making a growing contribution to climate change." *Communications Earth & Environment* 5:666. DOI: 10.1038/s43247-024-01775-z. **CC-BY 4.0 (Nature).**

**Model form:** Simplest possible — `E_fuel = flight_hours × FF_hourly` per airframe, with `E_CO2 = E_fuel × 3.16`. Inputs: flight duration (or distance/typical cruise speed) and aircraft model.

**Coefficients:** Supplementary Information provides an **hourly fuel-consumption table (48–576 gph) for 72 business/private-jet models** — Gulfstream, Cessna Citation, Bombardier Global/Challenger, Dassault Falcon, Embraer Phenom/Legacy, Beechcraft King Air, Pilatus PC-12, etc. Verify by downloading the SI dataset.

**Provenance:** Aircraft-model fuel-consumption values from manufacturer/industry brochures (not operational data). ADS-B Exchange used for flight times in the paper's inventory application, but the fuel-per-hour table is provenance-independent.

**Adds:** **No existing package model covers business/private jets at this granularity.** OpenAP, Seymour, Yanto, Lee, AIM2015, EEA all focus on commercial airliners. This is a clean niche fill with the least implementation friction of any candidate — a Python dict of 72 (model → gph) pairs.

### 3. Turgut, Cavcar, Usanmaz et al. (2014) — cruise fuel-flow regression

**Citation:** Turgut, E.T.; Cavcar, M.; Usanmaz, O.; Canarslanlar, A.O.; Dogeroglu, T.; Armutlu, K.; Yay, O.D. (2014). "Fuel flow analysis for the cruise phase of commercial aircraft on domestic routes." *Aerospace Science and Technology* 37:1–9. DOI: 10.1016/j.ast.2014.04.012.

**Model form:** Multiple linear regression `FF_cruise = f(altitude, mass, TAS)` per aircraft type. Output = kg/h cruise fuel flow. Complements block-fuel models by exposing cruise-phase sensitivity to weight/altitude/speed.

**Coefficients:** Per-type regression sensitivities tabulated for **5 narrow-bodies: A319, A320, A321, B737-700, B737-800**. Derived from ~4,320 cruise observations of Turkish Airlines FDR data (January 2011). **User verification required:** confirm the article's tables provide the full regression equation (intercept + slopes) versus only marginal sensitivities. If sensitivities only, downgrade to tier ii.

**Provenance:** Proprietary FDR data (Turkish Airlines) — the fitted coefficients are publishable and transcribable, but the data is not re-fitable independently. Same legal posture as `lee_etal`.

**Caveats:** Cruise-only; pre-2015 (technically outside the primary 2015–2026 window but peer-reviewed and coefficient-published, matching the `lee_etal` era).

**Adds:** Cruise fuel-flow rate model — orthogonal to the block-fuel models already in the package.

### 4. Brueckner & Abreu (2020) — the sole BTS Form 41 candidate

**Citation:** Brueckner, J.K.; Abreu, C. (2020). "Airline fuel usage and carbon emissions: Determining factors" (disaggregated version). *Economics Letters* 197:109466. DOI: 10.1016/j.econlet.2020.109466. See also the airline-level 2017 predecessor: DOI 10.1016/j.jairtraman.2017.03.004.

**Model form:** Fuel_use = f(ATM, load factor, stage length, fleet vintage, fuel price, delays), fitted at the airline × aircraft-model level. Regression tables report fixed effects for ~10 popular narrow-body models plus wide-bodies.

**Coefficients:** Reported directly in the paper's regression tables.

**Provenance:** **US DOT BTS Form 41 + T-100 — fully public domain.** This is the only paper found that combines these open datasets with published per-model coefficients. **License-clean throughout.**

**Adds:** Annual/airline-level fuel estimator complementary to per-flight modules. Useful for macro fleet studies where per-flight granularity is unnecessary. **Verify** during implementation that model dummies and interaction coefficients are numerically reported (Economics Letters papers sometimes report only marginal effects, which would downgrade this to tier ii).

### 5. Loftin (1980), NASA RP-1060 — historical benchmark dataset

**Citation:** Loftin, L.K. Jr. (1980). *Subsonic Aircraft: Evolution and the Matching of Size to Performance*. NASA Reference Publication 1060, August 1980. NASA NTRS — US public domain.

**Model form:** Not a fuel-burn regression per se, but a **per-aircraft parametric table** across ~40 historical airliners: MTOW, OEW, W_fuel, R, cruise M, cruise altitude, W/S, T/W, AR. Serves as input to any Breguet-based fuel calculation and as a validation benchmark for pre-1980 fleet emissions studies.

**Provenance:** US public domain, fully transcribable.

**Caveat:** DC-3 to L-1011/747-200 era only — **no modern types (A320neo, 787, A350, MAX).** Value is historical benchmarking, not modern fleet estimation.

**Adds:** A dedicated historical-benchmark submodule; low ambiguity for the maintainer.

### 6. Sun, Hoekstra & Ellerbroek (2020) — drag-polar coefficients (tier i–ii)

**Citation:** Sun, J.; Hoekstra, J.M.; Ellerbroek, J. (2020). "Estimating aircraft drag polar using open flight surveillance data and a stochastic total energy model." *Transportation Research Part C* 114:391–404. DOI: 10.1016/j.trc.2020.01.026. Coefficients on **Figshare: doi.org/10.6084/m9.figshare.11424924**.

**Model form:** Quadratic drag polar `C_D = C_D0 + k·C_L²` for **20 aircraft types** (B737-3/4/7/8/900, A319/320/321, A332/333/343/346, B762/763/772/773/744, E190, CRJ9). Published as ADS-B-derived, no BADA dependence in the fit itself.

**Adds:** Not a stand-alone fuel model — needs an engine SFC (e.g., Poll–Schumann Part 3 tables) to convert drag → fuel. Recommend cataloging as an intermediate aerodynamic building block rather than a fuel module. Substantial overlap with OpenAP's drag database (same author). **Downgrade to tier ii/iii unless the package plans a drag-polar layer.**

## Borderline candidates (tier ii — need specific checks)

- **Cecen (2025)**, *Int. J. Aeronaut. Space Sci.* 26:2058–2069, DOI 10.1007/s42405-024-00860-z. OLS regression for CO₂ (R²=0.958) with mass, distance, aircraft type, flight regime. Paywalled; needs full-text retrieval to confirm coefficient tables are printed per aircraft × regime.
- **Zhang, Bian, Jiang, Wu (2025)**, *TR-E* 203:104339, DOI 10.1016/j.tre.2025.104339. Fourier + nonlinear fit for **11 modern Chinese-fleet types including B737 MAX 8 and A321-200** from ADS-B+ACARS. **This would be genuinely new coverage** (MAX/NEO family) if coefficients are printed rather than only described. High-priority full-text check.
- **Klenner et al. (2024)**, *ES&T*, DOI 10.1021/acs.est.3c08592. AviTeam pipeline with an **11-cluster aircraft-to-representative-type lookup (SI Table S1)**. Cluster lookup is tier i; distance→fuel curves require BADA execution. Inspect the ES&T supplement and the companion ERL 2024 paper (DOI 10.1088/1748-9326/ad3a7d) for any per-cluster distance-to-fuel curves.
- **DEFRA/DESNZ UK GHG conversion factors** (annual, current 2025). **OGL v3.0 — fully MIT-compatible.** Haul-band × cabin-class per-pax-km factors only (no per-aircraft resolution). Upstream derivation uses EUROCONTROL SET, but the published aggregate factors do not expose SET's structure — legally defensible for redistribution. Adds a policy-standard low-fidelity layer analogous to what no existing module provides.
- **ADEME Base Carbone aviation factors.** **Licence Ouverte v2.0 — MIT-compatible.** Per-seat-band × haul-distance factors. Upstream derivation traces to post-2009 EMEP/EEA methodology (flagged as restricted per task), but the aggregate ADEME outputs do not embed EEA copyrightable expression.
- **Filippone (2012), *Advanced Aircraft Flight Performance*, Appendix A.** Complete drag-polar + engine deck for a single reference aircraft (Gulfstream G-550). Tier ii only because it's one aircraft, not a fleet.
- **Jenkinson, Simpkin & Rhodes (1999) companion website.** Per-aircraft data tables for ~30 late-1990s civil jets (MTOW, OEW, cruise M, SFC, L/D). Vintage limits utility; transcription effort is non-trivial.
- **US EPA NEI aircraft LTO factors (Table 4-1, 2020 NEI).** US public domain; values derived from AEDT/BADA upstream. LTO-only; useful only for LTO/ground-ops decomposition.
- **Baklacioglu (2015/2016)** genetic-algorithm neural networks. Only one aircraft type (B737-800); polynomial fits are transcribable but of limited fleet value. DOIs 10.1017/S0001924000010393 and 10.1016/j.ast.2015.11.031.

## Critical licensing revision — CORSIA CERT is NOT a strong candidate

**The prior assessment of ICAO CORSIA CERT as a strong candidate should be revised.** The CERT 2023 Design/Development documentation does publish piecewise-linear coefficients (fuel = slope × GCD + intercept) for **116 aircraft types by ICAO designator**, calibrated on 6.3 million real flights from the CAEP WG4 Operations and Fuel database — technically the highest-quality per-aircraft dataset in existence, independent of BADA and Piano-X. **However, the ICAO CEM Use Agreement (icao.int/CORSIA/corsia-cem-2025) explicitly forbids** "creation of derivative works from the CEMs for use outside of the CORSIA framework, specifically including the creation of a database of aviation CO2 emissions." This precisely describes the intended `jetfuelburn` use case. **Treat CERT as tier-iii cite-only.** A runtime wrapper that calls the CERT tool remains permissible; embedding the coefficients does not.

**Related licensing findings:** ICCT reports (Graver/Kharina/Rutherford/Zheng) are **CC-BY-SA 4.0 — copyleft, incompatible with MIT** for bulk data incorporation, even setting aside their Piano-5 upstream. Cite in docs, do not embed. IATA RP 1726 is a passenger-CO2 allocation standard containing no fuel-burn coefficients (only cabin-class weights and the Jet A → CO2 factor of 3.16). atmosfair publishes methodology PDFs but no coefficient tables — the numbers live in Piano-X.

## Tier-iii catalog (for the `reducedorder_external` documentation page)

**Trajectory/inventory-tier institutional models:** ANCAT/EC2 (Gardner et al. 1998) publishes only gridded aggregates; AERO2k (Eyers et al. QINETIQ/04/01113, 2004) is under QinetiQ release restriction; FAST (Owen, Lee & Lim 2010, *ES&T* 44:2255) is an internal MMU/DLR wrapper on Piano-X; AEM (EUROCONTROL) is BADA-license-gated; NASA SAGE (Kim et al. FAA-EE-2005-01/02/03) describes methodology only, superseded by AEDT; AEDT 3g uses ANP + BADA 3/4 with public technical manuals but proprietary numerical data; Piano-X (Lissys Ltd) explicitly forbids redistribution of per-aircraft data; DLR-2 / FATE (Deidewig, Schmitt, Grewe, Schumann) publishes emission-index correlations but no per-aircraft fuel coefficients.

**Recent ADS-B / ML trajectory-tier work:** Filippone, Parkes, Bojdo & Kelly (2021, *Aeronaut. J.* 125:988, CC-BY-NC-ND) integrates FLIGHT over ADS-B tracks; Quadros, Snellen, Sun & Dedoussi (2022, *J. Aircraft* 59:1394) builds openAVEM on BADA 3.15; Krajček Nikolić et al. (2024, *Aerospace* 11:154) validates BADA against FDR; Jarry, Delahaye & Hurter (2024, ICRAT) and Jarry, Dalmau, Very & Sun (2025, *TR-C* 176:105143) train deep networks whose weights are non-transcribable; Sun, Ellerbroek & Hoekstra (2019, *TR-C* 98:118) WRAP provides kinematic (non-fuel) parametric distributions on GitHub; Chati & Balakrishnan (2018, TRR 2672:1) use Gaussian Process Regression with non-transcribable artefacts; Kang & Hansen (2021, *Transp. Sci.* 55:257) and Kang, Hansen & Ryerson (2018, *TR-C* 97:128) address contingency fuel with proprietary US-airline training data.

**Textbook methodologies (class-generic, no fleet coefficient table):** Roskam Part I (jet-transport phase fuel fractions Table 2.1); Raymer 6th ed. Table 6.2 (historical mission segment weight fractions); Torenbeek (1982, 2013) closed-form Küchemann-parameter cruise theory with class-average empirical constants; Howe (2000) modular closed-form propulsion/performance blocks with class-parametric coefficients; Corke (2003) duplicative of Roskam.

**Data sources rather than models:** ICAO Aircraft Engine Emissions Databank (EASA-hosted) — public per-engine LTO fuel flow at 4 thrust settings; input to BFFM2 but not a stand-alone fuel model. Airbus "Getting to Grips with Fuel Economy" (Issue 4, 2004) publishes per-family APU/single-engine-taxi fuel flows (A319/320/321 340 kg/h; A330 550–820 kg/h) — a tier-ii candidate for a ground-ops submodule only, since it contains no cruise per-seat-km data. Boeing publishes no equivalent per-aircraft cruise fuel factor document.

**Other calculator methodologies (cite only):** atmosfair (Piano-X upstream, no published coefficients); IATA CO2 Connect / RP 1726 (allocation-only, no fuel model); GREET aviation module (class-aggregated MJ/pkm for 6 pax + 4 freight classes; check GREET license terms); UBA/DLR tools (Piano-X/BADA upstream); Danish/Swedish EPA methodologies (wrappers on EMEP/EEA); STAC 2015 guide + DGAC TARMAAC (reference external databases rather than publishing their own tables); IPCC 2019 Refinement Vol. 2 Ch. 3 (aviation section marked "no refinement"; largely duplicates the EEA 2009 material already in the package).

## Explicit negative results (do not re-assess)

The following look candidate-worthy but fail implementability for the stated reason:

- **Filippone et al. (2021) *Aeronaut. J.* 125:988** — trajectory-tier (FLIGHT program), no closed-form; CC-BY-NC-ND (NC clause conflicts with MIT).
- **Pagoni & Psaraki-Kalouptsidi (2017) *TR-D* 54:172** — BADA-based clustering-and-registration on radar tracks; no per-aircraft coefficient table.
- **Jarry, Delahaye & Hurter (2024) ICRAT; Jarry, Dalmau, Very & Sun (2025) *TR-C* 176:105143** — deep neural network weights, thousands of parameters, non-transcribable.
- **Quadros et al. (2022) *J. Aircraft* 59:1394 (openAVEM)** — global inventory pipeline, no new coefficients; BADA 3.15 upstream.
- **Sun, Blom, Ellerbroek & Hoekstra (2019) *TR-C* 105:145** — particle-filter mass estimation, requires BADA at runtime.
- **Ryerson et al. (2015) *J. Aircraft* 10.2514/1.C033215** — only the linear model is transcribable, and only for 3 tail numbers (not types).
- **Chati & Balakrishnan (2018) TRR 2672:1 and 2016 ICAS** — GPR artefacts non-transcribable.
- **Kang & Hansen (2021), Kang, Hansen & Ryerson (2018)** — contingency-fuel and proprietary US-airline FBD.
- **Larsson et al. (2018) *EIA Review* 72:137** — country-level accounting, no per-aircraft.
- **Baumeister papers and Gössling & Humpe commercial-aviation overviews** — airline-level or aggregated intensity averages only.
- **Zhang, Huang, Liu & Zhang (2019) *Sustainability* 11:4362** — climb-phase-only physics optimization for 5 aircraft; coefficients embedded in optimization, not distance-parametric.
- **Peteilh et al. (2025) *J. Aircraft* 10.2514/1.C038362** — conceptual-design MTOM regressions under new propulsion, not per-type operational fuel.
- **Huang & Cheng (2022) *JATM* 99:102181** — CART + neural network, no transcribable coefficients.
- **ICCT reports (Graver 2019, Rutherford & Zeinali 2009, Kharina & Rutherford 2015, Graver/Rutherford/Zheng 2020, Zheng & Rutherford 2025)** — CC-BY-SA (copyleft) blocks MIT integration; Piano-5 upstream adds a second licensing concern.
- **CORSIA CERT / ICAO CEMs** — explicit Use Agreement forbids derivative databases; despite being the technically best-in-class per-aircraft dataset (116 types, 6.3M real flights).
- **IATA RP 1726** — allocation-only, no fuel model.
- **atmosfair** — Piano-X upstream, no coefficient publication.
- **AEDT** — BADA upstream, no published coefficient table.
- **UBA, Danish/Swedish EPA, STAC/TARMAAC** — wrappers on EEA/BADA/Piano-X, no independent coefficients.
- **IPCC 2019 Refinement aviation** — largely duplicates `eea_emission_inventory_2009` already in the package; "no refinement" statement in 2019.
- **Roskam, Raymer, Corke, Howe, Torenbeek** — class-generic fuel fractions and closed-form Breguet variants; no per-aircraft parameter set beyond what Lee & Chatterji already provides.

## Provenance-vs-license clarification

The Lee & Chatterji precedent — BADA-derived k-coefficients published in a peer-reviewed paper and thus legally transcribable — extends cleanly to several of the shortlisted candidates. Förster et al. (2022, CC-BY) fits regressions on BADA-3 outputs, but its published fitted coefficients are the authors' own derivative product and MIT-transcribable. Turgut et al. (2014) fits on proprietary Turkish Airlines FDR data, but the published sensitivities/coefficients are citable. Sun, Hoekstra & Ellerbroek (2020) fits directly on ADS-B (no BADA in the fit itself). Gössling, Humpe & Leitão (2024) and Brueckner & Abreu (2020) have no license-restricted upstream — the cleanest cases.

What is not defensible is redistribution of raw BADA files, Piano-X aircraft files, EUROCONTROL SET internals, post-2009 EMEP/EEA data files, or the CORSIA CEM database itself. The distinction between the underlying restricted source data and the published fitted coefficients derived from it is the same distinction the package already relies on for `lee_etal`.

## Conclusion — what to build next

The single highest-value implementation target is **Förster et al. (2022)** — it is CC-BY, has appendix-tabulated coefficients, adds explicit seat-load-factor dependence not present in existing modules, and mirrors the functional form of `seymour_etal` and `yanto_etal` closely enough that the developer effort is small. **Gössling, Humpe & Leitão (2024)** is the second-highest priority because it fills an entire niche (business/private jets) that no current module addresses, at minimal implementation cost. **Turgut et al. (2014)** and **Brueckner & Abreu (2020)** add orthogonal capabilities (cruise fuel-flow rate; airline-annual Form 41 fits) and should be pursued after full-text verification of the coefficient tables. **Loftin (1980)** is a low-controversy historical benchmark addition. **Sun et al. (2020)** drag polar is worth adopting only if a drag-polar layer is planned.

Beyond those, the field is closed either by license (CORSIA CERT, ICCT, Piano-X, BADA-gated tools, CC-BY-SA copyleft), by non-transcribable artefacts (neural-net weights across the entire post-2020 ML wave), or by duplication of models already in the package (IPCC 2019 aviation Tier 2 ≈ EEA 2009; Roskam/Raymer generics ≈ what Lee already generalizes). The DEFRA/ADEME policy-tier factor sets are worth a low-fidelity companion module chiefly because of their license cleanliness (OGL v3.0 and Licence Ouverte v2.0), not their granularity.
