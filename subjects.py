#!/usr/bin/env python3

import json
from os import path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import ExaminationSubject

DATA_DIR = 'data/nvoresults.com'
INTERNAL = 'matura_results.json'


def _load():

    file_path = path.join(DATA_DIR, INTERNAL)

    title_set = set()
    table_rows = set()

    with open(file_path, 'r', encoding='utf-8') as file:
        results = json.load(file)['results']
        for school_str in results:
            for date_str in results[school_str]:
                for subject in results[school_str][date_str]:
                    title_set.add(subject)

    title_set.add('Български език и литература')
    title_set.add('Математика')

    for subject in (title_set):
        table_rows.add(ExaminationSubject(subject=subject))

    return table_rows



if __name__ == "__main__":
    engine = create_engine("postgresql://localhost/infobg")

    with Session(engine) as session:
        rows = _load()
        if not rows:
            sys.exit(0)
        session.add_all(rows)
        session.commit()

        e = session.query(ExaminationSubject).filter_by(subject='Математика').first()
        print(e)