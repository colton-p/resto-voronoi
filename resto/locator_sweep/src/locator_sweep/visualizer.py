import datetime as dt
import folium
import folium.plugins
import json

from shapely import to_geojson as shapely_to_geojson
from shapely.geometry import Polygon

from locator_sweep.sweeper import Sweeper, circle


def to_geojson(obj, k=0, color="blue"):
    if hasattr(obj, "geoms"):
        geoms = obj.geoms
    else:
        geoms = [obj]

    ret = []
    for geom in geoms:
        geom = json.loads(shapely_to_geojson(geom))
        geom["coordinates"] = [(y, x) for (x, y) in geom["coordinates"]]

        ret += [
            {
                "type": "Feature",
                "geometry": geom,
                "properties": {
                    "times": [
                        str(dt.datetime(2000, 1, 1) + dt.timedelta(minutes=2 * k))
                        for _i in geom["coordinates"]
                    ],
                    "style": {
                        "color": color,
                        "weight": 5,
                    },
                },
            }
        ]
    return ret


class Visualizer:
    def __init__(self, sweeper) -> None:
        boundary = sweeper.boundary
        self.map = folium.Map(location=boundary.centroid.coords[0], prefer_canvas=True)
        self.features = []
        self.level = 0
        # draw boundary
        folium.Polygon(boundary.buffer(0.01).exterior.coords, color="cyan").add_to(
            self.map
        )

    def add_features(self, sweeper: Sweeper, points):
        self.features += [*to_geojson(sweeper.frontier, k=self.level)]
        for interior in sweeper.cover.interiors:
            self.features += [*to_geojson(interior, k=self.level, color="purple")]
        for pt in sweeper.points_to_explore():
            self.features += [
                *to_geojson(
                    Polygon(circle(pt, 1000.1, 4)).exterior, k=self.level, color="red"
                )
            ]
        self.add_points(points)

        self.level += 1

    def add_points(self, points):
        for pt in points:
            self.features += [
                *to_geojson(
                    Polygon(circle(pt.point, 0.1, 4)).exterior,
                    k=self.level,
                    color="green",
                )
            ]

    def finalize(self):
        folium.plugins.TimestampedGeoJson(
            {
                "type": "FeatureCollection",
                "features": self.features,
            },
            period="PT1M",
            duration="PT1M",
            add_last_point=False,
        ).add_to(self.map)
