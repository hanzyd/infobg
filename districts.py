#!/usr/bin/env python3

import json
import glob
from os import path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import District

# https://www.nsi.bg/nrnm/ekatte/archive

DATA_DIR = 'data/nsi.bg'

"""
  name      Char 25  - Наименование на областта
  abbrev    Char 3   - Идентификационен код на областта (3 букви).
"""


def _process_one_year(dir: str, unique_filter: set) -> list:

    a_json = None
    table_rows = list()

    file_path = path.join(dir, 'ek_obl.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        a_json = json.load(file)

    if not a_json:
        return table_rows

    for m in a_json[:-1]:
        abbrev = m['oblast']
        if abbrev in unique_filter:
            continue
        unique_filter.add(abbrev)
        d_name = m['name'].lower().capitalize()
        new_unit = District(name=d_name, abbrev=abbrev)
        table_rows.append(new_unit)

    return table_rows


def _load(dir_name):

    unique_filter = set()
    rows = list()
    for dir in glob.iglob(f'{dir_name}/*'):
        one = _process_one_year(dir, unique_filter)
        rows.extend(one)

    return rows

if __name__ == "__main__":
    rows = _load(DATA_DIR)
    if not rows:
        sys.exit(0)

    engine = create_engine("postgresql://localhost/infobg")
    with Session(engine) as session:
        session.add_all(rows)
        session.commit()

        row = session.query(District).filter_by(abbrev='SHU').first()
        print(row)
