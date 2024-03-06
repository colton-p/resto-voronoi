import csv

from resto.population import paths
from resto.states import USA_50, USA_ALIASES


def pop_dict(state):
    population = {}
    if state in USA_50 or state in USA_ALIASES:
        states = USA_ALIASES.get(state, [state])
        for st in states:
            path = paths.US.population_path(st)
            with open(path, 'r') as csvfile:
                for (geo_id, pop) in csv.reader(csvfile):
                    if pop == 'population': continue
                    population[geo_id] = int(pop)

    path = paths.Canada.population_path()
    with open(path, 'r') as csvfile:
        for line in csv.reader(csvfile):
            geo_id = line[1]
            if geo_id == 'ALT_GEO_CODE':
                continue
            pop = int(line[-1] or 0)
            population[geo_id] = pop

    return population
