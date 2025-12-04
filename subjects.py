#!/usr/bin/env python3

import json
from os import path


DATA_DIR = 'data/nvoresults.com'
INTERNAL = 'matura_results.json'
OUT_FILE = 'json/subjects.json'


class Subject():

    def __init__(self, code: int, title: str):
        self.code = int(code)
        self.title = str(title)

    def __str__(self):
        return f'{self.title}'

    def __repr__(self):
        return f'Тема <{self.code} {self.title}>'

    def __hash__(self):
        return hash(self.code)

    def __eq__(self, other):
        if isinstance(other, Subject):
            equal = self.code == other.code

            if equal and self.title != other.title:
                print(f'Внимание: {self.code}: {self.title} != {other.title}')

            return equal

        return NotImplemented


def _load_subjects():

    if path.isfile(OUT_FILE):
        try:
            with open(OUT_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            pass

    file_path = path.join(DATA_DIR, INTERNAL)

    t_set = set()
    s_set = set()

    with open(file_path, 'r', encoding='utf-8') as file:
        results = json.load(file)['results']
        for school_str in results:
            for date_str in results[school_str]:
                for subject in results[school_str][date_str]:
                    t_set.add(subject)

    t_set.add('Български език и литература')
    t_set.add('Математика')

    for num, subject in enumerate(t_set):
        s_set.add(Subject(num + 1, subject))

    return s_set


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return {
            'code': obj.code,
            'title': obj.title,
        }


class Subjects():
    def __init__(self):
        self.nodes = _load_subjects()

    def find_subject(self, code: int) -> str:
        for n in self.nodes:
            if n.code == code:
                return n.title
        return None

    def find_code(self, title: str) -> int:
        for n in self.nodes:
            if n.title == title:
                return n.code
        return None

    def toJSON(self):
        with open(OUT_FILE, 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.nodes, indent=4, cls=Encoder))


if __name__ == "__main__":
    nodes = Subjects()
    nodes.toJSON()
