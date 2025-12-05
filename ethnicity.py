#!/usr/bin/env python3

from os import path
import csv

DATA_DIR = 'data/infostat.nsi.bg'

IN_FILE = 'ЕТНИЧЕСКА ПРИНАДЛЕЖНОСТ.csv'


class Ethnicity():
    def __init__(self, abbrev: str, name: str, total: int, bul: int, tur: int,
                 roma: int, other: int, cant_decide: int, dont_answer: int,
                 not_shown: int):
        self.abbrev = str(abbrev)
        self.name = str(name)
        self.total = int(total)
        self.bul = int(bul)
        self.tur = int(tur)
        self.roma = int(roma)
        self.other = int(other)
        self.cant_decide = int(cant_decide)
        self.dont_answer = int(dont_answer)
        self.not_shown = int(not_shown)

    def __str__(self):
        return f'{self.abbrev:5} {self.total:7} {self.name}'

    def __repr__(self):
        return f'Етнос <{self.abbrev:5} {self.total:7} {self.name}>'

    def __hash__(self):
        return hash(self.abbrev)

    def __eq__(self, other):
        if isinstance(other, Ethnicity):
            equal = self.abbrev == other.abbrev

            if equal and self.name != other.name:
                print(f'Внимание: {self.abbrev}: {self.name} != {other.name}')

            return equal

        return NotImplemented


def _load():

    a_set = set()

    file_path = path.join(DATA_DIR, IN_FILE)
    with open(file_path, newline='') as csv_file:
        spam = csv.reader(csv_file, delimiter=';')

        next(spam)
        next(spam)
        next(spam)

        for row in spam:
            nick_and_name = row[0].split(' ', 1)

            abbrev = str(nick_and_name[0])
            name = str(nick_and_name[1])

            total = int(row[1])

            try:
                bul = int(row[2])
            except ValueError:
                bul = 0

            try:
                tur = int(row[3])
            except ValueError:
                tur = 0

            try:
                roma = int(row[4])
            except ValueError:
                roma = 0

            try:
                other = int(row[5])
            except ValueError:
                other = 0

            try:
                cant_decide = int(row[6])
            except ValueError:
                cant_decide = 0

            try:
                dont_answer = int(row[7])
            except ValueError:
                dont_answer = 0

            try:
                not_shown = int(row[8])
            except ValueError:
                not_shown = 0

            new_node = Ethnicity(abbrev, name, total, bul, tur,
                                 roma, other, cant_decide, dont_answer,
                                 not_shown)

            a_set.add(new_node)

    return a_set


class Ethnicities():
    def __init__(self):
        self.nodes = _load()

    def __iter__(self):
        for node in self.nodes:
            yield node


if __name__ == "__main__":
    nodes = Ethnicities()
    for n in nodes:
        print(n)
