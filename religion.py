#!/usr/bin/env python3

from os import path
import csv

DATA_DIR = 'data/infostat.nsi.bg'

IN_FILE = 'ВЕРОИЗПОВЕДАНИЕ.csv'


class Religion():
    def __init__(self, abbrev: str, name: str, total: int, orthodox: int, muslims: int,
                 judean: int, other: int, none: int, cant_decide: int, dont_answer: int,
                 not_shown: int):
        self.abbrev = str(abbrev)
        self.name = str(name)
        self.total = int(total)
        self.orthodox = int(orthodox)
        self.muslims = int(muslims)
        self.judean = int(judean)
        self.other = int(other)
        self.none = int(none)
        self.cant_decide = int(cant_decide)
        self.dont_answer = int(dont_answer)
        self.not_shown = int(not_shown)

    def __str__(self):
        return f'{self.abbrev:5} {self.total:7} {self.name}'

    def __repr__(self):
        return f'Език <{self.abbrev:5} {self.total:7} {self.name}>'

    def __hash__(self):
        return hash(self.abbrev)

    def __eq__(self, other):
        if isinstance(other, Religion):
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
                orthodox = int(row[2])
            except ValueError:
                orthodox = 0

            try:
                muslims = int(row[3])
            except ValueError:
                muslims = 0

            try:
                judean = int(row[4])
            except ValueError:
                judean = 0

            try:
                other = int(row[5])
            except ValueError:
                other = 0

            try:
                none = int(row[6])
            except ValueError:
                none = 0

            try:
                cant_decide = int(row[7])
            except ValueError:
                cant_decide = 0

            try:
                dont_answer = int(row[8])
            except ValueError:
                dont_answer = 0

            try:
                not_shown = int(row[9])
            except ValueError:
                not_shown = 0

            new_node = Religion(abbrev, name, total, orthodox, muslims,
                                judean, other, none, cant_decide, dont_answer,
                                not_shown)

            a_set.add(new_node)

    return a_set


class Religions():
    def __init__(self):
        self.nodes = _load()

    def __iter__(self):
        for node in self.nodes:
            yield node


if __name__ == "__main__":
    nodes = Religions()
    for n in nodes:
        print(n)
