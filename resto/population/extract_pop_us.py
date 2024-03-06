import csv

import resto.population.paths as paths
from resto.states import USA_50

def pops_for_state(state):
    header_name = paths.US.header_path(state)
    table_name = paths.US.table_path(state)

    ids = {}
    with open(header_name, 'r', encoding='latin1') as f:
        for line in f:
            line = line.split('|')
            if line[-3] == 'BG' and line[2] == '150':
                record_id = line[7]
                geo_id = line[9]
                ids[record_id] = geo_id

    total_pop = 0
    with open(table_name, 'r', encoding='utf8') as f:
        for (ix, line) in enumerate(f):
            line = line.split('|')
            if ix == 0:
                expcted_pop = int(line[5])
            record_id = line[4]
            if record_id in ids:
                geo_id = ids[record_id]
                pop = int(line[5])
                yield(geo_id, pop)
                total_pop += pop
    assert total_pop == expcted_pop
    print(f'{state} blocks={len(ids)} pop={total_pop}')


def write_pops(state):
    with open(paths.US.population_path(state), 'w', encoding='utf8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['geoid', 'population'])
        writer.writerows(pops_for_state(state))


if __name__ == "__main__":
    for st in USA_50:
        write_pops(st)
