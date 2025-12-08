#!/usr/bin/env python3

import json
import glob
from os import path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Municipality
from models import SettlementAltitude
from models import SettlementType
from models import Settlement
from models import MotherTongue


# https://www.nsi.bg/nrnm/ekatte/archive

DATA_DIR = 'data/nsi.bg'


"""
  code     Char 5   - Идентификационен код на териториалната единица.
                        (ЕКАТТЕ-код). 4+1 цифри. Последната цифра е
                        контролна, изчислена по приетия в НСИ алгоритъм
                        за изчисляване на контролна цифра по модул 11.
                        Съвпада изцяло с кода по ЕКНМ на населеното място
                        от предишния класификатор!

  name       Char 25  - Наименование на териториалната единица.

  kind       Char 1   - Код на типа на териториалната единица:
                        1  "гр. "  -  град
                        3  "с.  "  -  село
                        7  "ман."  -  манастир

  altitude   Char 1   - Надморска височина
                        Код        Групи (в метри)
                        1          до 49 вкл.
                        2          50 - 99 вкл.
                        3          100 - 199 вкл.
                        4          200 - 299 вкл.
                        5          300 - 499 вкл.
                        6          500 - 699 вкл.
                        7          700 - 999 вкл.
                        8          1000 и повече

  municipality    Char 5   - Идентификационен код на общината, в чийто състав влиза
                        териториалната единица (5 знака; първите 3 букви са
                        кода на областта; следващите 2 цифри са пореден номер
                        на общината в областта).
                        Кодирането (декодирането) се извършват с помощта на
                        файл EK_OBST

  district     Char 3   - Идентификационен код на областта, към която принадлежи
                        териториалната единица (3 букви).
                        Кодирането (декодирането) се извършват c помощта на
                        файл EK_OBL.

"""


def _process_one_year(dir: str, unique_filter: set, session: Session) -> list:

    a_json = None
    table_rows = list()

    file_path = path.join(dir, 'ek_atte.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        a_json = json.load(file)

    if not a_json:
        return table_rows

    for node in a_json[:-1]:

        s_code = str(node['ekatte'])
        if s_code in unique_filter:
            continue
        unique_filter.add(s_code)
        s_name = str(node['name']).lower().capitalize()
        s_kind = int(node['kind'])
        s_altitude = int(node['altitude'])
        m_abbrev = str(node['obshtina'])

        m_index = session.query(Municipality.index).filter_by(abbrev=m_abbrev).one()[0]

        new_node = Settlement(code=s_code, name=s_name,
                               municipality_index=m_index,
                               kind_code=s_kind, altitude_code=s_altitude)
        table_rows.append(new_node)

    return table_rows


def _load(dir_name: str, session: Session):

    unique_filter = set()
    rows = list()

    for dir in glob.iglob(f'{dir_name}/*'):
        one = _process_one_year(dir, unique_filter, session)
        rows.extend(one)

    return rows

if __name__ == "__main__":
    engine = create_engine("postgresql://localhost/infobg")

    with Session(engine) as session:

        e = [
            SettlementAltitude(code=1, label='до 49 вкл.'),
            SettlementAltitude(code=2, label='50 - 99 вкл.'),
            SettlementAltitude(code=3, label='100 - 199 вкл.'),
            SettlementAltitude(code=4, label='200 - 299 вкл.'),
            SettlementAltitude(code=5, label='300 - 499 вкл.'),
            SettlementAltitude(code=6, label='500 - 699 вкл.'),
            SettlementAltitude(code=7, label='700 - 999 вкл.'),
            SettlementAltitude(code=8, label='1000 и повече'),

            SettlementType(code=1, label='гр.'),
            SettlementType(code=3, label='с.'),
            SettlementType(code=7, label='ман.'),
        ]

        session.add_all(e)
        session.commit()

        rows = _load(DATA_DIR, session)
        if not rows:
            sys.exit(0)

        session.add_all(rows)
        session.commit()

        e = session.query(SettlementAltitude).filter_by(code=2).first()
        print(e)

        e = session.query(SettlementType).filter_by(label='с.').first()
        print(e)

        e = session.query(Settlement).filter_by(code='29129').first()
        print(e)

        e = session.query(Settlement).filter_by(
            name='\u0422\u0443\u0442\u0440\u0430\u043a\u0430\u043d').first()
        print(e)
