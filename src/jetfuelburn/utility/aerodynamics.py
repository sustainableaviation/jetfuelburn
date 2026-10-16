# %%
import csv
import math
from importlib import resources
from typing import Callable
import functools
from jetfuelburn.utility.physics import (
    _calculate_dynamic_pressure,
    _calculate_airspeed_from_mach,
    _calculate_atmospheric_density,
    _calculate_dynamic_viscosity,
)
import pint
from jetfuelburn import ureg


class poll_schumann_drag_polars:
    r"""
    The class implements the clean-configuration drag polar of Poll & Schumann (2025)
    for 67 civil transport aircraft, including the effects of Reynolds number and compressibility.

    ```python exec="true" html="true"
    from jetfuelburn.figures.aerodynamics import figure_poll_schumann_dragpolar
    fig = figure_poll_schumann_dragpolar()
    print(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    # https://pawamoy.github.io/markdown-exec/gallery/#with-plotly
    ```
    _Lift-to-drag ratio of an A320 at 58,800 kg over the drag coefficient, for five Mach numbers
    (altitude varies along each curve). Compare Fig. 3 in Poll & Schumann (2025)._

    The drag coefficient is the sum of a low-speed parabolic polar and a wave drag term:

    \begin{align*}
    C_D &= C_{D0} + K \cdot C_L^2 + C_{D,w} \\
    C_{D0} &= \psi_0 \cdot \frac{0.0269}{(R^{ac})^{0.14}} \\
    K &= \frac{1}{\pi \cdot A \cdot e_{LS}} \\
    e_{LS} &= \frac{1}{1.03 + \delta_2 + \pi \cdot A \cdot k_1}
    \end{align*}

    with $A = s^2/S_{ref}$, $\delta_2 = 2 (b_f/s)^2$ and $k_1 = 0.80 (1 - 0.53 \cos\Lambda) \cdot C_{D0}$.
    The Reynolds number $R^{ac} = \sqrt{S_{ref}} \cdot \rho \cdot a \cdot M / \mu$ is evaluated at the flight condition.
    The wave drag $C_{D,w}$ depends on the Mach number and the lift coefficient (Eqs. 39-44 in the paper).

    | Symbol      | Dimension       | Description                                     |
    |-------------|-----------------|-------------------------------------------------|
    | $C_{D0}$    | [dimensionless] | Zero-lift drag coefficient                      |
    | $K$         | [dimensionless] | Induced drag factor                             |
    | $C_{D,w}$   | [dimensionless] | Wave drag coefficient                           |
    | $\psi_0$    | [dimensionless] | Zero-lift drag parameter (Table 2)              |
    | $R^{ac}$    | [dimensionless] | Reynolds number based on $\sqrt{S_{ref}}$       |
    | $A$         | [dimensionless] | Wing aspect ratio                               |
    | $s$         | [length]        | Wing span (Table 2)                             |
    | $S_{ref}$   | [area]          | Wing reference area (Table 2)                   |
    | $b_f$       | [length]        | Fuselage width (Table 2)                        |
    | $\Lambda$   | [angle]         | Wing quarter-chord sweep (Table 2)              |
    | $e_{LS}$    | [dimensionless] | Low-speed span efficiency factor                |

    Notes
    -----
    Two details follow the authors' own model rather than the printed equations of Part 3:

    - The drag-rise term $40 (X - X_{DO})^4$ of Eq. (44) is added outside the $\cos^3\Lambda$ factor.
      This reproduces Fig. 3 of the paper.
    - For the 14 types fitted with winglets or sharklets, $e_{LS}$ is multiplied by 1.075
      (Poll & Schumann 2021, Part 2, with the winglet flags of the pycontrails implementation of the model).

    The model describes the clean configuration (flaps and landing gear retracted).

    References
    ----------
    Poll, D. I. A., & Schumann, U. (2025).
    An estimation method for the fuel burn and other performance characteristics of civil transport aircraft;
    part 3 full flight profile when the trajectory is specified.
    _The Aeronautical Journal_, 129(1334), 825-861.
    doi:[10.1017/aer.2024.141](https://doi.org/10.1017/aer.2024.141)

    Licensing Note
    --------------
    Aircraft parameters from Table 2 of Poll & Schumann (2025), [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
    Full notice in [`NOTICE.md`](https://github.com/sustainableaviation/jetfuelburn/blob/main/NOTICE.md).
    """

    # Types fitted with winglets or sharklets (e_LS multiplied by 1.075).
    _WINGLETS = {
        "A20N", "A21N", "A35K", "B37M", "B38M", "B39M", "BCS1",
        "BCS3", "CRJ9", "E170", "E190", "E195", "E75L", "E75S",
    }  # fmt: skip
    _J3 = 40.0  # drag-rise constant of Eq. (44)

    _aircraft_data = {}
    with resources.open_text("jetfuelburn.data.PS2025", "table_2.csv") as file:
        for row in csv.DictReader(file):
            _aircraft_data[row["ICAO"]] = {
                "S": float(row["S_ref (m^2)"]),  # wing reference area [m²]
                "span": float(row["s (m)"]),  # wing span [m]
                "b_f": float(row["b_f (m)"]),  # fuselage width [m]
                "sweep": float(row["Lambda_w (deg)"]),  # quarter-chord sweep [deg]
                "psi_0": float(row["psi_0"]),
                "M_DO": float(row["M_DO"]),  # design-optimum Mach number
                "R_DO": float(row["(R^ac)_DO"]),  # design-optimum Reynolds number
                "CL_DO": float(row["(C_L)_DO"]),  # design-optimum lift coefficient
                "M_TF": float(row["(M_TF)^ac"]),  # aircraft technology factor
                "j_1": float(row["J_1"]),
                "j_2": float(row["J_2"]),
            }

    @staticmethod
    def list_aircraft() -> list[str]:
        r"""
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(poll_schumann_drag_polars._aircraft_data.keys())

    @staticmethod
    def _get_data(acft: str) -> dict:
        if acft not in poll_schumann_drag_polars._aircraft_data:
            raise ValueError(
                f"ICAO Aircraft Designator '{acft}' not found in model data."
            )
        return poll_schumann_drag_polars._aircraft_data[acft]

    @staticmethod
    def _calculate_reynolds_number(acft: str, M: float, h: pint.Quantity) -> float:
        # Eq. (34): R = sqrt(S_ref) * rho * a * M / mu
        S = poll_schumann_drag_polars._get_data(acft)["S"] * ureg("m^2")
        reynolds = (
            S**0.5
            * _calculate_atmospheric_density(h)
            * _calculate_airspeed_from_mach(M, h)
            / _calculate_dynamic_viscosity(h)
        )
        return reynolds.to("dimensionless").magnitude

    @staticmethod
    def _calculate_low_speed_polar(
        acft: str, reynolds: float
    ) -> tuple[float, float, float]:
        data = poll_schumann_drag_polars._get_data(acft)
        aspect_ratio = data["span"] ** 2 / data["S"]  # Eq. (31)
        CD0 = data["psi_0"] * 0.0269 / reynolds**0.14  # Eqs. (32), (33)
        delta_2 = 2 * (data["b_f"] / data["span"]) ** 2  # Eq. (36)
        k_1 = (
            0.80 * (1 - 0.53 * math.cos(math.radians(data["sweep"]))) * CD0
        )  # Eq. (37)
        e_LS = 1 / (1.03 + delta_2 + math.pi * aspect_ratio * k_1)  # Eq. (35)
        if acft in poll_schumann_drag_polars._WINGLETS:
            e_LS *= 1.075
        K = 1 / (math.pi * aspect_ratio * e_LS)  # Eq. (38)
        return CD0, K, e_LS

    @staticmethod
    def _calculate_wave_drag(acft: str, CL: float, M: float) -> float:
        data = poll_schumann_drag_polars._get_data(acft)
        cos_sweep = math.cos(math.radians(data["sweep"]))
        # Eqs. (40), (41) and (43)
        X = M * cos_sweep / (data["M_TF"] - 0.10 * CL / cos_sweep**2)
        X_DO = (
            data["M_DO"]
            * cos_sweep
            / (data["M_TF"] - 0.10 * data["CL_DO"] / cos_sweep**2)
        )
        if X <= data["j_2"]:
            return 0.0
        CD_wave = cos_sweep**3 * data["j_1"] * (X - data["j_2"]) ** 2  # Eq. (42)
        if X > X_DO:
            # Eq. (44), with the drag-rise term outside the cos^3 factor (reproduces Fig. 3 of the paper)
            CD_wave += poll_schumann_drag_polars._J3 * (X - X_DO) ** 4
        return CD_wave

    @staticmethod
    def get_basic_drag_parameters(
        acft: str,
        M: float | None = None,
        h: pint.Quantity | None = None,
    ) -> dict:
        r"""
        Returns the parameters of the low-speed parabolic drag polar $C_D = C_{D0} + K \cdot C_L^2$
        for a given aircraft.

        Without `M` and `h`, the parameters are evaluated at the design-optimum Reynolds number
        $(R^{ac})_{DO}$ of Table 2. With `M` and `h`, they are evaluated at the Reynolds number of that flight condition.

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator (e.g., 'A320', 'B738', etc.)
        M : float, optional
            Mach number
        h : pint.Quantity (length), optional
            Altitude

        Returns
        -------
        dict
            A dictionary of the form:

            | Key   | Type                   |  Description                                 |
            |-------|------------------------|----------------------------------------------|
            | `S`   | `pint.Quantity` [area] | Wing reference area in square meters [m²]    |
            | `CD0` | `float`                | Zero-lift drag coefficient (dimensionless)   |
            | `K`   | `float`                | Induced drag factor (dimensionless)          |
            | `e`   | `float`                | Low-speed span efficiency factor             |

        Raises
        ------
        ValueError
            If the ICAO Aircraft Designator is not found in the model data.

        Example
        -------
        ```pyodide install='jetfuelburn'
        from jetfuelburn.utility.aerodynamics import poll_schumann_drag_polars
        poll_schumann_drag_polars.get_basic_drag_parameters('A320')
        ```
        """
        data = poll_schumann_drag_polars._get_data(acft)
        if M is None or h is None:
            reynolds = data["R_DO"]
        else:
            reynolds = poll_schumann_drag_polars._calculate_reynolds_number(acft, M, h)
        CD0, K, e_LS = poll_schumann_drag_polars._calculate_low_speed_polar(
            acft, reynolds
        )
        return {"S": data["S"] * ureg("m^2"), "CD0": CD0, "K": K, "e": e_LS}

    @staticmethod
    @ureg.check(
        None,
        "[force]",  # lift
        "[]",  # Mach number
        "[length]",  # altitude
        None,
    )
    def calculate_drag(
        acft: str,
        L: pint.Quantity,
        M: float | pint.Quantity,
        h: pint.Quantity,
        compressibility: bool = True,
    ) -> pint.Quantity:
        r"""
        Calculates the drag force for a given aircraft, lift force, Mach number and altitude.

        Drag is calculated as:

        \begin{align*}
        D &= q \cdot S_{ref} \cdot C_D \\
        C_L &= \frac{L}{q \cdot S_{ref}}
        \end{align*}

        with $C_D$ as described in the class documentation.

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator (e.g., 'A320', 'B738', etc.)
        L : pint.Quantity (force)
            Lift force
        M : float (dimensionless)
            Mach number
        h : pint.Quantity (length)
            Altitude
        compressibility : bool, optional
            Includes the wave drag if `True` (default). With `False`, only the low-speed polar is used.

        Returns
        -------
        pint.Quantity (force)
            Drag force [N]

        Raises
        ------
        ValueError
            If the ICAO Aircraft Designator is not found in the model data.
        ValueError
            If the Mach number is less than or equal to zero.
        ValueError
            If the altitude is less than zero.
        ValueError
            If the lift force is less than or equal to zero.

        Example
        -------
        ```pyodide install='jetfuelburn'
        import jetfuelburn
        from jetfuelburn import ureg
        from jetfuelburn.utility.aerodynamics import poll_schumann_drag_polars
        poll_schumann_drag_polars.calculate_drag(
            acft='A320',
            L=60*ureg.metric_ton*ureg.gravity,
            M=0.78,
            h=35000*ureg.feet,
        )
        ```
        """
        data = poll_schumann_drag_polars._get_data(acft)
        if M <= 0:
            raise ValueError("Mach number must be greater than zero.")
        if h < 0 * ureg.meter:
            raise ValueError("Altitude must be greater than or equal to zero.")
        if L <= 0 * ureg.newton:
            raise ValueError("Lift force must be greater than zero.")
        M = float(ureg.Quantity(M).to("dimensionless").magnitude)

        S = data["S"] * ureg("m^2")
        q = _calculate_dynamic_pressure(
            speed=_calculate_airspeed_from_mach(M, h), altitude=h
        )
        CL = (L / (q * S)).to("dimensionless").magnitude
        reynolds = poll_schumann_drag_polars._calculate_reynolds_number(acft, M, h)
        CD0, K, _ = poll_schumann_drag_polars._calculate_low_speed_polar(acft, reynolds)
        CD = CD0 + K * CL**2  # Eq. (30)
        if compressibility:
            CD += poll_schumann_drag_polars._calculate_wave_drag(
                acft, CL, M
            )  # Eq. (39)
        return (q * S * CD).to("N")

    @staticmethod
    @ureg.check(
        None,
        "[force]",  # lift
        "[]",  # Mach number
        "[length]",  # altitude
        None,
    )
    def calculate_lift_to_drag(
        acft: str,
        L: pint.Quantity,
        M: float | pint.Quantity,
        h: pint.Quantity,
        compressibility: bool = True,
    ) -> pint.Quantity:
        r"""
        Given lift, Mach number, and altitude,
        calculates the lift-to-drag ratio for a specified aircraft.

        See Also
        --------
        - [`jetfuelburn.utility.aerodynamics.poll_schumann_drag_polars.calculate_drag`][]
        - [`jetfuelburn.utility.aerodynamics.poll_schumann_drag_polars.calculate_lift_to_drag_binder_function`][]

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator (e.g., 'A320', 'B738', etc.)
        L : pint.Quantity (force)
            Lift force
        M : float or pint.Quantity (dimensionless)
            Mach number
        h : pint.Quantity (length)
            Altitude
        compressibility : bool, optional
            Includes the wave drag if `True` (default).

        Returns
        -------
        pint.Quantity (dimensionless)
            Lift-to-drag ratio
        """
        drag = poll_schumann_drag_polars.calculate_drag(acft, L, M, h, compressibility)
        return (L / drag).to("dimensionless")  # Eq. (45)

    @staticmethod
    def calculate_lift_to_drag_binder_function(
        acft: str,
        L: pint.Quantity | None = None,
        M: float | pint.Quantity | None = None,
        h: pint.Quantity | None = None,
        compressibility: bool = True,
    ) -> Callable | pint.Quantity:
        r"""
        Serves as a binder for the `calculate_lift_to_drag` method.
        If parameters `L`, `M`, or `h` are omitted, returns a
        [Callable (partial)](https://docs.python.org/3/library/functools.html#functools.partial)
        with `acft` (and `compressibility`) pre-bound.
        If all arguments are provided, performs the calculation immediately.

        Notes
        -----
        This is useful for scenarios where you want to create a reusable function for a specific aircraft,
        and then call it with different flight conditions (lift, Mach number, altitude) without having
        to specify the aircraft each time. For example:

        ```pyodide install='jetfuelburn'
        from jetfuelburn import ureg
        from jetfuelburn.utility.aerodynamics import poll_schumann_drag_polars
        a320_lift_to_drag = poll_schumann_drag_polars.calculate_lift_to_drag_binder_function(acft='A320')
        a320_lift_to_drag(L=60*ureg.metric_ton*ureg.gravity, M=0.78, h=35000*ureg.feet)
        ```

        See Also
        --------
        [`jetfuelburn.utility.aerodynamics.poll_schumann_drag_polars.calculate_lift_to_drag`][]
        """
        if L is None or M is None or h is None:
            return functools.partial(
                poll_schumann_drag_polars.calculate_lift_to_drag,
                acft=acft,
                compressibility=compressibility,
            )
        return poll_schumann_drag_polars.calculate_lift_to_drag(
            acft, L, M, h, compressibility
        )


# Deprecated aliases of names replaced in jetfuelburn 4.0.0 (to be removed in 5.0.0).
# Accessing an old name raises a DeprecationWarning and returns the replacement.
from jetfuelburn.utility.code import (
    _add_deprecated_method_aliases,
    _deprecated_module_attribute,
)

_add_deprecated_method_aliases(
    poll_schumann_drag_polars, {"available_aircraft": "list_aircraft"}
)

_DRAG_POLAR_NOTE = (
    "The drag polars now come from Poll & Schumann (2025), so results differ, "
    "and aircraft are identified by ICAO designators."
)
_DEPRECATED = {
    "openap_drag_polars": (
        "poll_schumann_drag_polars",
        poll_schumann_drag_polars,
        _DRAG_POLAR_NOTE,
    ),
    "jsbsim_drag_polars": (
        "poll_schumann_drag_polars",
        poll_schumann_drag_polars,
        _DRAG_POLAR_NOTE,
    ),
}


def __getattr__(name):
    return _deprecated_module_attribute(__name__, name, _DEPRECATED)
