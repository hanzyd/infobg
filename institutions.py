#!/usr/bin/env python3

import json
import sys
from os import path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import InstitutionStatus
from models import InstitutionDetails
from models import InstitutionFinancing
from models import Institution
from models import Settlement
from models import Municipality
from models import District

from finance import guess_institution_financing
from details import guess_institution_details
from transform import guess_institution_status

MON_DIR = 'data/mon.bg'
REGISTER = 'public-register.json'

RES_DIR = 'data/nvoresults.com'
INTERNAL = 'matura_results.json'
EXTERNAL = 'results.json'
SCHOOLS = 'matura_schools.json'

# https://nvoresults.com/matura_schools.json


def _load_mon(unique_set: set, session: Session) -> list:

    rows = list()

    file_path = path.join(MON_DIR, REGISTER)
    with open(file_path, 'r', encoding='UTF-8') as file:
        try:
            register = json.load(file)['data']['publicInstitutions']
        except KeyError as err:
            print(f'{err}')
            sys.exit(1)

    for node in register:

        school_code = str(node['instid'])
        num_id = str(node['id'])

        if school_code != num_id:
            print(f'Разминаване в кода на институцията {school_code} != {num_id}')
            continue

        if school_code in unique_set:
            continue

        name = node['name']
        s_code = str(node['town']).zfill(5)
        s_index = session.query(Settlement.index).filter_by(code=s_code).first()
        if not s_index:
            print(f'Невалидно селище {s_code}: {name}')
            continue

        f_code = int(node['financialSchoolType'])
        f_index = session.query(InstitutionFinancing.code).filter_by(code=f_code).first()
        if not f_index:
            print(f'Невалиден финасов код {f_code}: {name}')
            continue

        d_code = int(node['detailedSchoolType'])
        d_index = session.query(InstitutionDetails.code).filter_by(code=d_code).first()
        if not d_index:
            print(f'Невалиден детайлен код {d_code}: {name}')
            continue

        t_code = int(node['transformType'])
        t_index = session.query(InstitutionStatus.code).filter_by(code=t_code).first()
        if not t_index:
            print(f'Невалиден код на състоянието {t_code}: {name}')
            continue

        new_unit = Institution(code=school_code, name=name, settlement_index=s_index[0],
                               financing_code=f_code, details_code=d_code,
                               status_code=t_code)

        rows.append(new_unit)
        unique_set.add(school_code)

    return rows


def _strip_location(location: str) -> str:

    location = location.lower()
    location = location.removeprefix('гр.')
    location = location.removeprefix('с.').strip()

    cap = location.capitalize()
    if 'София-област' == cap:
        cap = 'София'
    elif 'София-град' == cap:
        cap = 'София (столица)'

    return cap


def _load_nvo(unique_set: set, session: Session) -> list:

    rows = list()

    file_name = path.join(RES_DIR, SCHOOLS)
    with open(file_name, 'r', encoding='utf-8') as file:
        datum = json.load(file)

        for school_code in datum:

            if school_code in unique_set:
                continue

            school_name = datum[school_code]['data']['school']
            s_name = _strip_location(datum[school_code]['data']['city'])
            m_name = _strip_location(datum[school_code]['data']['obshtina'])
            d_name = _strip_location(datum[school_code]['data']['oblast'])

            d_index = session.query(District.index).filter_by(name=d_name).first()
            if not d_index:
                print(f'Невалидна област: {d_name}')
                continue

            m_index = session.query(Municipality.index).filter_by(name=m_name).first()
            if not m_index:
                print(f'Невалидна община в област {d_name}: {m_name}')
                continue

            s_index = session.query(Settlement.index).filter_by(name=s_name).filter_by(municipality_index=m_index[0]).first()
            if not s_index:
                print(f'Невалидна селище в област {d_name}, община {d_name}: {m_name}')
                continue

            f_code = guess_institution_financing(school_name)
            d_code = guess_institution_details(school_name)
            s_code = guess_institution_status(school_name)

            new_unit = Institution(code=school_code, name=school_name, settlement_index=s_index[0],
                                   financing_code=f_code, details_code=d_code,
                                   status_code=s_code)

            rows.append(new_unit)
            unique_set.add(school_code)

    file_name = path.join(RES_DIR, EXTERNAL)
    with open(file_name, 'r', encoding='utf-8') as file:
        datum = json.load(file)

        for school_code in datum:

            if school_code in unique_set:
                continue

            school_name = datum[school_code]['name']
            s_name = _strip_location(datum[school_code]['city'])
            m_name = _strip_location(datum[school_code]['municipality'])
            d_name = _strip_location(datum[school_code]['region'])

            d_index = session.query(District.index).filter_by(name=d_name).first()
            if not d_index:
                print(f'Невалидна област: {d_name}')
                continue

            m_index = session.query(Municipality.index).filter_by(name=m_name).first()
            if not m_index:
                print(f'Невалидна община в област {d_name}: {m_name}')
                continue

            s_index = session.query(Settlement.index).filter_by(name=s_name, municipality_index=m_index[0]).first()
            if not s_index:
                print(f'Невалидна селище в област {d_name}, община {d_name}: {m_name}')
                continue

            f_code = guess_institution_financing(school_name)
            d_code = guess_institution_details(school_name)
            s_code = guess_institution_status(school_name)

            new_unit = Institution(code=school_code, name=school_name, settlement_index=s_index[0],
                                   financing_code=f_code, details_code=d_code,
                                   status_code=s_code)

            rows.append(new_unit)
            unique_set.add(school_code)

    return rows


if __name__ == "__main__":
    engine = create_engine("postgresql://localhost/infobg")

    with Session(engine) as session:

        unique_set = set()
        rows = _load_mon(unique_set, session)
        rows.extend(_load_nvo(unique_set, session))
        if not rows:
            sys.exit(0)

        session.add_all(rows)
        session.commit()

        rows = session.query(Institution).filter_by(code='103503').all()
        for r in rows:
            print(r)

