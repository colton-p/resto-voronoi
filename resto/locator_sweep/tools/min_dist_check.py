import argparse
import logging
import math
import folium

import haversine

from locator_sweep.specs import Spec
from locator_sweep.fetcher import Fetcher


sd = (32.5362325777801, -117.1173664121147)
hon = (21.306753238447882, -157.868914454869)

from resto.map import Map

def main(args):
    spec = Spec.for_tag(args.tag)
    f = Fetcher(spec)

    def max_dist(p):
        rslt = f.page(*p)

        dists = [haversine.haversine(p, q.point) for q in rslt]
        if not dists:
            return None
        print(min(dists), max(dists), len(rslt))

        return max(dists)



    def pick_initial(p):
        south = min((loc.point for loc in f.page(*p)), key=lambda l: l.lat)
        return south
    

    # ----|-------|
    #         ^
    tb = (48.45594858305442, -89.26706422308901)
    init = pick_initial(tb)
    print(init)
    max_dist(init)
    min_d, max_d = 0, 1000

    max_range = 0
    
    for i in range(16):
        print(f'range: {min_d} -- {max_d}')
        query_d = min_d + (max_d - min_d) / 2
        print(f'query: {query_d}')
        query_pt = haversine.inverse_haversine(init, query_d, math.pi)

        rslt = max_dist(query_pt)
        if rslt is None:
            max_d = query_d
        else:
            min_d = query_d
            max_range = max(query_d, max_range)

    print('')
    print(max_range)
        


    exit()
    point = (47.122, -81.00659160804538)
    print(point)
    print(max_dist(point))
    print('')
    for i in range(50):
        point = haversine.inverse_haversine(point, 1_000 / 1000, 0)
        print(point)
        print(i, max_dist(point))
    
    locs = f.page(*point)
    m = Map()
    for loc in locs:
        m.plot_location(loc)
    folium.CircleMarker(
        location=point,
        color='black',#COLOR.get(location.tag, 'black'),
        radius=5,
        fill=False,
    ).add_to(m.m)

    m.m.save('out.html')



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tag")
    main(parser.parse_args())