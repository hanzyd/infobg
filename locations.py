#!/usr/bin/env python3

import json
import glob
from os import path

# https://www.nsi.bg/nrnm/ekatte/archive

DATA_DIR = 'data/nsi.bg'
OUT_FILE = 'json/locations.json'


class Location():
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

    def __init__(self, code: str, name: str, municipality: str, district: str, kind: int, altitude: int):
        self.code = str(code)
        self.name = str(name)
        self.municipality = str(municipality)
        self.kind = int(kind)
        self.altitude = int(altitude)

        if district != municipality[:-2]:
            print(f'Внимание: {name}: {municipality} != {district}')

    def __str__(self):
        return f'{self.code:5} {self.name:25} {self.municipality:5}'

    def __repr__(self):
        return f'Селище <{self.code:5} {self.name:25} {self.municipality:5} {self.kind} {self.altitude}>'

    def __hash__(self):
        return hash((self.code, self.name, self.municipality))

    def __eq__(self, other):
        if isinstance(other, Location):
            equal = self.code == other.code and \
                self.municipality == other.municipality

            if equal and self.name != other.name:
                print(f'Внимание: {self.code} община: {self.municipality} {self.name} != {other.name}')

            return equal

        return NotImplemented

    def district(self):
        return self.municipality[:-2]

    def location_name(locations: list, code: str) -> bool:

        for unit in locations:
            if unit.code == code:
                return True

        return False


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return {
            'code': obj.code,
            'name': obj.name,
            'municipality': obj.municipality,
            'kind': obj.kind,
            'altitude': obj.altitude
        }


def _process_one_year(dir) -> set:

    a_json = None
    a_list = list()
    a_set = set()

    file_path = path.join(dir, 'ek_atte.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        a_json = json.load(file)

    if not a_json:
        return a_set

    for node in a_json[:-1]:

        node_code = str(node['ekatte'])
        node_name = str(node['name'])
        node_kind = int(node['kind'])
        node_alt = int(node['altitude'])
        mun_name = str(node['obshtina'])
        dist_name = str(node['oblast'])

        new_node = Location(node_code, node_name, mun_name,
                            dist_name, node_kind, node_alt)

        a_list.append(new_node)
        a_set.add(new_node)

    if len(a_set) != len(a_list):
        print(f'Има повтарящи се селища във входния файл {file_path}')

    return a_set


def _load() -> set:

    if path.isfile(OUT_FILE):
        try:
            with open(OUT_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            pass

    dir_name = DATA_DIR

    nodes = set()
    for dir in glob.iglob(f'{dir_name}/*'):
        p = _process_one_year(dir)
        nodes.update(p)

    return nodes


class Locations():
    def __init__(self):
        self.nodes = _load()

    def __iter__(self):
        for node in self.nodes:
            yield node

    def find_code(self, name: str, dist_nick='', mun_nick='') -> str:
        small = name.lower()
        for m in self.nodes:
            if m.name.lower() == small:
                if mun_nick and m.municipality == mun_nick:
                    return m.code
                if dist_nick and m.municipality[:-2] == dist_nick:
                    return m.code
        return None

    def find_name(self, code: str) -> bool:
        for unit in self.nodes:
            if unit.code == code:
                return unit.name
        return None

    def toJSON(self):
        with open(OUT_FILE, 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.nodes, indent=4, cls=Encoder))


if __name__ == "__main__":
    nodes = Locations()
    nodes.toJSON()
