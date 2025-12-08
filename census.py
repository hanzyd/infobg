#!/usr/bin/env python3

# grao.bg

import json
import glob
import sys
from os import path
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Census, Moment, District, Municipality, Settlement


DATA_DIR = 'data/grao.bg'


RENAMED = [ ('марикостеново', 'марикостиново'),
    ('палатник', 'палатик'),
    ('вълчидол', 'вълчи дол'),
    ('мосомиша', 'мосомище'),
    ('мусомиша', 'мосомище'),
    ('мусомишо', 'мосомище'),
    ('санстефано', 'сан-стефано'),
    ('екзарх-антимово', 'екзарх антимово'),
    ('бобовдол', 'бобов дол'),
    ('в.търново', 'велико търново'),
    ('генерал-тошево', 'генерал тошево'),
    ('георги-дамяново', 'георги дамяново'),
    ('софийска', 'софия'),
    ('никола-козлево', 'никола козлево'),
    ('добричка', 'добрич-селска'),
    ('генерал тошово', 'генерал тошево'),
    ('стефан-караджово', 'стефан караджово'),
    ('панайот-волово', 'панайот волово'),
    ('капитан петко войво', 'капитан петко войвода'),
    ('георги-добрево', 'георги добрево'),
    ('колю-мариново', 'колю мариново'),
    ('полковник серафимов', 'полковник серафимово'),
    ('полковник ламбринов', 'полковник ламбриново'),
    ('полско косово', 'полско косово'),
    ('генерал-кантарджиев', 'генерал кантарджиево'),
    ('любен-каравелово', 'любен каравелово'),
    ('поликрайще', 'поликраище'),
    ('ефрейтор-бакалово', 'ефрейтор бакалово'),
    ('генерал-киселово', 'генерал киселово'),
    ('фелдфебел-дяинково', 'фелдфебел денково'),
    ('захари-стояново', 'захари стояново'),
    ('уручовци', 'уручевоци'),
    ('поручик-кърджиево', 'поручик кърджиево'),
    ('полковник-свещарово', 'полковник свещарово'),
    ('генерал-колево', 'генерал колево'),
    ('александър стамболи', 'александър стамболийски'),
    ('киселичево', 'киселчово'),
    ('иван-шишманово', 'иван шишманово'),
    ('славейино', 'славейково'),
    ('равнина', 'ровино'),
    ('полковник-серафимов', 'полковник серафимово'),
    ('орешица', 'орешец'),
    ('кокорково', 'кокорово'),
    ('вълчадол', 'вълчан дол'),
    ('графитово', 'графитово'),
    ('професор-иширково', 'професор иширково'),
    ('полковник-ламбринов', 'полковник ламбриново'),
    ('полковник-чолаково', 'полковник чолаково'),
    ('полковник-таслаково', 'полковник таслаково'),
]


def _name_check(name: str) -> str:
    for tup in RENAMED:
        if name == tup[0]:
            name = tup[1]

    return name.lower().capitalize()



def _cleanup_lines(file_name: str):

    old_lines = []
    with open(file_name, encoding='windows-1251') as txt_file:
        try:
            num = 0
            for num, line in enumerate(txt_file):
                old_lines.append(line)
        except UnicodeDecodeError as err:
            print(f'{file_name}:{num}:{err}')
            return old_lines

    new_lines = []
    for num, line in enumerate(old_lines):

        if 'ЬО' in line:
            new_lines.append(line)
            continue

        if 'Ь' in line:
            line = line.replace('Ь', 'Ъ')

        new_lines.append(line)

    return new_lines


def _find_date_index(exam_date: date, session: Session) -> int:

    d_index = session.query(Moment.index).filter_by(date=exam_date).first()
    if not d_index:
        m = Moment(date=exam_date)
        session.add(m)
        session.commit()
        d_index = session.query(Moment.index).filter_by(date=exam_date).first()

    return d_index[0]


def _process_one_year(file_name: str, session: Session, strict=False) -> list:

    lines = _cleanup_lines(file_name)

    population = []
    dist_name = None
    mun_name = None
    census_date = None
    for num, line in enumerate(lines):

        line = line.lower().strip()

        if 'дата' in line:
            tokens = line.split()
            if 'водата' in line or 'пирамидата' in line:
                pass
            else:
                d_str = tokens[1]
                try:
                    census_date = date.strptime(d_str, "%d.%m.%Y")
                    dist_name = None
                    mun_name = None
                except ValueError:
                    pass

        if 'всичко за общината'.lower() in line:
            census_date = None

        # 1998
        if 'област:' in line:
            line = line.removesuffix('Т А Б Л И Ц А'.lower()).strip()
            tokens = line.split(':')
            tokens = [t.strip() for t in tokens]
            dist_name = _name_check(tokens[1])

        # 1998
        if 'община:' in line:
            line = line.removesuffix('на населението по постоянен и настоящ адрес').strip()
            line = line.removesuffix('на населението по адрес и местожителство').strip()
            tokens = line.split(':')
            tokens = [t.strip() for t in tokens]
            mun_name = _name_check(tokens[1])

        if 'област' in line and 'община' in line:

            d_offs = line.index('област')
            m_offs = line.index('община')

            dist_name = line[d_offs + len('област'):m_offs].strip()
            mun_name = line[m_offs + len('община'):].strip()

            dist_name = _name_check(dist_name)
            mun_name = _name_check(mun_name)

        if line.startswith('|гр') or line.startswith('|с'):
            # Remove start and end '|' character
            line = line.strip()[1:-1]
            tokens = line.split('|')
        elif line.startswith('| гр') or line.startswith('| с'):
            # Remove start and end '|' character
            line = line.strip()[1:-1]
            tokens = line.split('|')
        elif line.startswith('! гр') or line.startswith('! с'):
            # Remove start and end '|' character
            line = line.strip()[1:-1]
            tokens = line.split('!')
        else:
            continue

        if not census_date:
            print(f'{file_name}:{num} липсва дата')
            continue

        time_index = _find_date_index(census_date, session)

        tokens = [t.strip() for t in tokens]
        town_name = tokens[0].removeprefix('с.').removeprefix('гр.').strip()
        town_name = _name_check(town_name)

        # Конвертиран код с UTF-8 стрингове
        if mun_name == 'Столична' and dist_name == 'София':
            dist_name = 'София (столица)'
        if mun_name == 'Столична' and dist_name == 'София':
            dist_name = 'София (столица)'
        elif mun_name == 'Добрич' and dist_name == 'Добрич':
            mun_name = 'Добрич-селска'
        elif mun_name == 'Добрич-град' and dist_name == 'Добрич':
            mun_name = 'Добрич'
        elif mun_name == 'Лъки' and dist_name == 'Смолян':
            dist_name = 'Пловдив'
        elif town_name == 'Топчии' and dist_name == 'Русе' and mun_name == 'Ветово':
            dist_name = 'Разград'
            mun_name = 'Разград'
        elif mun_name == 'Кнежа' and dist_name == 'Враца':
            dist_name = 'Плевен'
        elif town_name == 'Чубрика' and not dist_name and not mun_name:
            mun_name = 'Ардино'
            dist_name = 'Кърджали'
        elif town_name == 'Ябълковец' and not dist_name and not mun_name:
            mun_name = 'Ардино'
            dist_name = 'Кърджали'

        d_index = session.query(District.index).filter_by(name=dist_name).first()
        if not d_index:
            print(f'{file_name}:{num} Не намирам област {dist_name} община {mun_name} град {town_name}')
            continue

        m_index = session.query(Municipality.index).filter_by(district_index=d_index[0]).filter_by(name=mun_name).first()
        if not m_index:
            print(f'{file_name}:{num} Не намирам община {mun_name} в област {dist_name}')
            continue

        if 0 == int(tokens[1]) or 0 == int(tokens[2]) or 0 == int(tokens[3])  or \
                0 == int(tokens[5]) or 0 == int(tokens[6]) or 0 == int(tokens[7]):
            continue

        permanent = int(tokens[1])
        current = int(tokens[5])

        s_index = session.query(Settlement.index).filter_by(name=town_name).filter_by(municipality_index=m_index[0]).first()
        if not s_index:
            print(f'{file_name}:{num:4} Не намирам селище {town_name} в област {dist_name} в община {mun_name}')
            continue

        census = Census(settlement_index=s_index[0], municipality_index=m_index[0],
                        date_index=time_index, permanent=permanent, current=current)

        population.append(census)
        pass

    return population


def _load(session: Session) -> list:

    dir_name = DATA_DIR

    population = []

    file_names = [name for name in glob.iglob(f'{dir_name}/tadr*20*')]
    file_names.sort(reverse=True)

    strict = True
    for file_name in file_names:
        one = _process_one_year(file_name, session, strict)
        strict = False
        population.extend(one)

    return population


if __name__ == "__main__":

    engine = create_engine('sqlite:///models.sqlite')

    Census.__table__.drop(engine)
    Census.__table__.create(engine)

    with Session(engine) as session:

        rows = _load(session)
        if not rows:
            sys.exit(0)

        session.add_all(rows)
        session.commit()


