# https://ourairports.com/data/
# https://github.com/davidmegginson/ourairports-data/blob/660b39168c35e6f74f8c63836cbff0268b19c5a9/airports.csv

# Licensing Note:
# OurAirports data is in the public domain:
# "All data is released to the Public Domain, and comes with no guarantee of accuracy or fitness for use."
# (https://ourairports.com/data/)

# Processing:
# `airports.csv.gz` is built with `processing/ourairports/ourairports.py`, which
# - keeps airports with an IATA or an ICAO code,
# - drops closed airports,
# - drops the placeholder row with country code "ZZ",
# - drops the placeholder rows whose name starts with "[Duplicate]" or "(Duplicate)",
# - keeps all airport types, heliports and seaplane bases included,
# - stops the build if an IATA or an ICAO code appears more than once,
# - writes names with single spaces,
# - writes the preferred airport last where names repeat, so lookups by name return it (scheduled service, then larger type, then both codes),
# - rounds coordinates to 6 decimals.
