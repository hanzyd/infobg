#!/usr/bin/env python3

# grao.bg

import json
import glob
import sys
from os import path

from districts import Districts
from locations import Locations
from municipalities import Municipalities

DATA_DIR = 'data/grao.bg'
CENSUS = 'json/census.json'


RENAMED = [('марикостеново', 'марикостиново'),
           ('палатник', 'палатик'),
           ('вълчидол', 'вълчи дол'),
           ('мосомищa', 'мосомище'),
           ('мусомищa', 'мосомище'),
           ('мусомища', 'мосомище'),
           ('санстефано', 'сан-стефано'),
           ('екзарх-антимово', 'екзарх антимово'),
           ('добрич-град', 'добрич'),
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
           ('фелдфебел-дянково', 'фелдфебел денково'),
           ('захари-стояново', 'захари стояново'),
           ('уручовци', 'уручевци'),
           ('поручик-кърджиево', 'поручик кърджиево'),
           ('полковник-свещарово', 'полковник свещарово'),
           ('генерал-колево', 'генерал колево'),
           ('александър стамболи', 'александър стамболийски'),
           ('киселичево', 'киселчово'),
           ('иван-шишманово', 'иван шишманово'),
           ]



class Census():

    def __init__(self, code: str, mun_abbrev: str, _date: str, permanent: int, current: int):
        self.code = str(code)
        self.municipality = str(mun_abbrev)
        self.date = str(_date)
        self.permanent = int(permanent)
        self.current = int(current)

    def __str__(self):
        return f'{self.code} {self.date} {self.current}'

    def __repr__(self):
        return f'Преброяване <{self.code} {self.date} {self.permanent} {self.current}>'

    def __hash__(self):
        return hash((self.code, self.date, self.municipality))

    def __eq__(self, other):
        if isinstance(other, Census):
            equal = self.code == other.code and self.date == other.date and \
                self.municipality == other.municipality

            if equal and self.permanent != other.permanent:
                print(f'Селище: {self.code} дата: {self.date} разлика в постояннте жители {self.permanent} != {other.permanent}')

            if equal and self.current != other.current:
                print(f'Селище: {self.code} дата: {self.date} разлика в настоящите жители {self.current} != {other.current}')

            return equal

        return NotImplemented


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return {
            'code': obj.code,
            'municipality': obj.municipality,
            'date': obj.date,
            'permanent': obj.permanent,
            'current': obj.current,
        }


def _name_check(name: str) -> str:
    for tup in RENAMED:
        if name == tup[0]:
            return tup[1]

    return name



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


def _process_one_year(file_name: str, locations: Locations, munis: Municipalities, dists: Districts, strict=False) -> list:

    lines = _cleanup_lines(file_name)

    no_code = set()
    population = []

    dist_abbrev = None
    mun_abbrev = None
    date_str = None

    for num, line in enumerate(lines):

        line = line.lower().strip()

        if 'дата' in line:
            tokens = line.split()
            if 'с.водата' != tokens[1]:
                date_str = tokens[1]

        if 'таблица на населението' in line:
            dist_abbrev = None
            mun_abbrev = None

        if 'всичко за общината'.lower() in line:
            dist_abbrev = None
            mun_abbrev = None
            date_str = None

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

            d_index = line.index('област')
            m_index = line.index('община')

            dist_name = line[d_index + len('област'):m_index].strip()
            mun_name = line[m_index + len('община'):].strip()

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

        if not date_str:
            print(f'{file_name}:{num} липсва дата')
            continue

        dist_abbrev = dists.find_abbrev(dist_name)
        if not dist_abbrev:
            print(f'{file_name}:{num} Област: "{dist_name}" без псевдоним')
            sys.exit(1)

        mun_abbrev = munis.find_abbrev(mun_name)
        if not mun_abbrev:
            print(f'{file_name}:{num} Община: "{mun_name}" без псевдоним')
            sys.exit(1)

        tokens = [t.strip() for t in tokens]
        town_name = tokens[0].removeprefix('с.').removeprefix('гр.').strip()
        town_name = _name_check(town_name)

        if 0 == int(tokens[1]) or 0 == int(tokens[2]) or 0 == int(tokens[3])  or \
                0 == int(tokens[5]) or 0 == int(tokens[6]) or 0 == int(tokens[7]):
            continue

        permanent = int(tokens[1])
        current = int(tokens[5])

        town_code = locations.find_code(town_name, dist_abbrev, mun_abbrev)
        if not town_code:
            if strict:
                no_code.add((dist_name, mun_name, town_name))
            continue

        census = Census(town_code, mun_abbrev, date_str, permanent, current)

        population.append(census)
        pass

    for no in no_code:
        print(f'{no[0]} {no[1]} {no[2]}')

    return population


def _load():

    if path.isfile(CENSUS):
        try:
            with open(CENSUS, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            pass

    dir_name = DATA_DIR

    ek_dist = Districts()
    ek_units = Locations()
    ek_mun = Municipalities()

    population = []

    file_names = [name for name in glob.iglob(f'{dir_name}/tadr*')]
    file_names.sort(reverse=True)

    strict = True
    for file_name in file_names:
        one = _process_one_year(file_name, ek_units, ek_mun, ek_dist, strict)
        strict = False
        population.extend(one)

    return population


class Censuses():
    def __init__(self):
        self.nodes = _load()

    def __iter__(self):
        for node in self.nodes:
            yield node

    def toJSON(self):
        with open(CENSUS, 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.nodes, indent=4, cls=Encoder))


if __name__ == "__main__":
    nodes = Censuses()
    nodes.toJSON()


