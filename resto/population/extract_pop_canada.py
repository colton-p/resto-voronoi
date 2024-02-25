import csv

import resto.population.paths as paths

def extract_pop():
    return extract_metric('1', 'Population, 2021')


def extract_med_income():
    return extract_metric('113', 'Median total income in 2020 among recipients ($)')


def extract_metric(char_id, char_name):
    fname = paths.Canada.data_path()
    check_fname = paths.Canada.start_row_path()

    seen_lines = set()
    check_lines = {}
    with open(check_fname, 'r', encoding='latin1') as csvfile:
        reader = csv.DictReader(csvfile)
        check_lines = {row['Geo Code']: int(
            row['Line Number']) for row in reader}

    with open(fname, 'r', encoding='latin1') as csvfile:
        reader = csv.DictReader(csvfile)
        writer = csv.writer(open(paths.Canada.population_path(), 'w', encoding='utf8'))

        headers = ['DGUID', 'ALT_GEO_CODE',
                   'GEO_LEVEL', 'GEO_NAME', 'C1_COUNT_TOTAL']
        writer.writerow(headers)

        for (ix, row) in enumerate(reader):
            if row['CHARACTERISTIC_ID'] != char_id:
                continue
            assert row['CHARACTERISTIC_NAME'].strip(
            ) == char_name, row['CHARACTERISTIC_NAME']
            assert check_lines[row['DGUID']] == ix - int(char_id) + 3

            if row['GEO_LEVEL'] == 'Province':
                print(row['GEO_NAME'], len(seen_lines))

            seen_lines.add(row['DGUID'])
            out_row = tuple(row[k] for k in headers)

            writer.writerow(out_row)

    assert set(check_lines) == seen_lines


if __name__ == "__main__":
    extract_pop()
