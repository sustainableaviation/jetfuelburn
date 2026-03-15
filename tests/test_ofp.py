import polars as pl
import math
from figures.ofp.ofp_climb_descent import generate_4d_trajectory

def test_generate_4d_trajectory_climb_and_level_off():
    # Setup test data based on the user prompt scenario
    df_ofp = pl.DataFrame({
        'waypoint': ['A', 'B', 'C'],
        'lat': [12.1, 12.4, 12.7],
        'lon': [2.2, 2.4, 2.6],
        'timeto': [10.0, None, 40.0],
        'altitude': [0.0, 20000.0, 20000.0]
    })
    
    perf_data = {
        "climb": [
            {"min_alt": 0, "max_alt": 10000, "rate": 800},
            {"min_alt": 10000, "max_alt": 20000, "rate": 500}
        ],
        "descent": [
            {"min_alt": 0, "max_alt": 10000, "rate": 1000},
            {"min_alt": 10000, "max_alt": 20000, "rate": 800}
        ]
    }
    
    # Calculate expected time to reach 20,000 ft from 0 ft:
    # 0 -> 10,000 @ 800 fpm = 10000/800 = 12.5 mins
    # 10,000 -> 20,000 @ 500 fpm = 10000/500 = 20.0 mins
    # Total time = 32.5 mins
    # Given waypoint A is at 10.0, waypoint B should be at 10.0 + 32.5 = 42.5
    # Wait, the prompt says waypoint B has timeto=NaN. 
    # Let's see how our code handles this. It should assign B's timeto to 42.5.
    # We also added waypoint C at timeto=40.0. If B is at 42.5, C is backwards in time, 
    # which invalidates the flight plan order.
    # Let's adjust waypoint C to timeto=50.0 to make it consistent.
    
    df_ofp = pl.DataFrame({
        'waypoint': ['A', 'B', 'C'],
        'lat': [12.1, 12.4, 12.7],
        'lon': [2.2, 2.4, 2.6],
        'timeto': [10.0, None, 50.0],
        'altitude': [0.0, 20000.0, 20000.0]
    })
    
    df_res = generate_4d_trajectory(df_ofp, perf_data, resolution_min=1.0)
    
    assert df_res.columns == ['timestamp', 'lat', 'lon', 'alt']
    
    # Check bounds
    assert df_res['timestamp'].min() == 10.0
    assert df_res['timestamp'].max() == 50.0
    
    # Check altitude at 10.0 + 12.5 = 22.5 mins (should be ~10000 ft, meaning at 22 min <10000 and 23 min >10000)
    # At 22 mins: t=12. 12 * 800 = 9600 ft.
    row_22 = df_res.filter(pl.col("timestamp") == 22.0)
    if len(row_22) > 0:
        assert math.isclose(row_22['alt'][0], 9600.0, rel_tol=1e-5)
        
    # Check altitude at 42.5 mins (should be 20000 ft exactly based on the simulated loop, or close to it)
    # Let's check when it reaches 20000.
    row_43 = df_res.filter(pl.col("timestamp") == 43.0)
    if len(row_43) > 0:
        assert math.isclose(row_43['alt'][0], 20000.0, rel_tol=1e-5)
        
    # It should level off at 20000 ft from ~42.5 mins to 50 mins
    level_off = df_res.filter(pl.col("timestamp") >= 43.0)
    assert (level_off['alt'] == 20000.0).all()

def test_generate_4d_trajectory_early_arrival():
    # If the aircraft climbs to the next altitude, but the target waypoint is MUCH further away in time, 
    # it must level off at that altitude until it reaches the waypoint.
    
    # Waypoint A: alt 0, time 0
    # Waypoint B: alt 10000, time 30
    # ROC is 1000. It will take 10 mins. So from t=10 to t=30, altitude must be 10000.
    
    df_ofp = pl.DataFrame({
        'waypoint': ['A', 'B'],
        'lat': [0.0, 1.0],
        'lon': [0.0, 1.0],
        'timeto': [0.0, 30.0],
        'altitude': [0.0, 10000.0]
    })
    
    perf_data = {
        "climb": [
            {"min_alt": 0, "max_alt": 20000, "rate": 1000}
        ]
    }
    
    df_res = generate_4d_trajectory(df_ofp, perf_data, resolution_min=1.0)
    
    # Check at t=10
    row_10 = df_res.filter(pl.col("timestamp") == 10.0)
    assert math.isclose(row_10['alt'][0], 10000.0, rel_tol=1e-5)
    
    # Check at t=20
    row_20 = df_res.filter(pl.col("timestamp") == 20.0)
    assert math.isclose(row_20['alt'][0], 10000.0, rel_tol=1e-5)
