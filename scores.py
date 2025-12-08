#!/usr/bin/env python3

import json
import sys
from os import path
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Examination
from models import ExaminationSubject
from models import Institution
from models import Moment


# https://nvoresults.com/matura_results.json
# https://nvoresults.com/matura_schools.json
# https://nvoresults.com/results.json

DATA_DIR = 'data/nvoresults.com'

INTERNAL = 'matura_results.json'
EXTERNAL = 'results.json'


def _find_date_index(exam_date: date, session: Session) -> int:

    d_index = session.query(Moment.index).filter_by(date=exam_date).first()
    if not d_index:
        m = Moment(date=exam_date)
        session.add(m)
        session.commit()
        d_index = session.query(Moment.index).filter_by(date=exam_date).first()

    return d_index[0]


def _process_internal_results(session: Session) -> list:

    rows = []

    file_name = path.join(DATA_DIR, INTERNAL)
    with open(file_name, 'r', encoding='utf-8') as file:
        results = json.load(file)['results']

        for school_id in results:

            i_code = str(school_id)
            i_index = session.query(
                Institution.index).filter_by(code=i_code).first()
            if not i_index:
                print(f'Невалиден код на училище: {i_code}')
                continue

            for date_str in results[school_id]:

                tokens = date_str.replace('.', '_').split('_')
                exam_date = date(int(tokens[0]), int(tokens[1]), 1)

                d_index = _find_date_index(exam_date, session)
                if not d_index:
                    continue

                for subj_str in results[school_id][date_str]:
                    subj_code = session.query(ExaminationSubject.code).filter_by(
                        subject=subj_str).first()
                    if not subj_code:
                        print(f'Невалиден код на тема "{subj_str}" в училище "{school_id}"')
                        continue

                    score = results[school_id][date_str][subj_str]['score']
                    students = results[school_id][date_str][subj_str]['numberOfStudents']

                    exam = Examination(institution_index=i_index[0],
                                       date_index=d_index, grade=12,
                                       subject_code=subj_code[0], score=score,
                                       students=students)

                    rows.append(exam)
    return rows


def _process_external_results(session: Session) -> list:

    rows = []

    math_code = session.query(ExaminationSubject.code).filter_by(subject='Математика').first()[0]
    lang_code = session.query(ExaminationSubject.code).filter_by(subject='Български език и литература').first()[0]

    file_name = path.join(DATA_DIR, EXTERNAL)
    with open(file_name, 'r', encoding='utf-8') as file:
        results = json.load(file)

        for res in results:

            school_code = str(res)
            school_name = results[school_code]['name']
            city_name = results[school_code]['city']

            i_index = session.query(Institution.index).filter_by(
                code=school_code).first()
            if not i_index:
                print(f'Невалиден код на училище "{school_code}" "{school_name}" "{city_name}"')
                continue

            for date_str in results[school_code]['exam_results']:

                tokens = date_str.split('_')
                exam_date = date(2000 + int(tokens[2]), 5, 1)

                d_index = _find_date_index(exam_date, session)
                if not d_index:
                    continue

                grade = int(results[school_code]
                            ['exam_results'][date_str]['grade'])

                score = results[school_code]['exam_results'][date_str]['bel_score']
                students = results[school_code]['exam_results'][date_str]['bel_students']

                exam = Examination(institution_index=i_index[0],
                                   date_index=d_index, grade=grade,
                                   subject_code=lang_code, score=score,
                                   students=students)

                rows.append(exam)

                score = results[school_code]['exam_results'][date_str]['math_score']
                students = results[school_code]['exam_results'][date_str]['math_students']

                exam = Examination(institution_index=i_index[0],
                                   date_index=d_index, grade=grade,
                                   subject_code=math_code, score=score,
                                   students=students)

                rows.append(exam)

    return rows


def _load(session: Session) -> list:

    external = _process_external_results(session)
    internal = _process_internal_results(session)
    internal.extend(external)

    return internal


if __name__ == "__main__":

    engine = create_engine("postgresql://localhost/infobg")

    with Session(engine) as session:

        rows = _load(session)
        if not rows:
            sys.exit(0)

        session.add_all(rows)
        session.commit()

        rows = session.query(Examination).filter_by(institution_index=512).all()
        for r in rows:
            print(r)
