#!/usr/bin/env python3

import json
import glob
from os import path

# https://www.nsi.bg/nrnm/ekatte/archive

DATA_DIR = 'data/nsi.bg'
OUT_FILE = 'json/districts.json'


class District():
    """
      name      Char 25  - Наименование на областта
      nickname  Char 3   - Идентификационен код на областта (3 букви).
    """

    def __init__(self, name: str, nickname: str):
        self.name = str(name)
        self.nickname = str(nickname)

    def __str__(self):
        return f'{self.name:25}'

    def __repr__(self):
        return f'Област <{self.name:25} {self.nickname:3}>'

    def __hash__(self):
        return hash(self.nickname)

    def __eq__(self, other):
        if isinstance(other, District):
            equal = self.nickname == other.nickname

            if equal and self.name != other.name:
                print(f'Внимание: {self.nickname}: {self.name} != {other.name}')

            return equal

        return NotImplemented


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return {
            'name': obj.name,
            'nickname': obj.nickname,
        }


def _process_one_year(dir):

    a_json = None
    a_list = list()
    a_set = set()

    file_path = path.join(dir, 'ek_obl.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        a_json = json.load(file)

    if not a_json:
        return a_set

    for m in a_json[:-1]:
        new_unit = District(m['name'], m['oblast'])
        a_list.append(new_unit)
        a_set.add(new_unit)

    if len(a_set) != len(a_list):
        print(f'Има повтарящи се области във входния файл {file_path}')

    return a_set


def _load() -> set:

    if path.isfile(OUT_FILE):
        try:
            with open(OUT_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            pass

    dir_name = DATA_DIR
    districts = set()
    for dir in glob.iglob(f'{dir_name}/*'):
        one = _process_one_year(dir)
        districts.update(one)

    return districts


class Districts():
    def __init__(self):
        self.nodes = _load()

    def find_nickname(self, name: str) -> str:

        for m in self.nodes:
            if m.name.lower() == name.lower():
                return m.nickname
        return None

    def toJSON(self):
        with open(OUT_FILE, 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.nodes, indent=4, cls=Encoder))


if __name__ == "__main__":
    nodes = Districts()
    nodes.toJSON()