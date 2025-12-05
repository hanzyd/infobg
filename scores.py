#!/usr/bin/env python3

import json
import sys
from os import path
from datetime import date

from locations import Locations
from municipalities import Municipalities
from subjects import Subjects
from institutions import Institutions, Institution
from details import SchoolTypes
from finance import Finances


# https://nvoresults.com/matura_results.json
# https://nvoresults.com/matura_schools.json
# https://nvoresults.com/results.json

DATA_DIR = 'data/nvoresults.com'

INTERNAL = 'matura_results.json'
EXTERNAL = 'results.json'
SCHOOLS = 'matura_schools.json'

OUT_FILE = 'json/scores.json'


class Score():

    def __init__(self, school_id: str, date_str: str, grade: int, subject: int, score: int, students: int):
        self.id = school_id
        self.date = date_str
        self.grade = grade
        self.subject = subject
        self.score = score
        self.students = students

    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'Резултат <{self.id} {self.date} {self.grade} {self.subject}>'

    def __hash__(self):
        return hash((self.id, self.date, self.grade, self.subject))

    def __eq__(self, other):
        if isinstance(other, Score):

            equal = self.id == other.id and \
                self.date == other.date and \
                self.grade == other.grade and \
                self.subject == other.subject

            if equal and self.score != other.score:
                print(f'Внимание: {self.id}: {self.score} != {other.score}')

            if equal and self.students != other.students:
                print(f'Внимание: {self.id}: {self.students} != {other.students}')

            return equal

        return NotImplemented


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return {
            'id': obj.id,
            'date': obj.date,
            'grade': obj.grade,
            'subject': obj.subject,
            'score': obj.score,
            'students': obj.students
        }


def _process_internal_results(schools: Institutions, subjects: Subjects) -> list:

    a_list = []

    file_name = path.join(DATA_DIR, INTERNAL)
    with open(file_name, 'r', encoding='utf-8') as file:
        results = json.load(file)['results']

        for school_id in results:

            if not schools.is_valid(school_id):
                print(f'Невалиден код на училище "{school_id}"')
                continue

            for date_str in results[school_id]:

                tokens = date_str.replace('.', '_').split('_')
                exam_date = date(int(tokens[0]), int(tokens[1]), 1)

                for subj_str in results[school_id][date_str]:
                    subj_code = subjects.find_code(subj_str)
                    if not subj_code:
                        print(f'Невалиден код на тема "{subj_str}" в училище "{school_id}"')
                        continue

                    score = results[school_id][date_str][subj_str]['score']
                    students = results[school_id][date_str][subj_str]['numberOfStudents']

                    exam = Score(school_id,  exam_date.strftime('%Y-%m'),
                                 subj_code, 12, score, students)

                    a_list.append(exam)

    return a_list


def _process_external_results(schools: Institutions, subjects: Subjects) -> list:

    a_list = []

    math_code = subjects.find_code('Математика')
    lang_code = subjects.find_code('Български език и литература')

    file_name = path.join(DATA_DIR, EXTERNAL)
    with open(file_name, 'r', encoding='utf-8') as file:
        results = json.load(file)

        for school_id in results:

            if not schools.is_valid(school_id):
                school_name = results[school_id]['name']
                city_name = results[school_id]['city']
                print(f'Невалиден код на училище "{school_id}" "{school_name}" "{city_name}"')
                continue

            for date_str in results[school_id]['exam_results']:

                tokens = date_str.split('_')
                exam_date = date(2000 + int(tokens[2]), 5, 1)
                grade = int(results[school_id]['exam_results'][date_str]['grade'])
                score = results[school_id]['exam_results'][date_str]['bel_score']
                students = results[school_id]['exam_results'][date_str]['bel_students']

                exam = Score(school_id,  exam_date.strftime('%Y-%m'),
                             lang_code, grade, score, students)

                a_list.append(exam)

                score = results[school_id]['exam_results'][date_str]['math_score']
                students = results[school_id]['exam_results'][date_str]['math_students']

                exam = Score(school_id,  exam_date.strftime('%Y-%m'),
                             math_code, grade, score, students)

                a_list.append(exam)

    return a_list


def _strip_location(location: str) -> str:

    location = location.lower()
    location = location.removeprefix('гр.')
    location = location.removeprefix('с.').strip()

    return location


def _fill_missing_schools(schools: Institutions) -> None:

    locations = Locations()
    if not locations:
        return

    municipalities = Municipalities()
    if not municipalities:
        return

    school_types = SchoolTypes()
    if not school_types:
        return

    fin_types = Finances()
    if not fin_types:
        return

    file_name = path.join(DATA_DIR, SCHOOLS)
    with open(file_name, 'r', encoding='utf-8') as file:
        datum = json.load(file)

        for school_id in datum:

            if schools.is_valid(school_id):
                continue

            school_name = datum[school_id]['data']['school']
            city_name = _strip_location(datum[school_id]['data']['city'])
            mun_name = _strip_location(datum[school_id]['data']['obshtina'])

            mun_nick = municipalities.find_nickname(mun_name)
            if not mun_nick:
                print(f'Не намирам кода на община "{mun_name}" "{school_name}"')
                continue

            town_code = locations.find_code(city_name, mun_nick=mun_nick)
            if not town_code:
                print(f'Не намирам кода за населено място "{city_name}" "{school_name}"')
                continue

            f_code = fin_types.find_code(school_name)
            d_code = school_types.find_code(school_name)
            a_new = Institution(school_id, school_name, town_code, f_code, d_code)
            print(f'Добавям ново училище {a_new}')
            schools.add(a_new)

        schools.toJSON()

    file_name = path.join(DATA_DIR, EXTERNAL)
    with open(file_name, 'r', encoding='utf-8') as file:
        datum = json.load(file)

        for school_id in datum:

            if schools.is_valid(school_id):
                continue

            school_name = datum[school_id]['name']
            city_name = _strip_location(datum[school_id]['city'])
            mun_name = _strip_location(datum[school_id]['municipality'])

            mun_nick = municipalities.find_nickname(mun_name)
            if not mun_nick:
                print(f'Не намирам кода на община "{mun_name}" "{school_name}"')
                continue

            town_code = locations.find_code(city_name, mun_nick=mun_nick)
            if not town_code:
                print(f'Не намирам кода за населено място "{city_name}" "{school_name}"')
                continue

            f_code = fin_types.find_code(school_name)
            d_code = school_types.find_code(school_name)
            a_new = Institution(school_id, school_name, town_code, f_code, d_code)

            print(f'Добавям ново училище {a_new}')
            schools.add(a_new)

        schools.toJSON()


def _load():

    if path.isfile(OUT_FILE):
        try:
            with open(OUT_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            pass

    subjects = Subjects()
    if not subjects:
        return

    schools = Institutions()
    if not schools:
        return

    _fill_missing_schools(schools)

    external = _process_external_results(schools, subjects)

    internal = _process_internal_results(schools, subjects)

    internal.extend(external)

    return internal


class Scores():
    def __init__(self):
        self.nodes = _load()

    def __iter__(self):
        for node in self.nodes:
            yield node

    def toJSON(self):
        with open(OUT_FILE, 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.nodes, indent=4, cls=Encoder))


if __name__ == "__main__":
    nodes = Scores()
    nodes.toJSON()
