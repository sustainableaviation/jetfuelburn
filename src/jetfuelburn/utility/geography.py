# %%
import csv
import gzip
from importlib.resources import files
import math

from pyparsing import Optional
from jetfuelburn import ureg


class AirportAtlas:
    r"""
    Singleton-style class to manage airport data loading and lookups.
    Lazy-loads the dataset on the first request and indexes it by
    IATA code, ICAO code, and Name simultaneously to avoid repeated file I/O.
    """
    def __init__(self):
        self._loaded = False
        self._iata_index: dict[str, dict] = {}
        self._icao_index: dict[str, dict] = {}
        self._name_index: dict[str, dict] = {}

    def _load_data(self):
        """Loads the GZIP data into memory and builds indices."""
        if self._loaded:
            return

        path = files("jetfuelburn.data.Airports").joinpath("airports.csv.gz")
        
        with path.open('rb') as binary_file:
            with gzip.open(binary_file, mode='rt', encoding='utf-8') as text_file:
                reader = csv.DictReader(text_file)
                
                for row in reader:
                    try:
                        row['latitude'] = float(row['latitude'])
                        row['longitude'] = float(row['longitude'])
                    except (ValueError, KeyError):
                        continue # Skip invalid rows

                    if iata := row.get('iata'):
                        self._iata_index[iata] = row
                    
                    if icao := row.get('icao'):
                        self._icao_index[icao] = row
                        
                    if name := row.get('airport'):
                        self._name_index[name] = row
        
        self._loaded = True


    def get_airport(self, identifier: str, by: str = 'iata') -> dict:
        r"""Retrieves airport data by the specified identifier."""
        if not self._loaded:
            self._load_data()

        if by == 'iata':
            return self._iata_index.get(identifier)
        elif by == 'icao':
            return self._icao_index.get(identifier)
        elif by == 'name':
            return self._name_index.get(identifier)
        else:
            raise ValueError(f"Invalid identifier type: '{by}'. Must be 'iata', 'icao', or 'name'.")


_atlas = AirportAtlas()


def _get_airports_dict(by: str) -> dict:
    r"""
    Returns a dictionary of global airports and coordinates keyed by the specified field.

    See Also
    --------
    [`ip2location-iata-icao`](https://github.com/ip2location/ip2location-iata-icao) list of airport codes, names and coordinates on GitHub.

    Parameters
    ----------
    by : str
        The field to key the dictionary by. Must be one of:
        
        `icao`: International Civil Aviation Organization code  
        `iata`: International Air Transport Association code  
        `name`: Full airport name

    Returns
    -------
    dict
        A dictionary of airports keyed by the specified field. Structure depends
        on the `by` parameter. For example, if ``by='name'``:

        ```python
            {
                'Al Ain International Airport': {
                    'iata': 'AAN',
                    'icao': 'OMAL',
                    'latitude': 24.2617,
                    'longitude': 55.6092
                },
                ...
            }
        ```

    Raises
    ------
    ValueError
        If the ``by`` parameter is not one of ``'icao'``, ``'iata'``, or ``'name'``.
    
    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn.utility.geography import _get_airports_dict
    _get_airports_dict(by='iata').get('JFK')
    ```
    """
    header_map = {
        'icao': 'icao',
        'iata': 'iata',
        'name': 'airport' 
    }
    
    if by not in header_map:
        raise ValueError(f"Invalid key: '{by}'. Must be one of {list(header_map.keys())}")
    
    target_column = header_map[by]
    
    path = files("jetfuelburn.data.Airports").joinpath("airports.csv.gz")
    
    with path.open('rb') as binary_file:
        with gzip.open(binary_file, mode='rt', encoding='utf-8') as text_file:
            reader = csv.DictReader(text_file)
            
            airports = {}
            for row in reader:
                # 3. Extract the key (and remove it from the row)
                key_value = row.pop(target_column, "").strip()
                
                # If the chosen key is missing (e.g. airport has no IATA), skip it.
                if not key_value:
                    continue
                
                try:
                    row['latitude'] = float(row['latitude'])
                    row['longitude'] = float(row['longitude'])
                except ValueError:
                    pass
                
                airports[key_value] = row
                
            return airports


def _calculate_haversine_distance(lat1, lon1, lat2, lon2):
    r"""
    Calculates the Great Circle distance between two points 
    on the earth (specified in decimal degrees).

    \begin{align*}
    a &= \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos \phi_1 \cdot \cos \phi_2 \cdot \sin^2\left(\frac{\Delta\lambda}{2}\right) \\
    c &= 2 \cdot \operatorname{atan2}\left(\sqrt{a}, \sqrt{1-a}\right) \\
    d &= R \cdot c
    \end{align*}

    where:

    | Symbol                        | Description                                      |
    |-------------------------------|--------------------------------------------------|
    | $\phi$, $\lambda$             | Latitude and Longitude                           |
    | $\Delta\phi$, $\Delta\lambda$ | Difference in latitude and longitude (in radians)|
    | $R$                           | Mean earth radius (approx. 6,371 km)             |

    See Also
    --------
    [Haversine formula](https://en.wikipedia.org/wiki/Haversine_formula)  
    [Great-circle distance](https://en.wikipedia.org/wiki/Great-circle_distance)  
    [Earth radius](https://en.wikipedia.org/wiki/Earth_radius)

    Parameters
    ----------
    lat1 : float
        Latitude of point 1 in decimal degrees.
    lon1 : float
        Longitude of point 1 in decimal degrees.
    lat2 : float
        Latitude of point 2 in decimal degrees.
    lon2 : float
        Longitude of point 2 in decimal degrees.
    
    Returns
    -------
    Quantity
        The distance between the two points [length].

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn.utility.geography import _calculate_haversine_distance
    _calculate_haversine_distance(52.3086, 4.7639, 51.4700, -0.4543)
    ```
    """
    R = 6371.0 * ureg.km # Earth radius
    
    #  Decimal degrees to radians
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(d_lat / 2) ** 2) + \
    math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
    (math.sin(d_lon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def calculate_distance_between_airports(
    origin: str,
    destination: str,
    identifier: str = 'iata'
):
    r"""
    Calculates the Great Circle distance between two airports.

    ```python exec="true" html="true"
    import plotly.graph_objects as go

    # SYD: -33.9399, 151.1753
    # LHR: 51.4700, -0.4543
    lats = [-33.9399, 51.4700]
    lons = [151.1753, -0.4543]

    fig = go.Figure(data=go.Scattergeo(
        lat=lats,
        lon=lons,
        mode='lines+markers',
        line=dict(width=2, color='blue'),
        marker=dict(size=8, color='red'),
        text=['SYD', 'LHR'],
    ))

    fig.update_layout(
        height=500,
        margin={"r":0,"t":30,"l":0,"b":0},
        geo=dict(
            projection_type="natural earth",
            showland=True,
            landcolor="rgb(243, 243, 243)",
            countrycolor="rgb(204, 204, 204)",
        )
    )

    print(fig.to_html(full_html=False, include_plotlyjs="cdn"))
    ```
    _Great Circle route between Sydney (SYD) and London Heathrow (LHR).  
    On a mercator projection, the shortest path appears curved._

    Parameters
    ----------
    origin : str
        The origin airport code or name.
    destination : str
        The destination airport code or name.
    identifier : str, optional
        The type of airport identifier provided. Must be one of:
        
        `icao`: International Civil Aviation Organization code  
        `iata`: International Air Transport Association code  
        `name`: Full airport name  
        
        Default is `iata`.
    Returns
    -------
    Quantity
        The distance between the two airports as a `pint.Quantity` in kilometers.
    
    Raises
    ------
    ValueError
        If either airport code/name is not found.

    Example
    -------
    ```pyodide install='jetfuelburn'
    import jetfuelburn
    from jetfuelburn.utility.geography import calculate_distance_between_airports
    calculate_distance_between_airports('LOWI', 'LOWW', 'icao')
    ```
    """
    origin_info = _atlas.get_airport(origin, by=identifier)
    destination_info = _atlas.get_airport(destination, by=identifier)

    if not origin_info:
        raise ValueError(f"Origin airport '{origin}' not found using identifier '{identifier}'.")
    if not destination_info:
        raise ValueError(f"Destination airport '{destination}' not found using identifier '{identifier}'.")
    
    lat1 = origin_info['latitude']
    lon1 = origin_info['longitude']
    lat2 = destination_info['latitude']
    lon2 = destination_info['longitude']

    return _calculate_haversine_distance(lat1, lon1, lat2, lon2)