import itertools
from collections import Counter
import folium
import argparse
from functools import cached_property

from census_areas import CensusAreas

from shapely.geometry import Polygon, MultiPolygon
from voronoi import Vor

COLOR = {
    'tims': 'crimson',
    'mcds': 'yellow',
    'sbux': 'green',
}


def plot_points(m, points_dict):
    for (tag, points) in points_dict.items():
        for pt in points:
            folium.CircleMarker(
                location=pt,
                color=COLOR[tag],
                radius=5,
                fill=False
            ).add_to(m)


def plot_region(m: folium.Map, tag, region: Polygon, desc=''):
    folium.Polygon(
        region.exterior.coords,
        color=COLOR[tag],
        # fill_color='white',
        radius=5,
        fill=True,
        tooltip=desc,
        # fill_opacity=0,
    ).add_to(m)


def plot_overlap(tag, overlap):
    if isinstance(overlap, MultiPolygon):
        polys = list(overlap.geoms)
    else:
        polys = [overlap]
    for poly in polys:
        folium.Polygon(
            poly.exterior.coords,
            color=COLOR[tag],
            radius=5,
            fill=True,
            weight=0,
        ).add_to(m)


def overlap_pop(region, da):
    overlap = region.intersection(da.poly)
    pct = overlap.area / da.poly.area
    pop = round(pct*da.pop)

    return pop


def compute_overlaps2(regions, das):
    results = []

    remaining_das = {da.id: da for da in das}

    n_regions = len(regions)
    for (ix, (tag, region)) in enumerate(regions):
        if ix % 100 == 0:
            print(f'\t {ix}/{n_regions} das={len(remaining_das)}')

        reg_pop = reg_n = 0
        covered_das = set()
        for da in remaining_das.values():
            if not region.intersects(da.poly):
                continue

            if region.covers(da.poly):
                covered_das.add(da.id)

            pop = overlap_pop(region, da)
            reg_n += 1
            reg_pop += pop

        results += [
            (tag, region, reg_pop, reg_n)
        ]

        remaining_das = {
            k: v for (k, v) in remaining_das.items() if k not in covered_das}

    print('\t', 'das:', len(das), '-->', len(remaining_das))
    return results


class Overlaps:
    @classmethod
    def for_states(cls, states):
        das = itertools.chain(
            *(CensusAreas.for_state(state).areas() for state in states))
        return cls(list(das))

    @classmethod
    def for_state(cls, state):
        das = list(CensusAreas.for_state(state).areas())

        return cls(das)

    def __init__(self, das):
        self.das = das

    @staticmethod
    def totals_dict(region_totals):
        c = Counter()
        for (tag, _region, pop, _count) in region_totals:
            c[tag] += pop

        return c

    @cached_property
    def hull(self):
        all_das = MultiPolygon(da.poly for da in self.das)
        return all_das.convex_hull

    @cached_property
    def V(self):
        return Vor.within(self.hull)

    @cached_property
    def points(self):
        return self.V.points

    @cached_property
    def regions(self):
        return self.V.clipped_regions(self.hull, finite=True)

    def region_totals(self):
        return compute_overlaps2(self.regions, self.das)


def totals(state):
    O = Overlaps.for_state(state)

    return O.totals_dict(O.region_totals())


def main(args):
    O = Overlaps.for_states(args.state.split(','))

    m = folium.Map(location=O.hull.representative_point().coords[0])

    if args.plot_das:
        for da in O.das:
            folium.Polygon(da.poly.exterior.coords, color='blue',
                           fill=False, weight=1, dash_array='4', tooltip=f'{da.id} {da.pop}').add_to(m)

    print('points:', ' '.join(f'{t}={len(p)}' for (t, p) in O.points.items()))
    plot_points(m, O.points)

    print(
        f'regions:', f'shapes={len(O.regions)} points={sum(len(r[1].exterior.coords) for r in O.regions)}'
    )

    region_totals = O.region_totals()
    for (tag, region, reg_pop, reg_n) in region_totals:
        plot_region(m, tag, region,
                    f'tag={tag} pop={reg_pop} n={reg_n}')

    n_overlaps = sum(x[3] for x in region_totals)
    totals = O.totals_dict(region_totals)
    print('overlaps:', n_overlaps)

    print(f'pop={sum(totals.values())} das_pop={sum(da.pop for da in O.das)}')
    print(totals)

    c = Counter()
    for (tag, _region, pop, count) in region_totals:
        c[tag] += pop

    for t in c:
        print(t, c[t])

    m.save('overlap.html')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('state')
    parser.add_argument('--plot_das', action='store_true')
    main(parser.parse_args())
