#!/usr/bin/env python3

import json
import glob
from os import path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Municipality
from models import District

# https://www.nsi.bg/nrnm/ekatte/archive

DATA_DIR = 'data/nsi.bg'


"""
  name      Char 25  - Наименование на общината
  abbrev    Char 5   - Идентификационен код на общината (3 букви + 2 цифри;
                       първите 3 букви са идентификационния код на областта;
                       следващите 2 цифри са пореден номер на общината в
                       областта).
"""

def _process_one_year(dir: str, unique_set: set, session: Session) -> list:

    a_json = None
    table_rows = list()

    file_path = path.join(dir, 'ek_obst.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        a_json = json.load(file)

    if not a_json:
        return table_rows

    for m in a_json[:-1]:
        m_abbrev = m['obshtina']
        if m_abbrev in unique_set:
            continue
        unique_set.add(m_abbrev)

        m_name = m['name'].lower().capitalize()
        d_abbrev = m_abbrev[:3]
        d_index = session.query(District.index).filter_by(abbrev=d_abbrev).one()[0]
        new_unit = Municipality(name=m_name,abbrev=m_abbrev, district_index=d_index)
        table_rows.append(new_unit)

    return table_rows


def _load(dir_name: str, session: Session):

    unique_set = set()
    rows = list()

    for dir in glob.iglob(f'{dir_name}/*'):
        one = _process_one_year(dir, unique_set, session)
        rows.extend(one)

    return rows

if __name__ == "__main__":
    engine = create_engine("postgresql://localhost/infobg")

    with Session(engine) as session:
        rows = _load(DATA_DIR, session)
        if not rows:
            sys.exit(0)
        session.add_all(rows)
        session.commit()
        row = session.query(Municipality).filter_by(abbrev='BGS01').first()
        print(row)