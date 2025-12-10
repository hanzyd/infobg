#!/usr/bin/env python3

from os import path
import csv
import sys
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import MotherTongue, Municipality, Moment


DATA_DIR = 'data/infostat.nsi.bg'

IN_FILE = 'МАЙЧИН ЕЗИК.csv'



def _load(session: Session):

    rows = list()

    file_path = path.join(DATA_DIR, IN_FILE)
    with open(file_path, newline='') as csv_file:
        spam = csv.reader(csv_file, delimiter=';')

        next(spam)
        tokens = next(spam)
        next(spam)

        census_date = date(2021, 1, 1)
        for t in tokens:
            if t:
                census_date = date(int(t), 1, 1)
                break

        d_index = Moment.insert_date(census_date, session)

        for row in spam:
            abbrev_and_name = row[0].split(' ', 1)

            abbrev = str(abbrev_and_name[0])
            if len(abbrev) != 5:
                continue

            name = str(abbrev_and_name[1]).lower().capitalize()

            municipality = session.query(Municipality).filter_by(abbrev=abbrev).first()
            if not municipality:
                print(f'Не намирам община {name} с абреатура {abbrev}')
                continue

            if municipality.name != name:
                print(f'Името на общината {name} не съвпада {municipality.name}')
                continue

            total = int(row[1])

            try:
                bul = int(row[2])
            except ValueError:
                bul = 0

            try:
                tur = int(row[3])
            except ValueError:
                tur = 0

            try:
                roma = int(row[4])
            except ValueError:
                roma = 0

            try:
                other = int(row[5])
            except ValueError:
                other = 0

            try:
                cant_decide = int(row[6])
            except ValueError:
                cant_decide = 0

            try:
                dont_answer = int(row[7])
            except ValueError:
                dont_answer = 0

            try:
                not_shown = int(row[8])
            except ValueError:
                not_shown = 0

            new_node = MotherTongue(municipality.index, d_index, total, bul, tur,
                                    roma, other, cant_decide, dont_answer,
                                    not_shown)
            rows.append(new_node)

    return rows


if __name__ == "__main__":

    engine = create_engine("postgresql://localhost/infobg")

    with Session(engine) as session:

        rows = _load(session)
        if not rows:
            sys.exit(0)

        session.add_all(rows)
        session.commit()

        rows = session.query(MotherTongue).all()
        for r in rows:
            name = session.query(Municipality.name).filter_by(index=r.municipality_index).first()
            print(f'Община {name[0]:25} {r}')
