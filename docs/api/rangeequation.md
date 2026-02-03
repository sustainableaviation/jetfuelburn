!!! info

    The relation describing the specific air range of an aircraft in cruise can be adapted to 
    calculate the fuel required for a given range $R$. The governing equation for the range is:

    $$
    R = \frac{1}{g} \int_{m_2}^{m_1} \frac{V\cdot L/D}{TSFC \cdot m} \text{d}m
    $$

    Depending on which variables are assumed constant during the flight, different analytical solutions 
    to the integral can be derived:

    | Variables assumed Constant | Variables allowed to Vary | Solution                                                              | Function |
    |----------------------------|---------------------------|-----------------------------------------------------------------------|----------|
    | $TSFC, L/D, V$             | $m$                       | "Breguet range equation" or "climb-cruise flight schedule"            | [`jetfuelburn.rangeequation.calculate_fuel_consumption_breguet`][] <br> [`jetfuelburn.rangeequation.calculate_fuel_consumption_breguet_improved`][] |
    | $TSFC, h, V$               | $m, L/D$                  | "arctan solution" or "constant altitude and airspeed flight schedule" | N/A     |

    Section 13.2 in Young, T. M. (2018).
    Performance of the Jet Transport Airplane (Section 13.7.3 "Fuel Required for Specified Range"). 
    _John Wiley & Sons_. doi:[10.1002/9781118534786](https://doi.org/10.1002/9781118534786)


::: jetfuelburn.rangeequation