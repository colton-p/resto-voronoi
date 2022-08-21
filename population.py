import csv

STATES = {'ak', 'al', 'ar', 'az', 'ca', 'co', 'ct', 'de', 'fl', 'ga', 'hi', 'ia', 'id', 'il', 'in', 'ks', 'ky', 'la', 'ma', 'md', 'me', 'mi', 'mn', 'mo',
          'ms', 'mt', 'nc', 'nd', 'ne', 'nh', 'nj', 'nm', 'nv', 'ny', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'va', 'vt', 'wa', 'wi', 'wv', 'wy'}


def pop_dict(state):
    if state in STATES:
        with open(f'census/us/{state}_pop.csv', 'r') as csvfile:
            return {geo_id: int(pop) for (geo_id, pop) in csv.reader(csvfile)}

    population = {}
    with open('census/canada/full.csv', 'r') as csvfile:
        for line in csv.reader(csvfile):
            geo_id = line[1]
            if geo_id == 'ALT_GEO_CODE':
                continue
            pop = int(line[-1] or 0)
            population[geo_id] = pop

    return population
