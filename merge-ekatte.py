#!/usr/bin/env python3

import json
import sys
from os import path

# https://www.nsi.bg/nrnm/ekatte/archive


def find_municipality_code(municipalities: list, name: str) -> int:

    for m in municipalities:
        if m['obshtina'] == name:
            return int(m['ekatte'])

    print('Can\'t find {} municipality code'.format(name))
    return 0


def find_area_code(areas: list, name: str) -> int:

    for m in areas:
        if m['oblast'] == name:
            return int(m['ekatte'])

    print('Can\'t find {} area code'.format(name))
    return 0


def main(dir):

    unit_json = None
    area_json = None
    mun_json = None
    merged_json = []

    # Territorial units
    with open(path.join(dir, 'ek_atte.json'), 'r', encoding='utf-8') as file:
        unit_json = json.load(file)

    # Area units
    with open(path.join(dir, 'ek_obl.json'), 'r', encoding='utf-8') as file:
        area_json = json.load(file)

    # Municipality units
    with open(path.join(dir, 'ek_obst.json'), 'r', encoding='utf-8') as file:
        mun_json = json.load(file)

    if not unit_json or not area_json or not mun_json:
        return

    # Ignore last element
    for unit in unit_json[:-1]:

        try:
            mun_name = unit['obshtina']
        except KeyError as err:
            print(err)
            continue

        try:
            area_name = unit['oblast']
        except KeyError as err:
            print(err)
            continue

        mun_code = find_municipality_code(mun_json, mun_name)
        if mun_code == 0:
            continue

        area_code = find_area_code(area_json, area_name)
        if area_code == 0:
            continue

        unit_name = unit['name']

        merged_json.append({
            'code': int(unit['ekatte']),
            'name': str(unit_name),
            'kind': int(unit['kind']),
            'altitude': int(unit['altitude']),
            'area': area_code,
            'municipality': mun_code,
        })

    for unit in mun_json[:-1]:

        unit_name = unit['name']
        unit_code = int(unit['ekatte'])
        mun_name = unit['obshtina']
        area_name = mun_name[:-2]

        area_code = find_area_code(area_json, area_name)
        if area_code == 0:
            continue

        merged_json.append({
            'code': unit_code,
            'name': unit_name,
            'area': area_code,
            'municipality': unit_code,
        })

    for unit in area_json[:-1]:

        unit_name = unit['name']
        unit_code = int(unit['ekatte'])
        area_name = unit['oblast']

        area_code = find_area_code(area_json, area_name)
        if area_code == 0:
            continue

        merged_json.append({
            'code': area_code,
            'name': unit_name,
            'area': area_code,
            'municipality': unit_code,
        })

    print('Territorial units count: {}'.format(len(merged_json)))

    # Merged information
    with open(path.join('json', 'ek_territorial_units.json'), 'w', encoding='utf-8') as file:
        file.write(json.dumps(merged_json, indent=4))


if __name__ == "__main__":
    main('./data/nsi.bg/2025/')
