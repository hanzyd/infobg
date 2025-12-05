#!/usr/bin/env python3

import json
import sys
from os import path

DATA_DIR = 'data/mon.bg'

IN_FILE = 'financialSchoolType.json'
OUT_FILE = 'json/finances.json'

# https://nvoresults.com/matura_schools.json


class Finance():
    def __init__(self, code: int, label: str):
        self.code = int(code)
        self.label = str(label)

    def __str__(self):
        return f'{self.code} {self.label}'

    def __repr__(self):
        return f'Финансиране <{self.code} {self.label}>'

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        if isinstance(other, Finance):
            equal = self.code == other.code

            if equal and self.label != other.label:
                print(f'Внимание: {self.code}: {self.label} != {other.label}')

            return equal

        return NotImplemented


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return {
            'code': obj.code,
            'label': obj.label,
        }


def _load():

    if path.isfile(OUT_FILE):
        try:
            with open(OUT_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            pass

    i_set = set()
    file_path = path.join(DATA_DIR, IN_FILE)
    with open(file_path, 'r', encoding='UTF-8') as file:

        finance_types = json.load(file)['data']

        i_set = set()

        for node in finance_types:

            valid = str(node['isValid'])
            if valid != 'True':
                continue

            code = int(node['code'])
            label = str(node['label'])

            new_unit = Finance(code, label)
            i_set.add(new_unit)

    return i_set


class Finances():
    def __init__(self):
        self.nodes = _load()

    def __iter__(self):
        for node in self.nodes:
            yield node

    @staticmethod
    def find_code(school_name: str) -> int:
        name = school_name.lower()
        if 'частн' in name:
            return 3
        return 1

    def find_label(self, code: int) -> str:
        for n in self.nodes:
            if n.code == code:
                return n.label
        return None

    def toJSON(self):
        with open(OUT_FILE, 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.nodes, indent=4, cls=Encoder))


if __name__ == "__main__":
    nodes = Finances()
    nodes.toJSON()
