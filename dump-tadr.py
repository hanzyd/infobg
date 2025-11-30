#!/usr/bin/env python3

# grao.bg

import csv
import sys

def main(file_name):

    cvs_name = file_name + '.csv'
    with open(file_name, encoding='windows-1251') as txt_file:
        with open(cvs_name, 'w', encoding='UTF-8') as csv_file:
            writer = csv.writer(csv_file)
            for line in txt_file.readlines():
                if line.startswith('|ГР') or line.startswith('|С'):
                    # Remove start and end '|' character
                    line = line.strip()[1:-1]
                    split = line.split('|')
                elif line.startswith('| ГР') or line.startswith('| С'):
                    # Remove start and end '|' character
                    line = line.strip()[1:-1]
                    split = line.split('|')
                elif line.startswith('! ГР') or line.startswith('! С'):
                    # Remove start and end '|' character
                    line = line.strip()[1:-1]
                    split = line.split('!')
                else:
                    continue

                columns = [s.strip() for s in split]
                writer.writerow(columns)

if __name__ == "__main__":
   main(sys.argv[1])