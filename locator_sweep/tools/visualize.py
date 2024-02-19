import argparse
import datetime as dt
import folium
import folium.plugins
import logging
import json

import shapely
from shapely.geometry import Polygon, box

from locator_sweep.specs import Spec
from locator_sweep.fetcher import Fetcher
from locator_sweep.sweep import Sweep, circle


def to_geojson(obj, k=0, color='blue'):
    if hasattr(obj, 'geoms'):
        geoms = obj.geoms
    else:
        geoms = [obj]

    ret = []
    for geom in geoms:
        geom = json.loads(shapely.to_geojson(geom))
        geom['coordinates'] = [(y,x) for (x,y) in geom['coordinates']]

        ret += [{
            'type': 'Feature',
            'geometry': geom,
            'properties': {
                "times": [str(dt.datetime(2000, 1, 1) + dt.timedelta(minutes=2*k)) for _i in geom['coordinates']],
                "style": {
                    "color": color,
                    "weight": 5,
                },
            }
        }]
    return ret


def main(args):
    spec = Spec.for_tag(args.tag)
    fetcher = Fetcher(spec)
    boundary = box(args.lat-4, args.lon-4, args.lat+4, args.lon+4)
    sweep = Sweep(fetcher, boundary)

    m = folium.Map(location=boundary.centroid.coords[0], prefer_canvas=True)

    folium.Polygon(boundary.buffer(0.01).exterior.coords, color='cyan').add_to(m)

    features = []
    querys = set()
    points = set()
    # out_points = set()
    for k in range(args.iters):
        logging.info('round=%d queries=%d points=%d', k, len(querys), len(points))
        qs = sweep.points_to_explore()
        if not qs: break
        # rslt = list(tuple(r) for r in sweep.sweep())
        pts = {tuple(r.point) for r in sweep.sweep()}

        querys |= set(qs)
        points |= pts
        # out_points |= set(rslt)

        features += [*to_geojson(sweep.frontier, k=k)]
        for interior in sweep.cover.interiors:
            features += [*to_geojson(interior, k=k, color='purple')]
        for pt in sweep.points_to_explore():
            features +=[*to_geojson(Polygon(circle(pt,1000.1,4)).exterior, k=k, color='red')]
        for pt in pts:
            features +=[*to_geojson(Polygon(circle(pt,0.1,4)).exterior, k=k, color='green')]

    print(k, len(querys), len(points))
    for pt in points:
        features +=[*to_geojson(Polygon(circle(pt,0.1,4)).exterior, k=k, color='green')]

    folium.plugins.TimestampedGeoJson(
        {
            "type": "FeatureCollection",
            "features": features,
        },
        period="PT1M",
        duration="PT1M",
        add_last_point=False,
    ).add_to(m)

    #with open(args.out, 'w') as fp:
    #    json.dump(list(out_points), fp)

    m.save('out.html')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tag")
    parser.add_argument("lat", type=float)
    parser.add_argument("lon", type=float)
    parser.add_argument("--iters", type=int, default=5)

    logging.basicConfig(level=logging.INFO)

    main(parser.parse_args())
