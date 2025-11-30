#!/usr/bin/env python3

import json
import sys

# https://ri.mon.bg/active-institutions
# https://nvoresults.com/index.html
# https://www.nsi.bg/nrnm/ekatte/archive
# https://www.nsi.bg/nrnm/ekatte/zip/download?files_type=json


def main(file_name):

    with open(file_name, 'r', encoding='UTF-8') as file:
        data = json.load(file)
        print(json.dumps(data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
   main(sys.argv[1])