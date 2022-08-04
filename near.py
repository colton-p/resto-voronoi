import scipy
import numpy as np
import folium
import json
from math import radians, cos, sin, asin, sqrt
import itertools


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    r = 6371
    return c * r


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

for tag in TAGS:
    with open(f'data/{tag}.json', 'r') as f:
        data = json.load(f)
        DATA[tag] = [(lat, lon) for (id, name, lat, lon)
                     in data
                     # if haversine(lon, lat, -80.5, 43.5) > 0
                     if lat > 50
                     ]

for tag in DATA:
    print(tag, len(DATA[tag]))

m = folium.Map(location=[43.5, -80.5])
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
m.save('out2.html')
