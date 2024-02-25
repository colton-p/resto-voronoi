from functools import cached_property
from dataclasses import dataclass
import logging

from shapely.geometry import Polygon, box

from resto.shapes.loader import census_borders 
from resto.population.population import pop_dict as make_pop_dict

def _build_census_areas(state):
    n_shapes = 0
    n_parts = 0
    n_points = 0
    pop_map = make_pop_dict(state)
    for geo_id, polys in census_borders(state):
        n_shapes += 1

        total_pop = pop_map[geo_id]
        total_area = sum(p.area for p in polys)

        for (part_ix, poly) in enumerate(polys):
            pop = int(total_pop*poly.area / total_area)
            if pop > 0:
                n_parts += 1
                n_points += (len(poly.simplify(10**-2).exterior.coords) - 1)
                yield CensusArea(
                    id=f'{geo_id}-{part_ix}',
                    poly=poly,
                    pop=pop,
                )
    logging.info('%s: %d census areas; from shapes=%d points=%d', state, n_parts, n_shapes, n_points)


@dataclass(frozen=True)
class CensusArea:
    id: str
    poly: Polygon
    pop: int

    @staticmethod
    def for_state(state):
        return _build_census_areas(state)

    def points(self):
        return self.poly.exterior.coords

    @cached_property
    def box(self):
        return box(*self.poly.bounds)
