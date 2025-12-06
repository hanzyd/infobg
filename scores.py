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

                    exam = Score(school_id,  exam_date.strftime('%d.%m.%Y'),
                                 12, subj_code, score, students)

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

                exam = Score(school_id,  exam_date.strftime('%d.%m.%Y'),
                             grade, lang_code, score, students)

                a_list.append(exam)

                score = results[school_id]['exam_results'][date_str]['math_score']
                students = results[school_id]['exam_results'][date_str]['math_students']

                exam = Score(school_id,  exam_date.strftime('%d.%m.%Y'),
                             grade, math_code, score, students)

                a_list.append(exam)

    return a_list


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
