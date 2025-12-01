#!/usr/bin/env python3

import json
import sys
from os import path

EK_UNITS = 'json/ek_territorial_units.json'


def valid_territorial_unit(ek_units: list, name: str) -> bool:

    if name.lower() == 'други':
        return True

    for unit in ek_units:
        if unit['name'].lower() == name.lower():
            return True

    return False


def label_by_code(data, code):
    for element in data:
        if int(element['code']) == int(code):
            return element['label']
    return None


def load_data(dir, file_name):

    file_path = path.join(dir, file_name)
    with open(file_path, 'r', encoding='UTF-8') as file:
        try:
            return json.load(file)['data']
        except KeyError as err:
            print('{}: {}'.format(file_path, err))
            sys.exit(1)


def main(dir):

    # Territorial units
    ek_json = None
    with open(EK_UNITS, 'r', encoding='utf-8') as file:
        ek_json = json.load(file)

    if not ek_json:
        return

    public_register = load_data(dir, 'public-register.json')['publicInstitutions']
    detailed_type = load_data(dir, 'detailedSchoolType.json')
    financial_type = load_data(dir, 'financialSchoolType.json')
    municipality = load_data(dir, 'municipality.json')
    municipality_multiple = load_data(dir, 'municipalityMultiple.json')
    regions = load_data(dir, 'region.json')
    towns = load_data(dir, 'town.json')
    transform_type = load_data(dir, 'transformType.json')

    public_institutions = []

    for institution in public_register:

        name = institution['name']

        code = institution['municipality']
        label = label_by_code(municipality, code)

        if not label:
            label = label_by_code(municipality_multiple, code)

        if not label:
            print('{}: {}: no municipality label'.format(code, name))
            continue

        if not valid_territorial_unit(ek_json, label):
            print('Invalid municipality {}: {}'.format(label, name))
            continue

        code = institution['region']
        label = label_by_code(regions, code)

        if not label:
            print('{}: {}: no region label'.format(code, name))
            continue

        if not valid_territorial_unit(ek_json, label):
            print('Invalid area {}: {}'.format(label, name))
            continue

        code = institution['town']
        label = label_by_code(towns, code)

        if not label:
            print('{}: {}: no town label'.format(code, name))
            continue

        if not valid_territorial_unit(ek_json, label):
            print('Invalid town {}: {}'.format(label, name))
            continue

        inst_id = int(institution['instid'])
        if inst_id != int(institution['id']):
            print('Institution code mismatch {} != {}'.format(
                inst_id, institution['id']))
            continue

        fin_code = int(institution['financialSchoolType'])
        if not label_by_code(financial_type, fin_code):
            print('Invalid financial code {}: {}'.format(fin_code, name))
            continue

        details_code = int(institution['detailedSchoolType'])
        if not label_by_code(detailed_type, details_code):
            print('Invalid detailed code {}: {}'.format(details_code, name))
            continue

        trans_code = int(institution['transformType'])
        if not label_by_code(transform_type, trans_code):
            print('Invalid transform code {}: {}'.format(trans_code, name))
            continue

        public_institutions.append({
            'code': inst_id,
            'name': name,
            'financial': fin_code,
            'details': details_code,
            'status': trans_code,
        })

    print('Public institutions count: {}'.format(len(public_institutions)))

    # Merged information
    with open(path.join('json', 'mon_public_institutions.json'), 'w', encoding='utf-8') as file:
        file.write(json.dumps(public_institutions, indent=4))


if __name__ == "__main__":
    main('./data/mon.bg/')
    sys.exit(0)
