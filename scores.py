#!/usr/bin/env python3

import json
import sys
from os import path
from datetime import date

INTERNAL = 'matura-results.json'
EXTERNAL = 'external-evaluation.json'

EK_UNITS = 'json/territorial_units.json'
SUBJECTS = 'json/exam_subjects.json'
MON_INSTITUTIONS = 'json/public_institutions.json'
SCHOOL_SCORES = 'json/schools_scores.json'


def find_subject_code(subjects: list, subject: str) -> int:

    for node in subjects:
        if node['subject'] == subject:
            return node['code']

    print('Can not find code for subject: {}'.format(subject))
    return -1


def is_valid_institution(schools: list, code: int) -> bool:

    for inst in schools:
        if inst['code'] == code:
            return True

    return False


def extract_exam_subjects(file_name):

    exam_subjects = set()
    dict_subjects = []

    with open(file_name, 'r', encoding='utf-8') as file:
        results = json.load(file)['results']
        for school_str in results:
            for date_str in results[school_str]:
                for subject in results[school_str][date_str]:
                    exam_subjects.add(subject)

    exam_subjects.add('Български език и литература')
    exam_subjects.add('Математика')

    print('{} unique exam subjects'.format(len(exam_subjects)))

    for num, subject in enumerate(exam_subjects):
        dict_subjects.append({'code': num, 'subject': subject})

    with open(SUBJECTS, 'w', encoding='utf-8') as file:
        file.write(json.dumps(dict_subjects, indent=4))

    return dict_subjects


def process_internal_results(file_name: str, schools: list, subj_table: list) -> list:

    dict_results = []

    with open(file_name, 'r', encoding='utf-8') as file:
        results = json.load(file)['results']

        for school_str in results:

            school_code = int(school_str)

            if not is_valid_institution(schools, school_code):
                print('Invalid school code: {}'.format(school_code))
                continue

            for date_str in results[school_str]:

                tokens = date_str.replace('.', '_').split('_')
                exam_date = date(int(tokens[0]), int(tokens[1]), 1)

                for subject_str in results[school_str][date_str]:

                    subject_code = find_subject_code(subj_table, subject_str)
                    score = results[school_str][date_str][subject_str]['score']
                    students = results[school_str][date_str][subject_str]['numberOfStudents']

                    exam = {
                        'school': school_code,
                        'date': exam_date.strftime('%Y-%m'),
                        'subject': subject_code,
                        'grade': 12,
                        'score': score,
                        'students': students
                    }

                    dict_results.append(exam)

    return dict_results


def process_external_results(file_name: str, schools: list, subj_table: list) -> list:

    dict_results = []

    with open(file_name, 'r', encoding='utf-8') as file:
        results = json.load(file)

        for school_str in results:

            school_code = int(school_str)

            if not is_valid_institution(schools, school_code):
                name = results[school_str]['name']
                city = results[school_str]['city']
                print('Invalid school code: {} {} {}'.format(school_code, name, city))
                continue

            for date_str in results[school_str]['exam_results']:

                tokens = date_str.split('_')
                exam_date = date(2000 + int(tokens[2]), 5, 1)

                subject_code = find_subject_code(subj_table, 'Български език и литература')
                grade = int(results[school_str]['exam_results'][date_str]['grade'])

                score = results[school_str]['exam_results'][date_str]['bel_score']
                students = results[school_str]['exam_results'][date_str]['bel_students']

                exam = {
                    'school': school_code,
                    'date': exam_date.strftime('%Y-%m'),
                    'grade': grade,
                    'subject': subject_code,
                    'score': score,
                    'students': students
                }

                dict_results.append(exam)

                subject_code = find_subject_code(subj_table, 'Математика')
                score = results[school_str]['exam_results'][date_str]['math_score']
                students = results[school_str]['exam_results'][date_str]['math_students']

                exam = {
                    'school': school_code,
                    'date': exam_date.strftime('%Y-%m'),
                    'grade': grade,
                    'subject': subject_code,
                    'score': score,
                    'students': students
                }

                dict_results.append(exam)

    return dict_results


def find_territorial_unit_code(ek_units: list, name: str) -> int:

    name = name.lower().removeprefix('гр.').removeprefix('с.').strip()

    for unit in ek_units:
        if unit['name'].lower() == name:
            return int(unit['code'])

    return None

def extract_missing_schools(file_name: str, schools: list) -> list:

    public_institutions = []

    # Territorial units
    ek_json = None
    with open(EK_UNITS, 'r', encoding='utf-8') as file:
        ek_json = json.load(file)

    if not ek_json:
        return

    with open(file_name, 'r', encoding='utf-8') as file:
        results = json.load(file)

        for school_str in results:
            school_code = int(school_str)
            if is_valid_institution(schools, school_code):
                continue

            town_str = results[school_str]['city']
            town_code = find_territorial_unit_code(ek_json, town_str)
            if not town_code:
                print('Can not find code for: {}'.format(town_str))
                continue

            mun_str = results[school_str]['municipality']
            mun_code = find_territorial_unit_code(ek_json, mun_str)
            if not mun_code:
                print('Can not find code for: {}'.format(mun_str))
                continue

            name_str = results[school_str]['name']
            if 'основно' in name_str.lower():
                details_code = 2
            elif 'ОУ' in name_str:
                details_code = 2
            elif 'СУ' in name_str:
                details_code = 124
            elif 'профилирана гимназия' in name_str.lower():
                details_code = 125
            elif 'начално' in name_str.lower():
                details_code = 121
            elif 'средно' in name_str.lower():
                details_code = 124
            elif 'вуи' in name_str.lower():
                details_code = 133
            elif 'възпитателно' in name_str.lower():
                details_code = 133
            else:
                print('{} details unknown'.format(name_str))
                details_code = 2

            public_institutions.append({
                'code': int(school_code),
                'name': name_str,
                'town': town_code,
                'municipality': mun_code,
                'financial': 2, # Общинско
                'details': details_code, # "основно (І - VІІІ клас)"
                'status': 3 # действаща
            })

    return public_institutions


def main(dir):

    file_path = path.join(dir, INTERNAL)
    subjects = extract_exam_subjects(file_path)

    # Territorial units
    schools = None
    with open(MON_INSTITUTIONS, 'r', encoding='utf-8') as file:
        schools = json.load(file)

    if not schools:
        return

    file_path = path.join(dir, EXTERNAL)
    missing = extract_missing_schools(file_path, schools)
    if len(missing):
        schools.extend(missing)
        # Merged information
        with open(MON_INSTITUTIONS, 'w', encoding='utf-8') as file:
            file.write(json.dumps(schools, indent=4))

    external = process_external_results(file_path, schools, subjects)

    file_path = path.join(dir, INTERNAL)
    internal = process_internal_results(file_path, schools, subjects)

    internal.extend(external)

    # Merged information
    with open(SCHOOL_SCORES, 'w', encoding='utf-8') as file:
        file.write(json.dumps(internal, indent=4))


if __name__ == "__main__":
    main('./data/nvoresults.com/')
    sys.exit(0)
