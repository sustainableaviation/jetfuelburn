@ureg.check(
    None, # string
    '[length]',
    '[mass]',
)
def calculate_fuel_consumption_based_on_yanto_etal(
    acft: str,
    R: float,
    PL: float,
) -> ureg.Quantity:
    """
    Given an ICAO aircraft designator, mission range and payload mass, calculates the fuel burned.

    The calculation is based on a regression model built by Yanto and Liem (2017).
    The regression coefficients were obtained by fitting mission parameters to fuel burn data obtained
    from the Eurocontrol BADA flight trajectory simulation model and climb/descent fuel burn data.

    INCLUDES RESERVE ETC.?

    See Also
    --------
    - [Yanto and Liem (2017)](https://doi.org/10.2514/6.2017-3338)

    Parameters
    ----------
    R : float
        Mission range [length]
    PL : float
        Payload mass [mass]

    Returns
    -------
    float
        Fuel burned during flight [mass]
    """

    R = R.to('km').magnitude
    PL = PL.to('kg').magnitude

    dict_regression_coefficients = {
        'A319': {'c_R': 1.809, 'c_P': 0.145, 'c_C': 580.83},
        'A320': {'c_R': 1.984, 'c_P': 0.138, 'c_C': 390.97},
        'A332': {'c_R': 8.305, 'c_P': 0.341, 'c_C': -2314.39},
        'A333': {'c_R': 8.278, 'c_P': 0.329, 'c_C': 706.80},
        'B731': {'c_R': 2.085, 'c_P': 0.148, 'c_C': 125.44},
        'B733': {'c_R': 2.099, 'c_P': 0.146, 'c_C': 470.24},
        'B734': {'c_R': 2.412, 'c_P': 0.16, 'c_C': 431.29},
        'B735': {'c_R': 1.825, 'c_P': 0.117, 'c_C': 631.40},
        'B736': {'c_R': 1.922, 'c_P': 0.185, 'c_C': 517.48},
        'B737': {'c_R': 2.063, 'c_P': 0.165, 'c_C': 915.72},
        'B738': {'c_R': 2.539, 'c_P': 0.157, 'c_C': 484.68},
        'B739': {'c_R': 2.507, 'c_P': 0.172, 'c_C': 503.32},
        'B739ER': {'c_R': 2.547, 'c_P': 0.18, 'c_C': 328.96},
        'B752': {'c_R': 2.966, 'c_P': 0.168, 'c_C': 443.28},
        'B753': {'c_R': 3.242, 'c_P': 0.177, 'c_C': 762.16},
        'B772': {'c_R': 6.724, 'c_P': 0.396, 'c_C': -7634.59},
        'B773': {'c_R': 8.163, 'c_P': 0.371, 'c_C': -8576.72},
        'CRJ2': {'c_R': 1.045, 'c_P': 0.116, 'c_C': 140.42},
        'CRJ9': {'c_R': 1.271, 'c_P': 0.141, 'c_C': 778.27},
        'E145': {'c_R': 0.705, 'c_P': 0.134, 'c_C': 601.88},
        'MD80': {'c_R': 2.463, 'c_P': 0.152, 'c_C': -67.81},
        'A318': {'c_R': 1.407, 'c_P': 0.172, 'c_C': 17.29},
        'A321': {'c_R': 2.61, 'c_P': 0.176, 'c_C': 880.53},
        'A343': {'c_R': 8.81, 'c_P': 0.424, 'c_C': -5057.09},
        'A345': {'c_R': 10.86, 'c_P': 0.453, 'c_C': -9708.52},
        'A342': {'c_R': 8.36, 'c_P': 0.348, 'c_C': -290.49},
        'A346': {'c_R': 12.428, 'c_P': 0.385, 'c_C': -8552.62},
        'B742': {'c_R': 10.06, 'c_P': 0.403, 'c_C': -8964.48},
        'B744': {'c_R': 8.779, 'c_P': 0.247, 'c_C': -9191.53},
        'B762': {'c_R': 4.102, 'c_P': 0.228, 'c_C': 716.20},
        'B763': {'c_R': 5.159, 'c_P': 0.279, 'c_C': -2282.61},
        'CRJ7': {'c_R': 1.194, 'c_P': 0.143, 'c_C': 725.06},
        'CRJ1': {'c_R': 0.781, 'c_P': 0.169, 'c_C': 351.56},
        'E140': {'c_R': 0.673, 'c_P': 0.133, 'c_C': 633.03},
        'E170': {'c_R': 1.19, 'c_P': 0.144, 'c_C': 949.164},
        'E190': {'c_R': 1.626, 'c_P': 0.145, 'c_C': 1219.34},
        'MD90': {'c_R': 2.157, 'c_P': 0.117, 'c_C': 643.18}
    }

    if acft not in dict_regression_coefficients.keys():
        raise ValueError(f"ICAO Aircraft Designator '{acft}' not found in model data. Please select one of the following: {dict_regression_coefficients.keys()}")

    weight_fuel =  dict_regression_coefficients[acft]['c_R'] * R + dict_regression_coefficients[acft]['c_P'] * PL + dict_regression_coefficients[acft]['c_C']
    return weight_fuel * ureg('kg')
    

"""
@ureg.check(
    None, # string
    '[mass]',
    '[mass]',
    '[mass]',
    '[mass]',
    '[area]',
    '[]', # dimensionless
    '[]', # dimensionless
    '[length]',
    '[speed]',
    '[length]'
)
"""
def calculate_fuel_consumption_based_on_lee_etal(
    acft: str,
    W_E: float,
    W_MPLD: float,
    W_MTO: float,
    W_MF: float,
    S: float,
    C_D0: float,
    C_D2: float,
    c: float,
    h: float,
    V: float,
    d: float,
) -> tuple[ureg.Quantity, ureg.Quantity]:
    """_summary_

    _extended_summary_

    Parameters
    ----------
    acft : str
        _description_
    R : float
        _description_
    PL : float
        _description_
    alt_cruise : float
        _description_
    speed_cruise : float
        _description_

    See Also
    --------
    - [Lee and Chatterji (2010)](https://doi.org/10.2514/6.2010-9156)

    Returns
    -------
    ureg.Quantity
        _description_

    Raises
    ------
    ValueError
        If the ICAO aircraft designator is not found in the model data.
    """

    """
    -[Lee and Chatterji (2010)](https://doi.org/10.2514/6.2010-9156)
    """
    q = _calculate_dynamic_pressure(speed=V, altitude=h)
    q = q.to('N/m^2').magnitude
    c = c.magnitude
    S = S.to('m^2').magnitude
    W_E = W_E.magnitude
    W_MPLD = W_MPLD.magnitude
    W_MTO = W_MTO.magnitude
    W_MF = W_MF.magnitude
    d = d.to('m').magnitude
    h = h.to('m').magnitude
    V = V.to('m/s').magnitude

    dict_regression_coefficients = {
        "FA50": {'k_1': -18.2e-12, 'k_2': 3.11e-9, 'k_3': -163e-9, 'k_4': 2.46e-6, 'k_5': 47.1e-6, 'k_6': -0.823e-3},
        "E145": {'k_1': 17.3e-12, 'k_2': 4.72e-9, 'k_3': -286e-9, 'k_4': 0.0268e-6, 'k_5': 77.5e-6, 'k_6': -1.36e-3},
        "CRJ1": {'k_1': 9.74e-12, 'k_2': 1.11e-9, 'k_3': 133e-9, 'k_4': 1.07e-6, 'k_5': -70.4e-6, 'k_6': 8.14e-3},
        "A319": {'k_1': 20.7e-12, 'k_2': -1.07e-9, 'k_3': 107e-9, 'k_4': 1.10e-6, 'k_5': -46.3e-6, 'k_6': 5.91e-3},
        "A320": {'k_1': 29.4e-12, 'k_2': -2.63e-9, 'k_3': 64.2e-9, 'k_4': 1.40e-6, 'k_5': -22.5e-6, 'k_6': 3.74e-3},
        "A332": {'k_1': 30.6e-12, 'k_2': -2.85e-9, 'k_3': 70.0e-9, 'k_4': 1.31e-6, 'k_5': -21.5e-6, 'k_6': 3.29e-3},
        "B712": {'k_1': -31.4e-12, 'k_2': 4.62e-9, 'k_3': -238e-9, 'k_4': 0.552e-6, 'k_5': 68.6e-6, 'k_6': -3.34e-3},
        "B732": {'k_1': -42.7e-12, 'k_2': 5.64e-9, 'k_3': -310e-9, 'k_4': 0.929e-6, 'k_5': 91.2e-6, 'k_6': -4.61e-3},
        "B733": {'k_1': -23.7e-12, 'k_2': 3.96e-9, 'k_3': -248e-9, 'k_4': 0.680e-6, 'k_5': 75.5e-6, 'k_6': -4.53e-3},
        "B737": {'k_1': 38.9e-12, 'k_2': -3.37e-9, 'k_3': 130e-9, 'k_4': 1.48e-6, 'k_5': -43.6e-6, 'k_6': 5.81e-3},
        "B738": {'k_1': 31.1e-12, 'k_2': -2.75e-9, 'k_3': 115e-9, 'k_4': 1.47e-6, 'k_5': -40.3e-6, 'k_6': 5.12e-3},
        "B744": {'k_1': 8.45e-12, 'k_2': -0.816e-9, 'k_3': 44.4e-9, 'k_4': 1.03e-6, 'k_5': -15.7e-6, 'k_6': 1.60e-3},
        "B752": {'k_1': -20.2e-12, 'k_2': 4.28e-9, 'k_3': -264e-9, 'k_4': 0.447e-6, 'k_5': 78.4e-6, 'k_6': -5.40e-3},
        "B763": {'k_1': -35.6e-12, 'k_2': 5.67e-9, 'k_3': -279e-9, 'k_4': 0.180e-6, 'k_5': 86.3e-6, 'k_6': -5.04e-3},
        "B772": {'k_1': 21.9e-12, 'k_2': -2.84e-9, 'k_3': 65.0e-9, 'k_4': 1.38e-6, 'k_5': -17.1e-6, 'k_6': 2.56e-3},
        "MD82": {'k_1': -58.9e-12, 'k_2': 8.29e-9, 'k_3': -364e-9, 'k_4': 0.290e-6, 'k_5': 106e-6, 'k_6': -5.48e-3},
        "MD83": {'k_1': -30.0e-12, 'k_2': 4.55e-9, 'k_3': -289e-9, 'k_4': 0.802e-6, 'k_5': 87.5e-6, 'k_6': -5.64e-3},
        "JS31": {'k_1': 38.4e-12, 'k_2': -15.2e-9, 'k_3': -612e-9, 'k_4': 2.46e-6, 'k_5': 1.61e-6, 'k_6': -10.6e-3},
        "SF34": {'k_1': -59.8e-12, 'k_2': 7.70e-9, 'k_3': -374e-9, 'k_4': 1.98e-6, 'k_5': 58.7e-6, 'k_6': -2.98e-3},
        "E120": {'k_1': 25.7e-12, 'k_2': -1.40e-9, 'k_3': -353e-9, 'k_4': 1.01e-6, 'k_5': 82.5e-6, 'k_6': -4.55e-3},
        "AT45": {'k_1': 29.7e-12, 'k_2': -6.41e-9, 'k_3': -244e-9, 'k_4': 1.41e-6, 'k_5': 63.7e-6, 'k_6': -3.96e-3}
    }

    if acft not in dict_regression_coefficients.keys():
        raise ValueError(f"ICAO Aircraft Designator '{acft}' not found in model data. Please select one of the following: {dict_regression_coefficients.keys()}")

    f_res = 0.08 # cf. Section II D of Lee et al.
    f_man = 0.007 # cf. Section II D of Lee et al.
    f_inc = (
        dict_regression_coefficients[acft]['k_1'] * h ** 2 + 
        dict_regression_coefficients[acft]['k_2'] * h * V +
        dict_regression_coefficients[acft]['k_3'] * V ** 2 +
        dict_regression_coefficients[acft]['k_4'] * h +
        dict_regression_coefficients[acft]['k_5'] * V +
        dict_regression_coefficients[acft]['k_6']
    )

    A_1 = (1/(q*S)) * math.sqrt(C_D2/C_D0) # Eqn.(14) in Lee et al.
    A_2 = (c/V) * math.sqrt(C_D2*C_D0) # Eqn.(15) in Lee et al.
    A_d = math.tan(A_2 * d) # Eqn.(16) in Lee et al.
    A_3 = f_inc + f_man # Eqn.(18) in Lee et al.
    A_4 = 1 + f_res # Eqn.(19) in Lee et al.
    W_MZF = (-A_1 * A_3 * A_d * W_MTO ** 2 + (1 - A_3) * W_MTO - (A_d / A_1)) / (A_4 * (A_1 * A_d * W_MTO + 1)) # Eqn.(20) in Lee et al.

    if W_E + W_MPLD < W_MZF: # Figure 5(b) in Lee et al.
        W_PLD = W_MPLD # Figure 5(d) in Lee et al.
        W_ZF = W_E + W_PLD # Figure 5(d) in Lee et al.
        a = A_1 * A_3 * A_d
        b = (A_1 * A_4 * A_d * W_ZF + A_3 - 1)
        c = (A_4 * W_ZF + (A_d/A_1))
        W_TO = (-b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a) # Eqn.(17) in Lee et al.
        W_F = W_TO-W_PLD
    else:
        W_F = W_MTO - W_MZF # Figure 5(c) in Lee et al.
        if W_F < W_MF: # Figure 5(e) in Lee et al.
            W_PLD = W_MZF-W_E
        else: # Figure 5(e) in Lee et al.
            a = A_1 * A_d * (A_3 + A_4) # Eqn.(22) in Lee et al.
            b = 2 * A_1 * A_d * (A_3 + A_4) * W_E + A_1 * A_d * (2 * A_3 + A_4) * W_MF + A_3 + A_4 - 1 # Eqn.(23) in Lee et al.
            c = ( 
                A_1 * A_d * (A_3 + A_4) * W_E**2 + 
                A_1 * A_d * (2 * A_3 + A_4) * W_E * W_MF +
                A_1 * A_3 * A_d * W_MF**2 +
                (A_3 + A_4 - 1) * W_E +
                (A_3 - 1) * W_MF +
                (A_d / A_1)
            ) # Eqn.(24) in Lee et al.
            W_PLD = (-b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a) # Eqn.(21) in Lee et al.

    g = 9.8067 * (ureg.m / ureg.s ** 2)
    m_f = (W_F * ureg.N) / g
    m_pld = (W_PLD * ureg.N) / g
    return m_f.to('kg'), m_pld.to('kg')