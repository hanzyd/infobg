#!/usr/bin/env python3

import json
from os import path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import InstitutionDetails


DATA_DIR = 'data/mon.bg'

IN_FILE = 'detailedSchoolType.json'

# https://nvoresults.com/matura_schools.json


def _load():

    rows = list()
    file_path = path.join(DATA_DIR, IN_FILE)
    with open(file_path, 'r', encoding='UTF-8') as file:

        school_types = json.load(file)['data']

        unique_filter = set()

        for node in school_types:

            valid = str(node['isValid'])
            if valid != 'True':
                continue

            code = int(node['code'])
            if code in unique_filter:
                continue

            unique_filter.add(code)
            label = str(node['label'])

            new_unit = InstitutionDetails(code=code, label=label)
            rows.append(new_unit)

    return rows


def guess_institution_details(school_name: str) -> int:
    name = school_name.lower()
    code = 122
    if 'основно' in name:
        code = 122
    elif 'оу' in name:
        code = 122
    elif 'су' in name:
        code = 124
    elif 'профилирана' in name:
        code = 125
    elif 'начално' in name:
        code = 121
    elif 'средно' in name:
        code = 124
    elif 'вуи' in name:
        code = 133
    elif 'възпитателно' in name:
        code = 133
    elif 'спортно' in name:
        code = 114
    elif 'обединено' in name:
        code = 123

    return code

if __name__ == "__main__":
    engine = create_engine('sqlite:///models.sqlite')

    InstitutionDetails.__table__.drop(engine)
    InstitutionDetails.__table__.create(engine)

    with Session(engine) as session:
        rows = _load()
        if not rows:
            sys.exit(0)
        session.add_all(rows)
        session.commit()

        e = session.query(InstitutionDetails).filter_by(label='обединено').first()
        print(e)
