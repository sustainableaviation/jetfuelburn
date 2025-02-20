fixture_lee_etal = {
    # Table 3 in Lee et al.
    'B732+JT9D9': {
        'W_E': 265825 * ureg.N,
        'W_MPLD': 156476 * ureg.N,
        'W_MTO': 513422 * ureg.N,
        'W_MF': 142365 * ureg.N,
        'S': 91.09 * ureg.m**2,
        'c': 2.131e-4 * (1/ureg.s),
        'h': 9144 * ureg.m,
        'f_res': 0.08,
        'f_man': 0.007,
        'C_D0': 0.0214,
        'C_D2': 0.0462,
        'Mach': 0.74
    },
}



V = calculate_aircraft_velocity(mach_number=fixture_lee_etal['B732+JT9D9']['Mach'], altitude=fixture_lee_etal['B732+JT9D9']['h'])

m_f, m_pld = calculate_fuel_consumption_based_on_lee_etal(
    acft='B732',
    W_E=fixture_lee_etal['B732+JT9D9']['W_E'],
    W_MPLD=fixture_lee_etal['B732+JT9D9']['W_MPLD'],
    W_MTO=fixture_lee_etal['B732+JT9D9']['W_MTO'],
    W_MF=fixture_lee_etal['B732+JT9D9']['W_MF'],
    S=fixture_lee_etal['B732+JT9D9']['S'],
    C_D0=fixture_lee_etal['B732+JT9D9']['C_D0'],
    C_D2=fixture_lee_etal['B732+JT9D9']['C_D2'],
    c=fixture_lee_etal['B732+JT9D9']['c'],
    h=fixture_lee_etal['B732+JT9D9']['h'],
    V=V,
    d=1705 * ureg.nmi
)
