from functools import cached_property

from locator_sweep.sweeper import circle
from shapely.geometry import Polygon
from shapely.ops import unary_union

from resto.borders import Borders
from resto.census_area import CensusArea
from resto import locations as location_loader
from resto.overlap import compute_overlaps_strtree
from resto.voronoi import VorRegion

class PopulationCurve():
    @staticmethod
    def for_state(state, tag):
        bounds = Borders.for_state(state)
        locations = location_loader.within([tag], bounds.multipoly())
        census_areas = list(CensusArea.for_state(state))
        return PopulationCurve(locations, census_areas)

    def __init__(self, locations, census_areas) -> None:
        self.locations = locations
        self.census_areas = census_areas

    @cached_property
    def total_pop(self):
        return sum(area.pop for area in self.census_areas)

    def distance(self, dist):
        covers = [
            Polygon(circle(loc.point, 1000 * dist))
            for loc in self.locations
        ]
        covered = unary_union(covers)

        if isinstance(covered, Polygon):
            covered_polys = [covered]
        else:
            covered_polys = covered.geoms

        result = compute_overlaps_strtree(
            self.census_areas,
            [VorRegion('', poly) for poly in covered_polys],
        )

        covered_pop = sum(x.pop for x in result)
        pct_covered = covered_pop / self.total_pop

        return [pct_covered, covered_pop, len(covered_polys)]
