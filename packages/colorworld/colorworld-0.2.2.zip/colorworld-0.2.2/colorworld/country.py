"""
Functions to convert country names
"""
from __future__ import with_statement

import csv
import re

from os.path import dirname, join

DATA_PATH = join(dirname(__file__), "country-codes.csv")
with file(DATA_PATH) as csv_file:
    country_data = list(csv.reader(csv_file))[1:]

country_codes, country_names, country_full_names, country_member_tests = [], [], [], []
for d in country_data:
    if len(d[5]) != 2:
        continue
    country_codes.append(int(d[0].strip()))
    country_names.append(d[5].strip())
    country_full_names.append(map(str.strip, (d[2].split(','))))
    country_member_tests.append(d[9])
country_count = len(country_codes)
del d, country_data


country_full_names_to_names = {}
country_member_map = {}
for full_names, letter_code, member_test in zip(country_full_names, country_names, country_member_tests):
    for name in full_names:
        country_full_names_to_names[name.lower()] = letter_code
    member_test = member_test.strip()
    if member_test:
        country_member_map[member_test.lower()] = letter_code


def convert_country_full_name_to_name(name):
    "Convert the full name for a country to a 2-letter iso code"
    name = name.lower().strip()
    if name in country_full_names_to_names:
        return country_full_names_to_names[name]

    for member_test, letter_code in country_member_map.items():
        if subseq(member_test.split(), re.split(" *,? *", name)):
            return letter_code
    raise KeyError(name)
    
