import argparse
from collections import Counter

from resto.borders import Borders
from resto.census_area import CensusArea
from resto.map import Map
from resto import locations as location_loader
from resto.overlap import compute_overlaps2, compute_overlaps_strtree
from resto.voronoi import Vor

COLOR = {'tims': 'red', 'sb': 'green', 'lcbo': 'blue', 'ct': 'black'}


def plot_points(m, points_dict):
    for (tag, points) in points_dict.items():
        for pt in points:
            m.plot_location(pt)

m = Map()
# border shape --> Borders
# swept data --> Location --Vor--> VorRegion ---> |
# census shape |                                  | compute overlap --> PopRegion
# population   |  -->      CensusArea        ---> |
#

import sys
import logging
def main(args):
    if not args.quiet:
        logging.basicConfig(level=logging.INFO)

    bounds = Borders.for_state(args.state)

    locations = location_loader.within(args.tags, bounds.multipoly())
    print(len(locations), 'total locations')
    loc_count = Counter(loc.tag for loc in locations)
    for t in loc_count:
        print('\t', t, loc_count[t])

    if args.plot_voronoi or args.plot_overlaps:
        vor_regions = Vor(locations).clipped_regions(bounds.hull(), finite=True)
        print(len(vor_regions), 'locations')

    if args.plot_census or args.plot_overlaps:
        census_areas = list(CensusArea.for_state(args.state))
        print(len(census_areas), 'census areas')

    if args.plot_overlaps:
        overlaps = compute_overlaps_strtree(census_areas, vor_regions)

    if args.plot_border:
        m.plot_border(bounds)
    if args.plot_voronoi:
        for region in vor_regions:
            m.plot_vor_region(region)
    if args.plot_census:
        m.plot_census_areas(census_areas)
    if args.plot_overlaps:
        for pop_region in overlaps:
            m.plot_pop_region(pop_region)
    if args.plot_locations:
        for loc in locations:
            m.plot_location(loc)


    m.m.save('out.html')

    if args.plot_overlaps:
        print('')
        rslt = Counter()
        for o in overlaps:
            rslt[o.tag] += o.pop

        for (tag, pop) in rslt.most_common():
            print(tag, pop)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("state")
    parser.add_argument("--tags", nargs='+')
    parser.add_argument("--plot_border", action='store_true')
    parser.add_argument("--plot_locations", action='store_true')
    parser.add_argument("--plot_voronoi", action='store_true')
    parser.add_argument("--plot_census", action='store_true')
    parser.add_argument("--plot_overlaps", action='store_true')
    parser.add_argument("--quiet", action="store_true")

    args = parser.parse_args()
    main(args)