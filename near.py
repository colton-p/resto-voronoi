import scipy
import numpy as np
import folium
import json
from math import radians, cos, sin, asin, sqrt
import itertools

import haversine

COLOR = {
    'tims': 'crimson',
    'mcds': 'yellow',
    'sbux': 'green',
}
TAGS = [
    'tims',
    'mcds',
    'sbux'
]
DATA = {}

S = [43.5, -80.5]


def near(m, S, dist):
    for tag in TAGS:
        with open(f'fetch/data/{tag}.json', 'r') as f:
            data = json.load(f)
            DATA[tag] = [(lat, lon) for (id, name, state, ctry, lat, lon)
                         in data
                         # if state in ['CA', 'Canada']
                         if haversine.haversine((lat, lon), S) < 50
                         # if lat > 50
                         ]
    # 33.4 -112.6

    for tag in DATA:
        print(tag, len(DATA[tag]))

    # m = folium.Map(location=S)
    if True:
        point_labels = list(itertools.chain(
            *[[tag] * len(DATA[tag]) for tag in DATA]
        ))
        points = list(itertools.chain(*DATA.values()))
        vor = scipy.spatial.Voronoi(points)

        region_labels = {
            region_ix: point_labels[point_ix]
            for (point_ix, region_ix) in enumerate(vor.point_region)
        }

        polys = []
        for (region_ix, region) in enumerate(vor.regions):
            if -1 in region:
                continue
            clr = COLOR.get(region_labels.get(region_ix), 'grey')
            polys += [
                ([vor.vertices[i] for i in region], clr)
            ]

        for (poly, clr) in polys:
            if poly:
                folium.Polygon(poly, color=clr, fill=True, stroke=True,
                               weight=1, opacity=0.5).add_to(m)

    for tag in DATA:
        for (lat, lon) in DATA[tag]:
            folium.CircleMarker(
                location=(lat, lon),
                color=COLOR[tag],
                radius=5,
                fill=True
            ).add_to(m)

    m.add_child(folium.LatLngPopup())
    # m.save('out3.html')
