#!/usr/bin/env python3

import json
import sys
from os import path

from locations import Locations
from finance import Finances
from details import SchoolTypes
from transform import Transforms
from municipalities import Municipalities


MON_DIR = 'data/mon.bg'
REGISTER = 'public-register.json'
OUT_FILE = 'json/institutions.json'

RES_DIR = 'data/nvoresults.com'
INTERNAL = 'matura_results.json'
EXTERNAL = 'results.json'
SCHOOLS = 'matura_schools.json'

# https://nvoresults.com/matura_schools.json


class Institution():
    # 2 - Общинско
    # 3 - действаща
    def __init__(self, num_id: str, name: str, location: str, finance=2, details=0, status=3):
        self.id = str(num_id)
        self.name = str(name)
        self.location = str(location)
        self.finance = finance
        self.details = details
        self.status = status

        if details != 0:
            return

        name = name.lower()
        if 'частн' in name:
            self.finance = 3

        code = 122
        if 'основно' in name:
            code = 122
        elif 'ОУ' in name:
            code = 122
        elif 'СУ' in name:
            code = 124
        elif 'профилирана' in name:
            code = 125
        elif 'начално' in name:
            code = 121
        elif 'средно' in name:
            code = 124
        elif 'вуи' in name:
            code = 133
        elif 'възпитателно' in name:
            code = 133
        elif 'спортно' in name:
            code = 114
        elif 'обединено' in name:
            code = 123

        self.details = code

    def __str__(self):
        return f'{self.id} {self.name}'

    def __repr__(self):
        return f'Институция <{self.id} {self.name} {self.location}>'

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Institution):
            equal = self.id == other.id

            if equal and self.name != other.name:
                print(f'Внимание: {self.id}: {self.name} != {other.name}')

            if equal and self.name != other.name:
                print(f'Внимание: {self.id}: {self.location} != {other.location}')

            return equal

        return NotImplemented


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return {
            'id': obj.id,
            'name': obj.name,
            'location': obj.location,
            'finance': obj.finance,
            'details': obj.details,
            'status': obj.status,
        }


def _load_mon_data(dir, file_name):

    file_path = path.join(dir, file_name)
    with open(file_path, 'r', encoding='UTF-8') as file:
        try:
            return json.load(file)['data']
        except KeyError as err:
            print('{}: {}'.format(file_path, err))
            sys.exit(1)


def _load_mon():

    i_list = list()
    i_set = set()

    if path.isfile(OUT_FILE):
        try:
            with open(OUT_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            pass

    dir = MON_DIR

    # Territorial units
    locations = Locations()
    if not locations:
        return i_set

    details = SchoolTypes()
    if not details:
        return i_set

    finances = Finances()
    if not finances:
        return i_set

    transforms = Transforms()
    if not transforms:
        return i_set

    register = _load_mon_data(dir, REGISTER)['publicInstitutions']

    for node in register:

        name = node['name']
        location_code = str(node['town']).zfill(5)

        if not locations.find_name(location_code):
            print(f'Невалидно селище {location_code}: {name}')
            continue

        inst_id = int(node['instid'])
        num_id = int(node['id'])

        if inst_id != num_id:
            print(f'Разминаване в кода на институцията {inst_id} != {num_id}')
            continue

        f_code = int(node['financialSchoolType'])
        f_label = finances.find_label(f_code)
        if not f_label:
            print(f'Невалиден финасов код {f_code}: {name}')
            continue

        d_code = int(node['detailedSchoolType'])
        d_label = details.find_label(d_code)
        if not d_label:
            print(f'Невалиден детайлен код {d_code}: {name}')
            continue

        t_code = int(node['transformType'])
        t_label = transforms.find_label(t_code)
        if not t_label:
            print(f'Невалиден код на състоянието {t_code}: {name}')
            continue

        new_unit = Institution(inst_id, name, location_code,
                               f_code, d_code, t_code)

        i_list.append(new_unit)
        i_set.add(new_unit)

    if len(i_set) != len(i_list):
        print(f'Има повтарящи се институции във входния файл')

    return i_set


def _strip_location(location: str) -> str:

    location = location.lower()
    location = location.removeprefix('гр.')
    location = location.removeprefix('с.').strip()

    return location


def _school_is_valid(schools: set, code: str) -> bool:
    for inst in schools:
        if inst.id == code:
            return True
    return False

def _load_rest(schools: Institutions) -> None:

    locations = Locations()
    if not locations:
        return schools

    municipalities = Municipalities()
    if not municipalities:
        return schools

    school_types = SchoolTypes()
    if not school_types:
        return schools

    fin_types = Finances()
    if not fin_types:
        return schools

    file_name = path.join(RES_DIR, SCHOOLS)
    with open(file_name, 'r', encoding='utf-8') as file:
        datum = json.load(file)

        for school_id in datum:

            if _school_is_valid(schools, school_id):
                continue

            school_name = datum[school_id]['data']['school']
            city_name = _strip_location(datum[school_id]['data']['city'])
            mun_name = _strip_location(datum[school_id]['data']['obshtina'])

            mun_abbrev = municipalities.find_abbrev(mun_name)
            if not mun_abbrev:
                print(f'Не намирам кода на община "{mun_name}" "{school_name}"')
                continue

            town_code = locations.find_code(city_name, mun_abbrev=mun_abbrev)
            if not town_code:
                print(f'Не намирам кода за населено място "{city_name}" "{school_name}"')
                continue

            f_code = fin_types.find_code(school_name)
            d_code = school_types.find_code(school_name)
            a_new = Institution(school_id, school_name, town_code, f_code, d_code)
            schools.add(a_new)

    file_name = path.join(RES_DIR, EXTERNAL)
    with open(file_name, 'r', encoding='utf-8') as file:
        datum = json.load(file)

        for school_id in datum:

            if _school_is_valid(schools, school_id):
                continue

            school_name = datum[school_id]['name']
            city_name = _strip_location(datum[school_id]['city'])
            mun_name = _strip_location(datum[school_id]['municipality'])

            mun_abbrev = municipalities.find_abbrev(mun_name)
            if not mun_abbrev:
                print(f'Не намирам кода на община "{mun_name}" "{school_name}"')
                continue

            town_code = locations.find_code(city_name, mun_abbrev=mun_abbrev)
            if not town_code:
                print(f'Не намирам кода за населено място "{city_name}" "{school_name}"')
                continue

            f_code = fin_types.find_code(school_name)
            d_code = school_types.find_code(school_name)
            a_new = Institution(school_id, school_name, town_code, f_code, d_code)
            schools.add(a_new)

    return schools


class Institutions():
    def __init__(self):
        self.nodes = _load_rest(_load_mon())

    def __iter__(self):
        for node in self.nodes:
            yield node

    def is_valid(self, code: str) -> bool:
        for inst in self.nodes:
            if inst.id == code:
                return True
        return False

    def toJSON(self):
        with open(OUT_FILE, 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.nodes, indent=4, cls=Encoder))


if __name__ == "__main__":
    nodes = Institutions()
    nodes.toJSON()

