import csv
import sys


def extract_pop(folder):
    fname = f'data/{folder}_eng_CSV/{folder}_English_CSV_data.csv'
    check_fname = f'data/{folder}_eng_CSV/{folder}_Geo_starting_row.CSV'

    seen_lines = set()
    check_lines = {}
    with open(check_fname, 'r', encoding='latin1') as csvfile:
        reader = csv.DictReader(csvfile)
        check_lines = {row['Geo Code']: int(
            row['Line Number']) for row in reader}

    with open(fname, 'r', encoding='latin1') as csvfile:
        reader = csv.DictReader(csvfile)
        writer = csv.writer(sys.stdout)

        headers = ['DGUID', 'ALT_GEO_CODE',
                   'GEO_LEVEL', 'GEO_NAME', 'C1_COUNT_TOTAL']
        writer.writerow(headers)

        for (ix, row) in enumerate(reader):
            if row['CHARACTERISTIC_ID'] != '1':
                continue
            assert row['CHARACTERISTIC_NAME'] == 'Population, 2021'
            assert check_lines[row['DGUID']] == ix + 2

            seen_lines.add(row['DGUID'])
            out_row = tuple(row[k] for k in headers)

            writer.writerow(out_row)

    assert set(check_lines) == seen_lines


if __name__ == "__main__":
    extract_pop(sys.argv[1])
