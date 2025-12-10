#!/usr/bin/env python3

import json
from os import path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import InstitutionFinancing

DATA_DIR = 'data/mon.bg'

IN_FILE = 'financialSchoolType.json'

# https://nvoresults.com/matura_schools.json


def _load() -> list:

    table_rows = list()

    file_path = path.join(DATA_DIR, IN_FILE)
    with open(file_path, 'r', encoding='UTF-8') as file:

        finance_types = json.load(file)['data']

        unique_filter = set()

        for node in finance_types:

            valid = str(node['isValid'])
            if valid != 'True':
                continue

            code = int(node['code'])
            if code in unique_filter:
                continue

            unique_filter.add(code)
            label = str(node['label'])

            new_unit = InstitutionFinancing(id=code, label=label)
            table_rows.append(new_unit)

    return table_rows


def guess_institution_financing(school_name: str) -> int:
    name = school_name.lower()
    if 'частн' in name:
        return 3
    return 1    # Държавно


if __name__ == "__main__":
    engine = create_engine("postgresql://localhost/infobg")

    with Session(engine) as session:
        rows = _load()
        if not rows:
            sys.exit(0)
        session.add_all(rows)
        session.commit()

        e = session.query(InstitutionFinancing).filter_by(label='Частно').first()
        print(e)