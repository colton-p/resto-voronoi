# given a fetcher
# does the sweep

import math

import haversine
from shapely.geometry import Polygon, Point

from locator_sweep.fetcher import Fetcher

def circle(pt, radius, num_points = 16):
    (lat, lon) = pt
    points = []
    for ix in range(num_points):
        heading = math.pi * 2 * ix / num_points
        points += [haversine.inverse_haversine((lat, lon), radius / 1000, heading)]

    return points

class Sweep:
    def __init__(self, fetcher: Fetcher, boundary: Polygon) -> None:
        self.fetcher = fetcher
        self.boundary = boundary # the bounds for exploration
        self.cover = Polygon() # the currently explored area

    @property
    def frontier(self):
        """the edge of the explored area"""
        return (self.cover.exterior).difference(self.boundary.exterior.buffer(0.01))

    def explore(self, pt):
        """explore from pt, expanding cover"""
        points = self.fetcher.page(*pt)

        if not points:
            return self.fetcher.max_range, []

        furthest = points[-1]
        radius = haversine.haversine(pt, furthest.point) * 1000
        radius = max(int(radius), 1)
        return radius, points

    def points_to_explore(self):
        """points to explore next, on the frontier of the currently explored area"""
        if self.cover.is_empty:
            return [self.boundary.centroid.coords[0]]
        qs = []
        exterior = self.frontier
        if not exterior.is_empty:
            qs += [exterior.interpolate(i / 4.0, True).coords[0] for i in range(4)]
        for interior in self.cover.interiors:
            qs += [interior.interpolate(i / 1.0, True).coords[0] for i in range(1)]

        return qs

    def sweep(self):
        """yield points, from one round of queries, expanding the explored area"""
        for q_pt in self.points_to_explore():
            (radius, points) = self.explore(q_pt)

            new_covered = Polygon(circle(q_pt, radius)).intersection(self.boundary)
            self.cover = self.cover.union(new_covered)
            if not isinstance(self.cover, Polygon):
                self.cover = max(self.cover.geoms, key=lambda x: x.area)

            for pt in points:
                if self.boundary.contains(Point(pt[4:])):
                    yield pt
    