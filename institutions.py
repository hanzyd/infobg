#!/usr/bin/env python3

import json
import sys
from os import path

from locations import Locations
from finance import Finances
from details import SchoolTypes
from transform import Transforms

DATA_DIR = 'data/mon.bg'
REGISTER = 'public-register.json'
OUT_FILE = 'json/institutions.json'

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


def _load_data(dir, file_name):

    file_path = path.join(dir, file_name)
    with open(file_path, 'r', encoding='UTF-8') as file:
        try:
            return json.load(file)['data']
        except KeyError as err:
            print('{}: {}'.format(file_path, err))
            sys.exit(1)


def _load():

    if path.isfile(OUT_FILE):
        try:
            with open(OUT_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            pass

    dir = DATA_DIR

    # Territorial units
    locations = Locations()
    if not locations:
        return

    details = SchoolTypes()
    if not details:
        return

    finances = Finances()
    if not finances:
        return

    transforms = Transforms()
    if not transforms:
        return

    register = _load_data(dir, REGISTER)['publicInstitutions']

    i_list = list()
    i_set = set()

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


class Institutions():
    def __init__(self):
        self.nodes = _load()

    def is_valid(self, code: str) -> bool:
        for inst in self.nodes:
            if inst.id == code:
                return True
        return False

    def add(self, obj: Institution) -> None:
        self.nodes.add(obj)

    def toJSON(self):
        with open(OUT_FILE, 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.nodes, indent=4, cls=Encoder))


if __name__ == "__main__":
    nodes = Institutions()
    nodes.toJSON()

