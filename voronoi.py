from typing import Tuple
import scipy
import numpy as np
import folium
import json
from math import radians, cos, sin, asin, sqrt
import itertools
from shapely.geometry import Polygon, box as Box, Point

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


class Vor:

    @classmethod
    def nearby(cls, pt=(43.5, -80.5), dist=50):
        all_data = {}
        for tag in TAGS:
            with open(f'fetch/data/{tag}.json', 'r') as f:
                data = json.load(f)
                all_data[tag] = [
                    (lat, lon) for (id, name, state, ctry, lat, lon)
                    in data
                    # if haversine.haversine((lat, lon), pt) < dist
                    if ctry in ['Canada', 'CA']
                ]
        return cls(all_data)

    @classmethod
    def within(cls, box=Box(43, -81, 44, -80)):
        all_data = {}
        for tag in TAGS:
            with open(f'fetch/data/{tag}.json', 'r') as f:
                data = json.load(f)
                all_data[tag] = [
                    (lat, lon) for (id, name, state, ctry, lat, lon)
                    in data
                    if box.contains(Point(lat, lon))
                ]
        return cls(all_data)

    def __init__(self, points) -> None:
        self.points = points

    def regions(self) -> Tuple[str, Polygon]:
        for (tag, regions) in self.regions_dict().items():
            for region in regions:
                yield(tag, region)

    def regions_dict(self):
        point_labels = list(itertools.chain(
            *[[tag] * len(self.points[tag]) for tag in self.points]
        ))
        points = list(itertools.chain(*self.points.values()))
        vor = scipy.spatial.Voronoi(points)

        region_labels = {
            region_ix: point_labels[point_ix]
            for (point_ix, region_ix) in enumerate(vor.point_region)
        }

        polys = {tag: [] for tag in TAGS}
        for (region_ix, region) in enumerate(vor.regions):
            if -1 in region:
                continue
            tag = region_labels.get(region_ix)
            if not tag:
                continue
            polys[tag] += [
                Polygon(vor.vertices[i] for i in region)
            ]

        return polys
