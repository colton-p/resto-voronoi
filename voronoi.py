from typing import Tuple
import scipy
import numpy as np
import json
import itertools
from shapely.geometry import Polygon, box as Box, Point

import haversine

TAGS = [
    'tims',
    'mcds',
    'sbux'
]


def voronoi_finite_polygons_2d(vor, radius=None):
    """
    Reconstruct infinite voronoi regions in a 2D diagram to finite
    regions.
    Parameters
    ----------
    vor : Voronoi
        Input diagram
    radius : float, optional
        Distance to 'points at infinity'.
    Returns
    -------
    regions : list of tuples
        Indices of vertices in each revised Voronoi regions.
    vertices : list of tuples
        Coordinates for revised Voronoi vertices. Same as coordinates
        of input vertices, with 'points at infinity' appended to the
        end.
    """

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()*2

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1]  # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:, 1] - c[1], vs[:, 0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)


def load_records(pred=lambda x, y: True):
    all_data = {}
    for tag in TAGS:
        with open(f'fetch/data/{tag}.json', 'r') as f:
            data = json.load(f)
            all_data[tag] = [(lat, lon) for
                             (id, name, state, ctry, lat, lon)
                             in data
                             if pred(lat, lon) and ctry in ['CA', 'Canada']]
    return all_data


class Vor:
    @classmethod
    def nearby(cls, pt=(43.5, -80.5), dist=50):
        def nearby_pred(lat, lon):
            return haversine.haversine((lat, lon), pt) < dist

        data = load_records(nearby_pred)
        return cls(data)

    @classmethod
    def within(cls, box=Box(43, -81, 44, -80)):
        def within_pred(lat, lon):
            return box.contains(Point(lat, lon))

        data = load_records(within_pred)
        return cls(data)

    @classmethod
    def all(cls):
        data = load_records()
        return cls(data)

    def __init__(self, points) -> None:
        self.points = points

    def clipped_points(self, hull):
        return {
            tag: [pt for pt in points if hull.contains(Point(pt))]
            for (tag, points)
            in self.points.items()
        }

    def clipped_regions(self, hull, finite=True):
        all_regions = [
            (tag, region.intersection(hull))
            for (tag, region)
            in self.regions(finite=finite)
        ]

        return [(tag, region) for (tag, region) in all_regions if not region.is_empty]

    def regions(self, finite=True) -> Tuple[str, Polygon]:
        for (tag, regions) in self.regions_dict(finite=finite).items():
            for region in regions:
                yield(tag, region)

    def regions_dict(self, finite=True):
        print(finite)
        point_labels = list(itertools.chain(
            *[[tag] * len(self.points[tag]) for tag in self.points]
        ))
        points = list(itertools.chain(*self.points.values()))
        vor = scipy.spatial.Voronoi(points)

        polys = {tag: [] for tag in TAGS}
        if finite:
            point_region, vertices = voronoi_finite_polygons_2d(vor)
        else:
            point_region = [vor.regions[ix] for ix in vor.point_region]
            vertices = vor.vertices
        print(len(point_region), len(point_labels))
        for (point_ix, region) in enumerate(point_region):

            tag = point_labels[point_ix]

            if -1 in region:
                continue

            polys[tag] += [
                Polygon(vertices[i] for i in region)
            ]

        return polys
