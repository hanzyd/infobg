#!/usr/bin/env python3

import json
import sys


def label_by_code(data, code):
    for element in data:
        if element['code'] == code:
            return element['label']
    return None

def load_data(file_name):

    with open(file_name, 'r', encoding='UTF-8') as file:
        try:
            return json.load(file)['data']
        except KeyError as err:
            print('{}: {}'.format(file_name, err))
            sys.exit(1)


if __name__ == "__main__":

   public_register = load_data('data/public-register.json')['publicInstitutions']
   detailed_type = load_data('data/detailedSchoolType.json')
   financial_type = load_data('data/financialSchoolType.json')
   municipality = load_data('data/municipality.json')
   municipality_multiple = load_data('data/municipalityMultiple.json')
   regions = load_data('data/region.json')
   towns = load_data('data/town.json')
   transform_type = load_data('data/transformType.json')

   for institution in public_register:

        mun = label_by_code(municipality, institution['municipality'])
        if not mun:
            mun = label_by_code(municipality_multiple, institution['municipality'])

        details = label_by_code(detailed_type, institution['detailedSchoolType'])
        finance = label_by_code(financial_type, institution['financialSchoolType'])
        region = label_by_code(regions, institution['region'])
        town = label_by_code(towns, institution['town'])
        status = label_by_code(transform_type, institution['transformType'])

        print('{}\t{:24}\t{:16}\t{:12}\t{:16}\t{:16}\t{}\t{}'.format(institution['id'], details, mun, finance, region, town, status, institution['name']))
        pass


   sys.exit(0)
