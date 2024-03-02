import argparse
import logging
import math
import folium

import haversine

from locator_sweep.specs import Spec
from locator_sweep.fetcher import Fetcher


sd = (32.5362325777801, -117.1173664121147)
hon = (21.306753238447882, -157.868914454869)
tb = (48.45594858305442, -89.26706422308901)

def main(args):
    spec = Spec.for_tag(args.tag)
    f = Fetcher(spec)

    def max_dist(p):
        rslt = f.page(*p, force=True)

        dists = [haversine.haversine(p, q.point) for q in rslt]
        if not dists:
            print('  no results')
            return None
        print(f'  near={min(dists):.3f} far={max(dists):.3f} num={len(rslt)}')

        return max(dists)

    def pick_initial(p):
        south = min((loc.point for loc in f.page(*p)), key=lambda l: l.lat)
        return south

    initial_area = {'sd': sd, 'hon': hon, 'tb': tb}[args.initial_location]

    init = pick_initial(initial_area)
    min_d, max_d = 0, args.initial_distance

    max_range = 0

    for i in range(args.iters):
        print(f"--- step {i} --- ")
        print(f"range: {min_d} -- {max_d}")
        query_d = min_d + (max_d - min_d) / 2
        print(f"query: {query_d: .3f}")
        query_pt = haversine.inverse_haversine(init, query_d, math.pi)

        rslt = max_dist(query_pt)
        if rslt is None:
            max_d = query_d
        else:
            min_d = query_d
            max_range = max(query_d, max_range)

    print("-----")
    print("")
    print("max range =")
    print(max_range)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tag")
    parser.add_argument("--initial_distance", default=1000, type=int)
    parser.add_argument("--initial_location", default='hon', choices=['tb', 'hon', 'sd'])
    parser.add_argument("--iters", default='10', type=int)
    main(parser.parse_args())
