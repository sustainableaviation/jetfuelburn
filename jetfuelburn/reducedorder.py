import math
import pint
ureg = pint.get_application_registry() # https://pint-pandas.readthedocs.io/en/latest/user/common.html#using-a-shared-unit-registry


class fuel_burn_model_yanto_etal:
    """
    Reduced-order fuel burn model using the parameters __payload__ and __range__ proposed by Yanto and Liem (2017).
    
    In this model, fuel burn calculations are based on a regression model.
    The regression coefficients were obtained by fitting mission parameters to fuel burn data obtained
    from the Eurocontrol BADA flight trajectory simulation model and climb/descent fuel burn data.

    ![Payload/Range Diagram](https://raw.githubusercontent.com/sustainableaviation/jetfuelburn/refs/heads/main/docs/_static/reduced_order_yanto_etal.svg)
    Diagrammatic illustration of the reduced-order fuel burn model by Yanto and Liem (2017).
    Climb and descent segment fuel burn is calculated using the [EUROCONTROL BADA](https://www.eurocontrol.int/model/bada) model.
    Cruise segment fuel burn is calculated using the Breguet range equation.
    The multi-variate 


    

    References
    ----------
    Yanto, J., & Liem, R. P. (2017).
    Efficient fast approximation for aircraft fuel consumption for decision-making and policy analysis.
    In _AIAA Modeling and Simulation Technologies Conference_ (p. 3338).
    doi:[10.2514/6.2017-3338](https://doi.org/10.2514/6.2017-3338)

    """
    def __init__(self):
        self.dict_regression_coefficients = {
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


    def available_aircraft(self) -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        See also Table 5 in Yanto and Liem (2017).
        """
        return sorted(self.dict_regression_coefficients.keys())


    @ureg.check(
        None, # string
        '[length]',
        '[mass]',
    )
    def calculate_fuel_consumption(
        self,
        acft: str,
        R: float,
        PL: float,
    ) -> ureg.Quantity:
        """
        Given an ICAO aircraft designator, mission range and payload mass, calculates the fuel burned.

        Parameters
        ----------
        R : float
            Mission range [length]
        PL : float
            Payload mass [mass]

        Raises
        ------
        ValueError
            If the ICAO aircraft designator is not found in the model data.

        Returns
        -------
        float
            Fuel burned during flight [kg]
        """

        R = R.to('km').magnitude
        PL = PL.to('kg').magnitude

        if acft not in self.dict_regression_coefficients.keys():
            raise ValueError(f"ICAO Aircraft Designator '{acft}' not found in model data. Please select one of the following: {self.dict_regression_coefficients.keys()}")

        weight_fuel =  self.dict_regression_coefficients[acft]['c_R'] * R + self.dict_regression_coefficients[acft]['c_P'] * PL + self.dict_regression_coefficients[acft]['c_C']
        return weight_fuel * ureg('kg')
    


class fuel_burn_model_lee_etal:
    """
    Reduced-order fuel burn model based on Lee et al. (2010).

    ![Payload/Range Diagram](https://raw.githubusercontent.com/sustainableaviation/jetfuelburn/refs/heads/main/docs/_static/reduced_order_lee_etal.svg)
    
    In this model, fuel burn calculations are based on a regression model.
    The regression coefficients were obtained by fitting mission parameters to fuel burn data obtained
    from the Eurocontrol BADA flight trajectory simulation model and climb/descent fuel burn data.

    References
    ----------
    Lee, H. T., & Chatterji, G. (2010, September).
    Closed-form takeoff weight estimation model for air transportation simulation.
    In _10th AIAA Aviation Technology, Integration, and Operations (ATIO) Conference_ (p. 9156).
    doi:[10.2514/6.2010-9156](https://doi.org/10.2514/6.2010-9156)

    """
    def __init__(self):
        self.dict_regression_coefficients = {
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
        

    def available_aircraft(self) -> list[str]:
        """
        Returns a sorted list of available ICAO aircraft designators included in the model.
        """
        return sorted(self.dict_regression_coefficients.keys())


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

        if acft not in self.dict_regression_coefficients.keys():
            raise ValueError(f"ICAO Aircraft Designator '{acft}' not found in model data. Please select one of the following: {self.dict_regression_coefficients.keys()}")

        f_res = 0.08 # cf. Section II D of Lee et al.
        f_man = 0.007 # cf. Section II D of Lee et al.
        f_inc = (
            self.dict_regression_coefficients[acft]['k_1'] * h ** 2 + 
            self.dict_regression_coefficients[acft]['k_2'] * h * V +
            self.dict_regression_coefficients[acft]['k_3'] * V ** 2 +
            self.dict_regression_coefficients[acft]['k_4'] * h +
            self.dict_regression_coefficients[acft]['k_5'] * V +
            self.dict_regression_coefficients[acft]['k_6']
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
    

class fuel_burn_model_seymour_etal():
    """
    Reduced-order fuel burn model based on Seymour et al. (2020).

    ![Payload/Range Diagram](https://raw.githubusercontent.com/sustainableaviation/jetfuelburn/refs/heads/main/docs/_static/reduced_order_seymour_etal.svg)
    
    In this model, fuel burn calculations are based on a regression model.
    The regression coefficients were obtained by fitting mission parameters to fuel burn data obtained
    from the Eurocontrol BADA flight trajectory simulation model and climb/descent fuel burn data.

    References
    ----------
    Seymour, K., Held, M., Georges, G., & Boulouchos, K. (2020).
    Fuel Estimation in Air Transportation: Modeling global fuel consumption for commercial aviation.
    _Transportation Research Part D: Transport and Environment_, 88, 102528.
    doi:[10.1016/j.trd.2020.102528](https://doi.org/10.1016/j.trd.2020.102528)

    """

    def __init__(self):
        self.dict_regression_coefficients = {
            'A140': {'reduced_fuel_a1': 0.0001570270040569, 'reduced_fuel_a2': 1.2982777526024196, 'reduced_fuel_intercept': 160.62447178027185},
            'A148': {'reduced_fuel_a1': 6.398806910579147e-05, 'reduced_fuel_a2': 1.757267905324482, 'reduced_fuel_intercept': 971.0358232404124},
            'A158': {'reduced_fuel_a1': 3.3362854604312986e-05, 'reduced_fuel_a2': 2.566018863868268, 'reduced_fuel_intercept': 799.9393976678402},
            'A20N': {'reduced_fuel_a1': 5.668855923612881e-05, 'reduced_fuel_a2': 2.382220322790334, 'reduced_fuel_intercept': 955.9771828145858},
            'A21N': {'reduced_fuel_a1': 6.322240065870233e-05, 'reduced_fuel_a2': 2.7236585444593007, 'reduced_fuel_intercept': 1121.9381760390395},
            'A306': {'reduced_fuel_a1': 0.000208303528197, 'reduced_fuel_a2': 5.292754728665013, 'reduced_fuel_intercept': 2408.3891219198267},
            'A30B': {'reduced_fuel_a1': 0.0001982893815144, 'reduced_fuel_a2': 6.474756928487186, 'reduced_fuel_intercept': 2222.798735754448},
            'A310': {'reduced_fuel_a1': 0.0001632949648442, 'reduced_fuel_a2': 4.359746729125529, 'reduced_fuel_intercept': 2228.0275509617168},
            'A318': {'reduced_fuel_a1': 6.89511440921109e-05, 'reduced_fuel_a2': 2.350075246472605, 'reduced_fuel_intercept': 1118.9090916083037},
            'A319': {'reduced_fuel_a1': 7.861925591479135e-05, 'reduced_fuel_a2': 2.3082582355790655, 'reduced_fuel_intercept': 1194.0996838404626},
            'A320': {'reduced_fuel_a1': 0.000130042337441, 'reduced_fuel_a2': 2.4260951197123437, 'reduced_fuel_intercept': 1310.7950948662055},
            'A321': {'reduced_fuel_a1': -5.7378784219075385e-05, 'reduced_fuel_a2': 4.083572128715679, 'reduced_fuel_intercept': 1084.1337567410246},
            'A332': {'reduced_fuel_a1': 0.0001747859503353, 'reduced_fuel_a2': 4.9031762660658, 'reduced_fuel_intercept': 3603.0351976719103},
            'A333': {'reduced_fuel_a1': 2.6407166359376788e-05, 'reduced_fuel_a2': 6.517233690161649, 'reduced_fuel_intercept': 2090.642673369657},
            'A339': {'reduced_fuel_a1': 0.0001769854542406, 'reduced_fuel_a2': 4.634359445213642, 'reduced_fuel_intercept': 4057.6671819265466},
            'A342': {'reduced_fuel_a1': 0.0002358094393848, 'reduced_fuel_a2': 5.160351823288175, 'reduced_fuel_intercept': 4479.616294853418},
            'A343': {'reduced_fuel_a1': 0.0002672084309844, 'reduced_fuel_a2': 5.40202955241821, 'reduced_fuel_intercept': 3954.7379543269417},
            'A345': {'reduced_fuel_a1': 0.0002101950285755, 'reduced_fuel_a2': 6.852207692367797, 'reduced_fuel_intercept': 4919.303525652402},
            'A346': {'reduced_fuel_a1': 0.0002565271632093, 'reduced_fuel_a2': 6.86051702890215, 'reduced_fuel_intercept': 5501.48232695819},
            'A359': {'reduced_fuel_a1': 8.61825848810227e-05, 'reduced_fuel_a2': 6.152636361762516, 'reduced_fuel_intercept': 1753.6413158785144},
            'A35K': {'reduced_fuel_a1': 0.0001846395304374, 'reduced_fuel_a2': 5.378231075979626, 'reduced_fuel_intercept': 4413.229547197276},
            'A388': {'reduced_fuel_a1': 0.0002976350034167, 'reduced_fuel_a2': 11.402874182880453, 'reduced_fuel_intercept': 6408.219743091526},
            'AJ27': {'reduced_fuel_a1': 0.0001128545234347, 'reduced_fuel_a2': 2.220290803974472, 'reduced_fuel_intercept': 896.880801146056},
            'AN24': {'reduced_fuel_a1': 6.1540118558856e-05, 'reduced_fuel_a2': 1.5981588090902188, 'reduced_fuel_intercept': 212.2134235255014},
            'AN38': {'reduced_fuel_a1': 3.03583389380524e-05, 'reduced_fuel_a2': 1.50932767352588, 'reduced_fuel_intercept': 60.10635243403112},
            'AT43': {'reduced_fuel_a1': 0.000203974136543, 'reduced_fuel_a2': 0.7995587234644723, 'reduced_fuel_intercept': 198.85276266580055},
            'AT72': {'reduced_fuel_a1': 0.0002572904328121, 'reduced_fuel_a2': 1.1306414713636488, 'reduced_fuel_intercept': 203.17938444650304},
            'ATP': {'reduced_fuel_a1': 0.0003809166804082, 'reduced_fuel_a2': 1.084751679629892, 'reduced_fuel_intercept': 227.04070386623405},
            'B190': {'reduced_fuel_a1': 3.5682877519871425e-05, 'reduced_fuel_a2': 0.6990438903158286, 'reduced_fuel_intercept': 81.44129452835466},
            'B38M': {'reduced_fuel_a1': 4.240664668087035e-05, 'reduced_fuel_a2': 2.2729590234452277, 'reduced_fuel_intercept': 976.4669475643968},
            'B39M': {'reduced_fuel_a1': 5.4363062104823e-05, 'reduced_fuel_a2': 2.1640858440661783, 'reduced_fuel_intercept': 1134.7527808384184},
            'B461': {'reduced_fuel_a1': 0.0001896156534328, 'reduced_fuel_a2': 2.574807111911259, 'reduced_fuel_intercept': 1028.0273918223684},
            'B462': {'reduced_fuel_a1': 9.335585006686742e-05, 'reduced_fuel_a2': 2.7314117130301314, 'reduced_fuel_intercept': 1007.602964246164},
            'B463': {'reduced_fuel_a1': 0.0002324252599588, 'reduced_fuel_a2': 2.7270723090638445, 'reduced_fuel_intercept': 1091.4142853804456},
            'B712': {'reduced_fuel_a1': 9.5143139789311e-05, 'reduced_fuel_a2': 2.5586278585965525, 'reduced_fuel_intercept': 888.8985953393758},
            'B722': {'reduced_fuel_a1': 0.0002302031088632, 'reduced_fuel_a2': 4.938178279411521, 'reduced_fuel_intercept': 1867.430322671009},
            'B732': {'reduced_fuel_a1': 2.2603602200632625e-05, 'reduced_fuel_a2': 3.2972368428696255, 'reduced_fuel_intercept': 1136.061288362087},
            'B733': {'reduced_fuel_a1': -1.8591243748478092e-05, 'reduced_fuel_a2': 3.397847036676938, 'reduced_fuel_intercept': 783.8308256672553},
            'B734': {'reduced_fuel_a1': 0.000104184430457, 'reduced_fuel_a2': 3.2101738101978854, 'reduced_fuel_intercept': 1167.7732498010064},
            'B735': {'reduced_fuel_a1': 7.415187194803607e-05, 'reduced_fuel_a2': 2.644615749830163, 'reduced_fuel_intercept': 1144.5821378914425},
            'B736': {'reduced_fuel_a1': 5.9790833605521954e-05, 'reduced_fuel_a2': 2.3907264907192607, 'reduced_fuel_intercept': 1141.073186805245},
            'B737': {'reduced_fuel_a1': 8.453820942255774e-05, 'reduced_fuel_a2': 2.491056389417562, 'reduced_fuel_intercept': 1254.8001814325753},
            'B738': {'reduced_fuel_a1': 7.378617475106708e-05, 'reduced_fuel_a2': 2.920849872328848, 'reduced_fuel_intercept': 1218.8211966548952},
            'B739': {'reduced_fuel_a1': 5.865901988277855e-05, 'reduced_fuel_a2': 3.08055767111119, 'reduced_fuel_intercept': 1193.9582841250576},
            'B744': {'reduced_fuel_a1': 0.0003298404730252, 'reduced_fuel_a2': 8.335664382081461, 'reduced_fuel_intercept': 5173.3875295867765},
            'B748': {'reduced_fuel_a1': 0.0002615950218363, 'reduced_fuel_a2': 7.162095963451604, 'reduced_fuel_intercept': 6199.102376527022},
            'B752': {'reduced_fuel_a1': 0.0001250041873004, 'reduced_fuel_a2': 3.647634675096872, 'reduced_fuel_intercept': 1815.4045757940405},
            'B753': {'reduced_fuel_a1': 0.0001342318330896, 'reduced_fuel_a2': 4.317066583350788, 'reduced_fuel_intercept': 1813.2095734231495},
            'B762': {'reduced_fuel_a1': 0.0001583633647879, 'reduced_fuel_a2': 4.430972686802388, 'reduced_fuel_intercept': 2153.699352414358},
            'B763': {'reduced_fuel_a1': 0.0001498699734856, 'reduced_fuel_a2': 4.1777176647610075, 'reduced_fuel_intercept': 2897.9537791913026},
            'B764': {'reduced_fuel_a1': 0.0001395325459059, 'reduced_fuel_a2': 5.114127993219688, 'reduced_fuel_intercept': 2381.9024793420685},
            'B772': {'reduced_fuel_a1': 0.0001914747351383, 'reduced_fuel_a2': 5.782782753633973, 'reduced_fuel_intercept': 3631.7961997048337},
            'B773': {'reduced_fuel_a1': 5.538872222565771e-05, 'reduced_fuel_a2': 8.815299638918951, 'reduced_fuel_intercept': 1523.2308861083802},
            'B77L': {'reduced_fuel_a1': 0.000187327605956, 'reduced_fuel_a2': 5.340268459176023, 'reduced_fuel_intercept': 4948.453927021372},
            'B77W': {'reduced_fuel_a1': 0.0002100662403456, 'reduced_fuel_a2': 6.448265007681931, 'reduced_fuel_intercept': 4650.533009643688},
            'B788': {'reduced_fuel_a1': 0.0001189480776098, 'reduced_fuel_a2': 3.915939456305177, 'reduced_fuel_intercept': 2992.551574337729},
            'B789': {'reduced_fuel_a1': 0.0001183339933326, 'reduced_fuel_a2': 3.8896865199583086, 'reduced_fuel_intercept': 3252.7546948675517},
            'B78X': {'reduced_fuel_a1': 6.96546740401871e-05, 'reduced_fuel_a2': 4.9773040757617, 'reduced_fuel_intercept': 2688.3477805166585},
            'BCS1': {'reduced_fuel_a1': -3.664096369648817e-05, 'reduced_fuel_a2': 2.643412792798112, 'reduced_fuel_intercept': 946.8722926376108},
            'BCS3': {'reduced_fuel_a1': 7.443724168476606e-05, 'reduced_fuel_a2': 2.6444285855634635, 'reduced_fuel_intercept': 1125.1345884342045},
            'BE20': {'reduced_fuel_a1': 0.0001303970296386, 'reduced_fuel_a2': 0.4105068660204155, 'reduced_fuel_intercept': 96.25496475566538},
            'BE40': {'reduced_fuel_a1': 0.0003617800752137, 'reduced_fuel_a2': 0.2171313723076476, 'reduced_fuel_intercept': 391.7302550427421},
            'BE55': {'reduced_fuel_a1': 6.889557082612185e-07, 'reduced_fuel_a2': 0.3202570786539638, 'reduced_fuel_intercept': 30.36468757934483},
            'BN2P': {'reduced_fuel_a1': -8.205128215754698e-09, 'reduced_fuel_a2': 0.132753989743574, 'reduced_fuel_intercept': 21.547735384622264},
            'C172': {'reduced_fuel_a1': 1.2380190733546348e-06, 'reduced_fuel_a2': 0.1172950026862793, 'reduced_fuel_intercept': 11.483789127163092},
            'C208': {'reduced_fuel_a1': -3.67204459308379e-05, 'reduced_fuel_a2': 0.409798958305413, 'reduced_fuel_intercept': 35.55777284282115},
            'C25A': {'reduced_fuel_a1': -0.000282693779264, 'reduced_fuel_a2': 0.5862234916387068, 'reduced_fuel_intercept': 239.36721284281825},
            'C310': {'reduced_fuel_a1': 9.448978075532466e-07, 'reduced_fuel_a2': 0.2628322330731762, 'reduced_fuel_intercept': 44.83353114827668},
            'C680': {'reduced_fuel_a1': 2.5546695713196677e-05, 'reduced_fuel_a2': 0.8718606846703527, 'reduced_fuel_intercept': 330.4345529840358},
            'CRJ1': {'reduced_fuel_a1': 0.0001034796676926, 'reduced_fuel_a2': 1.3108614265324785, 'reduced_fuel_intercept': 500.6895406352646},
            'CRJ2': {'reduced_fuel_a1': -2.11890390524605e-05, 'reduced_fuel_a2': 1.4390157984528462, 'reduced_fuel_intercept': 437.06905144489065},
            'CRJ7': {'reduced_fuel_a1': 6.393263464610222e-05, 'reduced_fuel_a2': 1.8737227331809316, 'reduced_fuel_intercept': 683.5325674653322},
            'CRJ9': {'reduced_fuel_a1': 6.253854476767629e-05, 'reduced_fuel_a2': 1.9514863304008472, 'reduced_fuel_intercept': 679.4050140092891},
            'CRJX': {'reduced_fuel_a1': 7.589077616154682e-05, 'reduced_fuel_a2': 1.8814076564312476, 'reduced_fuel_intercept': 732.788165874158},
            'CVLT': {'reduced_fuel_a1': 0.0001075431766106, 'reduced_fuel_a2': 1.2467937281785135, 'reduced_fuel_intercept': 177.1336926863886},
            'D228': {'reduced_fuel_a1': -0.0005777542326272, 'reduced_fuel_a2': 0.9370732551466758, 'reduced_fuel_intercept': 5.040827335603524},
            'D328': {'reduced_fuel_a1': -0.000245484831348, 'reduced_fuel_a2': 1.0680542090625096, 'reduced_fuel_intercept': 99.0574540055157},
            'DC94': {'reduced_fuel_a1': -0.0007380147037094, 'reduced_fuel_a2': 4.582581485903085, 'reduced_fuel_intercept': 1369.165916181886},
            'DH8A': {'reduced_fuel_a1': 5.4913163527237074e-05, 'reduced_fuel_a2': 1.2006748185217966, 'reduced_fuel_intercept': 82.97030736129432},
            'DH8B': {'reduced_fuel_a1': 5.294023651969404e-05, 'reduced_fuel_a2': 1.1298379879022638, 'reduced_fuel_intercept': 129.97126030913932},
            'DH8C': {'reduced_fuel_a1': 3.777230345836102e-05, 'reduced_fuel_a2': 1.2037109332443952, 'reduced_fuel_intercept': 130.9784890760368},
            'DH8D': {'reduced_fuel_a1': 4.137944106852309e-05, 'reduced_fuel_a2': 1.7022924843561966, 'reduced_fuel_intercept': 283.1844509558705},
            'DHC2': {'reduced_fuel_a1': 9.394277217245062e-09, 'reduced_fuel_a2': 0.1350185932366991, 'reduced_fuel_intercept': 18.63214523969382},
            'DHC3': {'reduced_fuel_a1': 9.394277217245062e-09, 'reduced_fuel_a2': 0.1350185932366991, 'reduced_fuel_intercept': 18.63214523969382},
            'DHC6': {'reduced_fuel_a1': -3.187691776518342e-05, 'reduced_fuel_a2': 0.6932737741810914, 'reduced_fuel_intercept': 28.91433554960173},
            'DHC7': {'reduced_fuel_a1': 0.0002256334072254, 'reduced_fuel_a2': 1.1144926491500595, 'reduced_fuel_intercept': 176.61790516295764},
            'DOVE': {'reduced_fuel_a1': 4.041204013649491e-07, 'reduced_fuel_a2': 0.4755121958528177, 'reduced_fuel_intercept': 41.24593693051449},
            'E110': {'reduced_fuel_a1': -0.0003954964631726, 'reduced_fuel_a2': 0.8019004282308231, 'reduced_fuel_intercept': 26.372293222619906},
            'E120': {'reduced_fuel_a1': 3.396360803553655e-05, 'reduced_fuel_a2': 0.7743334032519721, 'reduced_fuel_intercept': 130.4671411820412},
            'E135': {'reduced_fuel_a1': 3.881248459891573e-05, 'reduced_fuel_a2': 1.2802797068989786, 'reduced_fuel_intercept': 454.7038392357124},
            'E145': {'reduced_fuel_a1': 6.627833586003717e-05, 'reduced_fuel_a2': 1.3677383218438812, 'reduced_fuel_intercept': 466.9392548458616},
            'E170': {'reduced_fuel_a1': 7.130386850828785e-05, 'reduced_fuel_a2': 1.788021961966271, 'reduced_fuel_intercept': 734.8443010720312},
            'E190': {'reduced_fuel_a1': 2.5220395766467615e-05, 'reduced_fuel_a2': 2.272342310053173, 'reduced_fuel_intercept': 890.103548483628},
            'E195': {'reduced_fuel_a1': 9.296909049849587e-05, 'reduced_fuel_a2': 2.3434015643042234, 'reduced_fuel_intercept': 916.1048684752524},
            'E55P': {'reduced_fuel_a1': 2.8113528481754635e-05, 'reduced_fuel_a2': 0.5055806987093875, 'reduced_fuel_intercept': 263.0596628859755},
            'E75L': {'reduced_fuel_a1': 6.231272060497339e-05, 'reduced_fuel_a2': 1.7380947411831915, 'reduced_fuel_intercept': 765.1390243066526},
            'E75S': {'reduced_fuel_a1': 7.633313186405921e-05, 'reduced_fuel_a2': 1.8679073517735911, 'reduced_fuel_intercept': 748.818136677678},
            'F100': {'reduced_fuel_a1': 2.5980478899789716e-05, 'reduced_fuel_a2': 2.553982635471138, 'reduced_fuel_intercept': 986.7481180215008},
            'F27': {'reduced_fuel_a1': -0.0002541926266987, 'reduced_fuel_a2': 1.7277585574099523, 'reduced_fuel_intercept': 196.6758335860028},
            'F28': {'reduced_fuel_a1': -0.0002118866030524, 'reduced_fuel_a2': 2.4395667107842223, 'reduced_fuel_intercept': 919.63434762249},
            'F406': {'reduced_fuel_a1': -0.000172874678558, 'reduced_fuel_a2': 0.5916633519137168, 'reduced_fuel_intercept': 38.58854171684939},
            'F50': {'reduced_fuel_a1': -1.68579521124812e-05, 'reduced_fuel_a2': 1.603938199337737, 'reduced_fuel_intercept': 97.73412608032277},
            'F70': {'reduced_fuel_a1': 3.483050040475888e-05, 'reduced_fuel_a2': 2.154224431496384, 'reduced_fuel_intercept': 878.6415972747859},
            'GLF4': {'reduced_fuel_a1': -9.206168393838254e-06, 'reduced_fuel_a2': 2.0034530687683447, 'reduced_fuel_intercept': 776.3846882051707},
            'GLF5': {'reduced_fuel_a1': 8.496701035021204e-05, 'reduced_fuel_a2': 1.095257753616579, 'reduced_fuel_intercept': 856.2936427087615},
            'IL96': {'reduced_fuel_a1': 0.0003355134308113, 'reduced_fuel_a2': 6.6844565547395085, 'reduced_fuel_intercept': 3886.784383823287},
            'J328': {'reduced_fuel_a1': 0.0002338523634559, 'reduced_fuel_a2': 0.9637716785777416, 'reduced_fuel_intercept': 519.1105608572915},
            'JS31': {'reduced_fuel_a1': -1.3220003405312042e-06, 'reduced_fuel_a2': 0.5713326852277414, 'reduced_fuel_intercept': 66.96258057491974},
            'JS32': {'reduced_fuel_a1': -3.3202229312800924e-05, 'reduced_fuel_a2': 0.6341877292061346, 'reduced_fuel_intercept': 59.2533679466319},
            'JS41': {'reduced_fuel_a1': -1.2082975956007049e-05, 'reduced_fuel_a2': 0.769800713351197, 'reduced_fuel_intercept': 104.27394833382344},
            'L410': {'reduced_fuel_a1': 4.591700730749438e-07, 'reduced_fuel_a2': 0.8687432438994225, 'reduced_fuel_intercept': 57.7775495453979},
            'MD81': {'reduced_fuel_a1': 0.0001858628498956, 'reduced_fuel_a2': 3.3496268406160934, 'reduced_fuel_intercept': 1377.4108977098076},
            'MD82': {'reduced_fuel_a1': 0.0001642883930386, 'reduced_fuel_a2': 3.3107279063446025, 'reduced_fuel_intercept': 1363.4140348026076},
            'MD83': {'reduced_fuel_a1': 0.0001459972320678, 'reduced_fuel_a2': 3.4171974425632308, 'reduced_fuel_intercept': 1333.2290201545793},
            'MD87': {'reduced_fuel_a1': 0.0001229420769854, 'reduced_fuel_a2': 3.1550321556345344, 'reduced_fuel_intercept': 1323.906130239403},
            'MD88': {'reduced_fuel_a1': 0.0001469270242324, 'reduced_fuel_a2': 3.3449436030636535, 'reduced_fuel_intercept': 1348.501342350547},
            'MD90': {'reduced_fuel_a1': 0.0001511166380416, 'reduced_fuel_a2': 3.427298079612508, 'reduced_fuel_intercept': 1334.1836888132611},
            'P28B': {'reduced_fuel_a1': 2.2807878111152926e-07, 'reduced_fuel_a2': 0.137086252545506, 'reduced_fuel_intercept': 18.05093881829021},
            'PA31': {'reduced_fuel_a1': 3.943218134239146e-07, 'reduced_fuel_a2': 0.4755192978074509, 'reduced_fuel_intercept': 41.244657480513666},
            'PA46': {'reduced_fuel_a1': -0.0001679652383734, 'reduced_fuel_a2': 0.2894163162406889, 'reduced_fuel_intercept': 17.568703209879217},
            'PC12': {'reduced_fuel_a1': 2.810992423724068e-05, 'reduced_fuel_a2': 0.3035124397652268, 'reduced_fuel_intercept': 54.70847918002542},
            'RJ1H': {'reduced_fuel_a1': 0.0002294929775152, 'reduced_fuel_a2': 2.5829642807420203, 'reduced_fuel_intercept': 1190.9403071438264},
            'RJ85': {'reduced_fuel_a1': 0.0001193878936063, 'reduced_fuel_a2': 2.512925009824641, 'reduced_fuel_intercept': 1111.1277650256816},
            'SB20': {'reduced_fuel_a1': 6.951271057831221e-05, 'reduced_fuel_a2': 1.230813290288315, 'reduced_fuel_intercept': 240.9698013823472},
            'SF34': {'reduced_fuel_a1': 3.761065756624493e-05, 'reduced_fuel_a2': 0.8668857367792905, 'reduced_fuel_intercept': 105.6885620679833},
            'SU95': {'reduced_fuel_a1': -1.590219730163156e-05, 'reduced_fuel_a2': 2.6098410185373004, 'reduced_fuel_intercept': 758.7285792270977},
            'SW4': {'reduced_fuel_a1': 3.887258047974296e-05, 'reduced_fuel_a2': 0.5434736952797017, 'reduced_fuel_intercept': 79.65634302404072},
            'T134': {'reduced_fuel_a1': 0.0001588596945443, 'reduced_fuel_a2': 2.2965986311400504, 'reduced_fuel_intercept': 1903.6897216554444},
            'T154': {'reduced_fuel_a1': -3.740893149739577e-05, 'reduced_fuel_a2': 6.33528504824825, 'reduced_fuel_intercept': 1809.615118758342},
            'T204': {'reduced_fuel_a1': 0.0001518677745644, 'reduced_fuel_a2': 3.766156885359951, 'reduced_fuel_intercept': 1780.3599248722055},
            'Y12': {'reduced_fuel_a1': 6.525762169418137e-06, 'reduced_fuel_a2': 0.4703308850859443, 'reduced_fuel_intercept': 37.75680617124655},
            'YK40': {'reduced_fuel_a1': -0.0001548367132402, 'reduced_fuel_a2': 2.4829198850833447, 'reduced_fuel_intercept': 506.99668437757646},
            'YK42': {'reduced_fuel_a1': -3.869155508162691e-05, 'reduced_fuel_a2': 4.270710201048868, 'reduced_fuel_intercept': 1162.5017666089334}
        }

        
    @ureg.check(
        None, # string
        '[length]',
    )
    def calculate_fuel_consumption_based_on_seymour_etal(
        acft: str,
        R: float,
    ) -> ureg.Quantity:
        """
        Given an ICAO aircraft designator and mission range, calculates the fuel burned. An "average" payload is assumed for every aircraft.

        _extended_summary_

        INCLUDES RESERVE ETC.?

        See Also
        --------
        -[Seymour et al. (2020), supplementary document "Appendices A-M", Table M.7](https://doi.org/10.1016/j.trd.2020.102528)
        -[CSV of regression coefficients from Table M.7 at the FEAT GitHub repository](https://github.com/kwdseymour/FEAT/blob/master/ac_model_coefficients.csv)

        Parameters
        ----------
        acft : str
            ICAO Aircraft Designator
        R : float
            Mission range [length]

        Returns
        -------
        ureg.Quantity
            Fuel burned during flight [mass]

        """

        R = R.to('km').magnitude

        if acft not in self.dict_regression_coefficients.keys():
            raise ValueError(f"ICAO Aircraft Designator '{acft}' not found in model data.")

        weight_fuel = self.dict_regression_coefficients[acft]['reduced_fuel_a1'] ** 2 * R + self.dict_regression_coefficients[acft]['reduced_fuel_a2'] * R + self.dict_regression_coefficients[acft]['reduced_fuel_intercept']
        return weight_fuel * ureg('kg')
    

class fuel_burn_model_aim2015():
    """
    Reduced-order fuel burn model based on the AIM2015 air transport model (part "Aircraft Performance Model").

    ![Payload/Range Diagram](https://raw.githubusercontent.com/sustainableaviation/jetfuelburn/refs/heads/main/docs/_static/reduced_order_aim2015.svg)
    
    In this model, fuel burn calculations are based on a regression model.
    The regression coefficients were obtained by fitting mission parameters to fuel burn data obtained
    from the Eurocontrol BADA flight trajectory simulation model and climb/descent fuel burn data.

    References
    ----------
    - Dray, L. M., Krammer, P., Doyme, K., Wang, B., Al Zayat, K., O'Sullivan, A., & Schäfer, A. W. (2019).
    AIM2015: Validation and initial results from an open-source aviation systems model.
    _Transport Policy_, 79, 93-102.
    doi:[10.1016/j.tranpol.2019.04.013](https://doi.org/10.1016/j.tranpol.2019.04.013)
    - [AIM2015 documentation (v9)](https://web.archive.org/web/20241206191807/https://www.atslab.org/wp-content/uploads/2019/12/AIM-2015-Documentation-v9-122019.pdf)
    - [AIM2015 information in the EU MIDAS system](https://web.jrc.ec.europa.eu/policy-model-inventory/explore/models/model-aim/)


    """