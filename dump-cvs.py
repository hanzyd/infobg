#!/usr/bin/env python3

# wget https://danybon.com/wp-content/uploads/2025/04/4-nvo-7.csv
# wget https://danybon.com/wp-content/uploads/2025/04/7-nvo-7.csv
# wget https://danybon.com/wp-content/uploads/2025/04/10-nvo-7.csv
# wget https://danybon.com/wp-content/uploads/2025/04/12-nvo-7.csv

import csv
import sys

def main(file_name):

    with open(file_name, newline='') as csv_file:
        spam_reader = csv.reader(csv_file)
        for row in spam_reader:
            print(', '.join(row))

if __name__ == "__main__":
   main(sys.argv[1])