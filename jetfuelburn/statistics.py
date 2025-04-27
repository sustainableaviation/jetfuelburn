# %%
import pint
ureg = pint.get_application_registry()
import json
from importlib import resources


class usdot():
    """
    This class contains methods to access statistical data on aircraft fuel consumption
    reported by "large certified air carriers" to the US Department of Transport (US DOT).

    Data is based on averages of fuel consumption per passenger mile and per ton mile,
    reported by the US DOT in table T2, summarizing Form 41 Schedule T-100.

    Terminology
    -----
    - **Form 41**
    
        Form 41 is a report that the U.S. Department of Transportation (DOT) generates
        based on data which large certified air carriers are required to provide.

        The _Financial Report_ part of this form includes balance sheet, cash flow, employment, income statement, fuel cost and consumption,
        aircraft operating expenses, and operating expenses.
        The _Air Carrier Statistics_ part of this form includes data on
        passengers, freight and mail transported.
        It also includes aircraft type, service class, available capacity and seats, and aircraft hours ramp-to-ramp and airborne.

        The reporting requirements of Schedule T-100 of Form 41 are defined in federal law: 

        | Reglation | Scope |
        | --------- | ----- |
        | [14 CFR 291.45](https://www.ecfr.gov/current/title-14/section-291.45) | General |
        | [Appendix A to Subpart E of Part 291, Title 14](https://www.ecfr.gov/current/title-14/part-291/appendix-Appendix%20A%20to%20Subpart%20E%20of%20Part%20291) | US Air Carriers |
        | [Appendix A to Part 217, Title 14](https://www.ecfr.gov/current/title-14/part-217/appendix-Appendix A to Part 217) | Foreign Air Carriers |

    - **Schedule** (in the context of Form 41)

        A schedule is a specific section of the Form 41 that contains
        a particular type of data:

        > "the Air Carrier Financial Reports (Form 41 Financial Data) (...)
        > Each table in this database contains a different type of financial report or “schedule” (...)"

        [Durso (2007) "An Introduction to DOT Form 41 web resources for airline financial analysis"](https://rosap.ntl.bts.gov/view/dot/16264/dot_16264_DS1.pdf)

    - Schedule **T100**

        > "Form 41 Schedule T-100(f) provides flight stage data covering both passenger/cargo
        > and all cargo operations in scheduled and nonscheduled services.
        > The schedule is used to report all flights which serve points in the United States
        > or its territories as defined in this part."

        [Appendix A to Part 217, Title 14](https://www.ecfr.gov/current/title-14/part-217/appendix-Appendix A to Part 217)
    
    - (table) **T2**

        > This table summarizes the T-100 traffic data reported by U.S. air carriers. The quarterly summary (...)

    - (table) **T1**

        > This table summarizes the T-100 traffic data reported by U.S. air carriers. The monthly summary (...)
        
    Warning
    -------
    Form 41 Schedule T-100 data can be downloaded from the US Department of Transportation website.
    Unfortunately, there are no permalinks to the data files, and even regular URLs are
    generated dynamically based on some JavaScript magic.
    
    The best way to obtain the correct files is to search by name, according to the following hierarchy:

    ```
    Database Name: Air Carrier Summary Data (Form 41 and 298C Summary Data)
    T2: U.S. Air Carrier TRAFFIC And Capacity Statistics by Aircraft Type
    ```

    On the `T2: (...)` page, click on the "Download" button in the "Data Tools" sidebar (left).
    The download should be an archive, containing the following file:

    ```
    T_SCHEDULE_T2.csv
    ```

    Aircraft types in this file are labeled using integer codes. These codes are
    defined in a separate file, which must also be downloaded.
    On the `T2: (...)` page, click on the `AircraftType` Field Name entry
    and on the following page, click on the "Download Lookup Table" button.

    See Also
    --------
    Working links to the relevant files (05-2025):
    
    - [US DOT: BTS: Air Carrier Summary Data (Form 41 and 298C Summary Data)](https://www.transtats.bts.gov/Tables.asp?QO_VQ=EGD&QO)
    - [US DOT: BTS: Air Carrier Summary Data: T2 (U.S. Air Carrier Traffic And Capacity Statistics by Aircraft Type)](https://www.transtats.bts.gov/Fields.asp?gnoyr_VQ=FIH)

    Example
    --------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn import ureg
    from jetfuelburn.statistics import usdot
    usdot.available_years()
    usdot.available_aircraft(userdot.available_years()[0])
    usdot.calculate_fuel_consumption_per_weight(
        year=2023,
        acft='B787-800 Dreamliner',
        R=1000 * ureg.nmi,
        W=1000 * ureg.kg
    )
    ```
    """

    _years = [2013, 2018, 2024]
    _aircraft_data = {}
    for year in _years:
        with resources.open_text("jetfuelburn.data.USDOT", f"USDOT_data_{year}.json") as file:
            _aircraft_data[year] = json.load(file)

    @staticmethod
    def available_years() -> list[int]:
        """
        Returns a sorted list of available years included in the model.
        """
        return sorted(usdot._years)
    @staticmethod
    def available_aircraft(year: int) -> list[str]:
        """
        Given a year, returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(usdot._aircraft_data[year].keys())
    
    @staticmethod
    @ureg.check(
        None,
        None,
        '[length]',
        '[mass]',
    )
    def calculate_fuel_consumption_per_weight(
        year: int,
        acft: str,
        R: float,
        W: float,
    ) -> dict:
        r"""
        Given an aircraft name, range and payload weight, calculates the fuel burned during flight.

        Data is based on averages of fuel consumption per weight-distance flown by specific aircraft types,
        in specific years, reported by "large certified air carriers" to the US Department of Transport (US DOT):

        $$
        f = \frac{F(t=\text{year})}{WD(t=\text{year})} * R * W
        $$

        where:

        | Symbol | Units   | Description                                                                 |
        | ------ | ------- | --------------------------------------------------------------------------- |
        | $f$    | [kg]    | Fuel burned during flight                                                   |
        | $F$    | [kg]    | Total fuel consumption for a specific aircraft type in a specific year      |
        | $WD$   | [kg*km] | Total weight-distance flown on a specific aircraft type in a specific year  |
        | $R$    | [km]    | Range of the flight                                                         |
        | $W$    | [kg]    | Payload weight of the flight                                                |

        Warnings
        --------
        Aircraft types here are given as full-length strings, e.g. "Boeing 737-800", instead of the ususal ICAO designator "B738".
        These are taken directly from the `L_AIRCRAFT_TYPE.csv` US DOT lookup table file.

        Parameters
        ----------
        year : int
            Year of the data to be used for the calculation.
        acft : str
            Aircraft type to be used for the calculation.
        R : pint.Quantity
            Range of the flight.
        W : pint.Quantity
            Payload weight of the flight.

        Returns
        -------
        pint.Quantity
            Fuel burned during flight.

        Raises
        ------
        ValueError
            If the range or weight is negative.  
            If the year is not available in the model.  
            If the aircraft type is not available in the model for the given year.
        """
        if R.magnitude < 0 or W.magnitude < 0:
            raise ValueError(f"Range and/or weight must not be negative.")
        else:
            R = R.to(ureg('km'))
            W = W.to(ureg('kg'))

        if year not in usdot._years:
            raise ValueError(f"No data available for year '{year}'.")
        if acft not in usdot._aircraft_data[year]:
            raise ValueError(f"US DOT Aircraft Designator '{acft}' not found in model data.")
        else:
            aircraft_data = usdot._aircraft_data[year][acft]

        fuelburn = (aircraft_data['Fuel/Revenue Weight Distance'] * ureg('1/km')) * R * W
        fuelburn = fuelburn.to(ureg('kg'))

        return fuelburn
    

    @staticmethod
    @ureg.check(
        None,
        None,
        '[length]',
    )
    def calculate_fuel_consumption_per_seat(
        year: int,
        acft: str,
        R: float,
    ) -> dict:
        r"""
        Given an aircraft name and range, calculates the fuel burned during flight per passenger.

        Data is based on averages of fuel consumption per passenger-distance flown by specific aircraft types,
        in specific years, reported by "large certified air carriers" to the US Department of Transport (US DOT):

        $$
        f = \frac{F(t=\text{year})}{paxD(t=\text{year})} * R
        $$

        where:

        | Symbol | Units   | Description                                                                   |
        | ------ | ------- | ----------------------------------------------------------------------------- |
        | $f$    | [kg]    | Fuel burned during flight                                                     |
        | $F$    | [kg]    | Total fuel consumption for a specific aircraft type in a specific year        |
        | $paxD$ | [kg*km] | Total passenger-distance flown on a specific aircraft type in a specific year |
        | $R$    | [km]    | Range of the flight                                                           |

        Warnings
        --------
        Aircraft types here are given as full-length strings, e.g. "Boeing 737-800", instead of the ususal ICAO designator "B738".
        These are taken directly from the `L_AIRCRAFT_TYPE.csv` US DOT lookup table file.

        Parameters
        ----------
        year : int
            Year of the data to be used for the calculation.
        acft : str
            Aircraft type to be used for the calculation.
        R : pint.Quantity
            Range of the flight.

        Returns
        -------
        pint.Quantity
            Fuel burned per passenger during flight.

        Raises
        ------
        ValueError
            If the range is negative.  
            If the year is not available in the model.  
            If the aircraft type is not available in the model for the given year.
        """
        if R.magnitude < 0:
            raise ValueError(f"Range must not be negative.")
        else:
            R = R.to(ureg('km'))

        if year not in usdot._years:
            raise ValueError(f"No data available for year '{year}'.")
        if acft not in usdot._aircraft_data[year]:
            raise ValueError(f"US DOT Aircraft Designator '{acft}' not found in model data.")
        else:
            aircraft_data = usdot._aircraft_data[year][acft]

        fuelburn = (aircraft_data['Fuel/Revenue Seat Distance'] * ureg('kg/km')) * R
        fuelburn = fuelburn.to(ureg('kg'))

        return fuelburn