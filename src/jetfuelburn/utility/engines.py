# %%
import pint
from jetfuelburn import ureg
from jetfuelburn.utility.physics import _calculate_atmospheric_temperature


@ureg.check(
    "[time]/[length]", "[]", "[]", "[length]", "[length]", None  # [mg/Ns] = s/m
)
def calculate_corrected_tsfc(
    tsfc_reported: pint.Quantity[float | int],
    M_reported: pint.Quantity[float | int],
    M_actual: pint.Quantity[float | int],
    h_reported: pint.Quantity[float | int],
    h_actual: pint.Quantity[float | int],
    beta: float | int | pint.Quantity[float | int],
) -> pint.Quantity[float | int]:
    r"""
    Given a reported thrust-specific fuel consumption (TSFC) at reference conditions,
    calculates the actual TSFC under different flight conditions according to an empirical correction formula
    proposed by Martinez-Val & Perez (1992) and used by Cavcar (2006).

    TSFC is calculated as:

    $$
    \text{TSFC}_{\text{actual}} = \text{TSFC}_{\text{reported}} \cdot \left( \frac{M_{\text{actual}}}{M_{\text{reported}}} \right)^{\beta} \cdot \sqrt{\frac{\Theta_{\text{actual}}}{\Theta_{\text{reported}}}}
    $$

    where:

    | Symbol                         | Dimension        | Description                                                                                                               |
    |--------------------------------|------------------|---------------------------------------------------------------------------------------------------------------------------|
    | $\text{TSFC}_{\text{actual}}$  | [time]/[length]  | The actual thrust-specific fuel consumption under the given conditions ($M_{\text{actual}}$, $h_{\text{actual}}$).        |
    | $\text{TSFC}_{\text{reported}}$| [time]/[length]  | The reported thrust-specific fuel consumption at the reference conditions ($M_{\text{reported}}$, $h_{\text{reported}}$). |
    | $M_{\text{actual}}$            | [dimensionless]  | The actual Mach number during the flight.                                                                                 |
    | $M_{\text{reported}}$          | [dimensionless]  | The Mach number at which the TSFC was reported.                                                                           |
    | $h_{\text{actual}}$            | [length]         | The actual altitude during the flight.                                                                                    |
    | $h_{\text{reported}}$          | [length]         | The altitude at which the TSFC was reported.                                                                              |
    | $\Theta_{\text{actual}}$       | [dimensionless]  | The actual atmospheric temperature ratio, calculated as $T_{\text{actual}} / T(h=0).                                      |
    | $\Theta_{\text{reported}}$     | [dimensionless]  | The reported atmospheric temperature ratio, calculated as $T_{\text{reported}} / T(h=0)$.                                 |
    | $\beta$                        | [dimensionless]  | An empirically derived exponent that captures how TSFC changes with Mach number.                                          |

    Notes
    -----
    Cavcar (2006) suggests for $\beta$:

    > 0.2–0.4 for low bypass turbofan engines and 0.4–0.7 for high bypass turbofan engines.
    - P.126 in Martinez-Val & Perez (1992)

    Warnings
    --------
    Trust-specific fuel consumption is a complex function of many parameters,
    and generally dependent on engine thrust as well as the Mach number:

    ![TSFC vs Thrust](../_static/tsfc.svg)

    The correction formula implemented in this function is a simplified empirical model
    which considers only variations in Mach number and atmospheric temperature, not thrust.

    See Also
    --------
    - [Thrust-Specific Fuel Consumption entry on Wikipedia](https://en.wikipedia.org/wiki/Thrust-specific_fuel_consumption)
    - Bensel, A. (2018). Characteristics of the Specific Fuel Consumption for Jet Engines. _Master's Thesis_. doi:[10.15488/4316](https://doi.org/10.15488/4316)

    References
    ----------
    - Eqn. 3 in Martinez-Val, R., & Perez, E. (1992).
    Optimum cruise lift coefficient in initial design of jet aircraft.
    _Journal of Aircraft_, 29(4), 712-714.
    doi:[10.2514/3.46226](https://doi.org/10.2514/3.46226)
    - Eqn. 2 in Cavcar, A. (2006).
    Constant altitude-constant Mach number cruise range of transport aircraft with compressibility effects.
    _Journal of Aircraft_, 43(1), 125-131.
    doi:[10.2514/1.14252](https://doi.org/10.2514/1.14252)

    Parameters
    ----------
    tsfc_reported: pint.Quantity[float | int]
        The reported thrust-specific fuel consumption at the reference conditions (e.g., from engine performance charts).
    h_reported: pint.Quantity[float | int]
        The altitude at which the TSFC was reported (e.g., from engine performance charts).
    M_reported: pint.Quantity[float | int]
        The Mach number at which the TSFC was reported (e.g., from engine performance charts).
    h_actual: pint.Quantity[float | int]
        The actual altitude during the flight for which we want to calculate the TSFC.
    M_actual: pint.Quantity[float | int]
        The actual Mach number during the flight for which we want to calculate the TSFC.
    beta: float | int | pint.Quantity[float | int]
        An empirically derived exponent that captures how TSFC changes with Mach number.

    Raises
    ------
    ValueError
        If any of the input parameters are non-positive, or if beta is non-positive.

    Returns
    -------
    pint.Quantity[float | int]
        The actual thrust-specific fuel consumption under the given flight conditions.

    Example
    -------
    Engine performance charts often report TSFC at specific conditions.
    Consider, for example, this excerpt from the JT15D-1 engine datasheet:

    ![Engine Datasheet](https://marien.sdsu.edu/Class_Materials/jt15d-engine.pdf){ type=application/pdf style="min-height:50vh;width:100%" }

    ```pyodide install='jetfuelburn'
    from jetfuelburn import ureg
    from jetfuelburn.utility.engines import calculate_corrected_tsfc
    calculate_corrected_tsfc(
        tsfc_reported=0.5 * ureg('lb/(lbf*hr)'),
        M_reported=0.85 * ureg.dimensionless,
        M_actual=0.78 * ureg.dimensionless,
        h_reported=35000 * ureg.ft,
        h_actual=30000 * ureg.ft,
        beta=0.5
    )
    ```
    """
    if tsfc_reported <= 0 * tsfc_reported.units:
        raise ValueError("tsfc_reported must be > 0")
    if M_reported <= 0 * M_reported.units:
        raise ValueError("M_reported must be > 0")
    if M_actual <= 0 * M_actual.units:
        raise ValueError("M_actual must be > 0")
    if h_reported < 0 * h_reported.units:
        raise ValueError("h_reported must be > 0")
    if h_actual < 0 * h_actual.units:
        raise ValueError("h_actual must be > 0")
    if isinstance(beta, pint.Quantity):
        beta = beta.to("dimensionless")
    if beta <= 0 * ureg.dimensionless:
        raise ValueError("beta must be > 0")

    t_reported_abs = _calculate_atmospheric_temperature(h_reported).to("kelvin")
    t_sea_level_abs = _calculate_atmospheric_temperature(0 * ureg.ft).to("kelvin")
    t_actual_abs = _calculate_atmospheric_temperature(h_actual).to("kelvin")

    relative_temperature_reported = (
        t_reported_abs / t_sea_level_abs
    )  # if not coverted to Kelvin, will raise "pint.errors.OffsetUnitCalculusError: Ambiguous operation with offset unit (degree_Celsius, degree_Celsius)"

    relative_temperature_actual = t_actual_abs / t_sea_level_abs
    tsfc_actual = (
        tsfc_reported
        * ((M_actual / M_reported) ** beta)
        * (relative_temperature_actual / relative_temperature_reported) ** 0.5
    )

    return tsfc_actual
