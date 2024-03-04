from collections import namedtuple
import logging
from typing import List

from shapely import strtree

from resto.census_area import CensusArea
from resto.voronoi import VorRegion

PopRegion = namedtuple('PopRegion', ['tag', 'poly', 'pop', 'n_ca'])

def overlap_pop(region: VorRegion, census_area: CensusArea):
    overlap = region.poly.intersection(census_area.poly)
    pct = overlap.area / census_area.poly.area

    return round(pct * census_area.pop)

def compute_overlaps2(census_areas: List[CensusArea], vor_regions: List[VorRegion]):
    results: List[PopRegion] = []
    cas_by_id = {ca.id: ca for ca in census_areas}
    remaining_cas = {ca.id for ca in census_areas}

    logging.info('compute overlaps: census_areas=%d vor_regions=%d', len(census_areas), len(vor_regions))

    for (ix, region) in enumerate(vor_regions):
        if ix % 10 == 0:
            logging.info("%d / %d cas_left=%d", ix, len(vor_regions), len(remaining_cas))

        reg_pop = reg_n = 0
        covered_cas = set()
        for ca_id in remaining_cas:
            ca = cas_by_id[ca_id]
            if not region.poly.intersects(ca.poly):
                continue
            if region.poly.covers(ca.poly):
                covered_cas.add(ca.id)

            reg_n += 1
            reg_pop += overlap_pop(region, ca)
       
        results += [PopRegion(region.tag, region.poly, reg_pop, reg_n)]
        remaining_cas -= covered_cas

    return results

def compute_overlaps_strtree(census_areas: List[CensusArea], vor_regions: List[VorRegion]):
    logging.info('compute overlaps: census_areas=%d vor_regions=%d', len(census_areas), len(vor_regions))
    results: List[PopRegion] = []
    tree = strtree.STRtree([ca.poly for ca in census_areas])
    for (ix, region) in enumerate(vor_regions):
        reg_pop = reg_n = 0

        q_result = tree.query(region.poly)
        cas_to_check = [census_areas[i] for i in q_result]
        for ca in cas_to_check:
            pop = overlap_pop(region, ca)
            reg_n += int(pop > 0)
            reg_pop += pop
        results += [PopRegion(region.tag, region.poly, reg_pop, reg_n)]

    return results

class OverlapsCalc:
    def __init__(self, census_areas: List[CensusArea], vor_regions: List[VorRegion]) -> None:
        self.census_areas = census_areas
        self.vor_regions = vor_regions
