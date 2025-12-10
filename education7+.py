#!/usr/bin/env python3

from os import path
import csv
import sys
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Municipality, Moment, Education


DATA_DIR = 'data/infostat.nsi.bg'

IN_FILE = 'ОБРАЗОВАНИЕ 7+.csv'


def _load(session: Session):

    rows = list()

    file_path = path.join(DATA_DIR, IN_FILE)
    with open(file_path, newline='') as csv_file:
        spam = csv.reader(csv_file, delimiter=';')

        next(spam)
        tokens = next(spam)
        next(spam)

        date_indexes = []
        for t in tokens:
            if t:
                c_date = date(int(t), 1, 1)
                d_index = Moment.insert_date(c_date, session)
            else:
                d_index = None

            date_indexes.append(d_index)

        for row in spam:
            m_name = row[0].lower().capitalize()

            municipality = session.query(Municipality).filter_by(name=m_name).first()
            if not municipality:
                print(f'Не намирам община {m_name}')
                continue

            for offs in [1, 7]:

                d_index = date_indexes[offs]

                try:
                    total = int(row[offs + 0])
                except ValueError:
                    continue

                try:
                    university = int(row[offs + 1])
                except ValueError:
                    university = 0

                try:
                    secondary = int(row[offs + 2])
                except ValueError:
                    secondary = 0

                try:
                    primary = int(row[offs + 3])
                except ValueError:
                    primary = 0

                try:
                    elementary = int(row[offs + 4])
                except ValueError:
                    elementary = 0

                try:
                    none = int(row[offs + 5])
                except ValueError:
                    none = 0

                new_node = Education(municipality.index, d_index, total,
                                     university, secondary, primary,
                                     elementary, none)
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

        rows = session.query(Education).all()
        for r in rows:
            name = session.query(Municipality.name).filter_by(index=r.municipality_index).first()
            print(f'Община {name[0]:25} {r}')
