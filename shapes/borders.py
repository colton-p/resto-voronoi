import argparse
import itertools

import shapefile
import shapely
from shapely.geometry import Polygon, MultiPolygon
import pyproj


def shape_to_polys(shape, tx):
    part_ixs = itertools.pairwise(list(shape.parts) + [len(shape.points)])
    return [
        [(tx(*point)) for point in shape.points[start:end]] for (start, end) in part_ixs
    ]


PROV_PREFIX = {
    "nl": 10,
    "pe": 11,
    "ns": 12,
    "nb": 13,
    "qc": 24,
    "on": 35,
    "mb": 46,
    "sk": 47,
    "ab": 48,
    "bc": 59,
    "yt": 60,
    "nt": 61,
    "nu": 62,
    "atlantic": 1,
    "prairies": 4,
    "north": 6,
    "canada": "",
    "row": "3530",
}

STATE_CODE = {
    "al": "01",
    "ak": "02",
    "az": "04",
    "ar": "05",
    "ca": "06",
    "co": "08",
    "ct": "09",
    "de": 10,
    "fl": 12,
    "ga": 13,
    "hi": 15,
    "id": 16,
    "il": 17,
    "in": 18,
    "ia": 19,
    "ks": 20,
    "ky": 21,
    "la": 22,
    "me": 23,
    "md": 24,
    "ma": 25,
    "mi": 26,
    "mn": 27,
    "ms": 28,
    "mo": 29,
    "mt": 30,
    "ne": 31,
    "nv": 32,
    "nh": 33,
    "nj": 34,
    "nm": 35,
    "ny": 36,
    "nc": 37,
    "nd": 38,
    "oh": 39,
    "ok": 40,
    "or": 41,
    "pa": 42,
    "ri": 44,
    "sc": 45,
    "sd": 46,
    "tn": 47,
    "tx": 48,
    "ut": 49,
    "vt": 50,
    "va": 51,
    "wa": 53,
    "wv": 54,
    "wi": 55,
    "wy": 56,
}

class Borders:
    @staticmethod
    def for_state(state):
        if state in PROV_PREFIX:
            path = "shapes/canada/lpr_000a21a_e"
            prefix = PROV_PREFIX[state]
            can_txer = pyproj.Transformer.from_crs(3347, 4326)
            pt_tx = lambda x, y: can_txer.transform(x, y)
            return Borders(path, prefix, pt_tx)

        if state == "usa":
            path = "shapes/us/cb_2018_us_nation_20m"
            prefix = ""
        elif state in STATE_CODE:
            path = "shapes/us/cb_2018_us_state_20m"
            prefix = STATE_CODE[state]
        return Borders(path, prefix, lambda x, y: (y, x))

    def __init__(self, filepath, prefix, pt_tx):
        self.sf = shapefile.Reader(filepath, encoding="latin1")
        self.prefix = str(prefix)
        self.pt_tx = pt_tx

    def main(self):
        return max(self.multipoly().geoms, key=lambda x: len(x.exterior.coords))

    def hull(self):
        return shapely.unary_union(list(self.polygons())).convex_hull

    def multipoly(self):
        polys = [p.buffer(0.01) for p in self.polygons() if p.centroid.coords[0][1] < 0]

        union = shapely.unary_union(polys)
        if isinstance(union, Polygon):
            return MultiPolygon([union])
        return union

    def shapes(self):
        for sr in self.sf.iterShapeRecords():
            if self._geo_id(sr.record).startswith(self.prefix):
                yield sr.shape

    def polygons(self):
        for shape in self.shapes():
            for points in shape_to_polys(shape, self.pt_tx):
                yield Polygon(points).simplify(10**-3)
    
    def _geo_id(self, record):
        return record[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('state')
    args = parser.parse_args()

    b = Borders.for_state(args.state)

    print(args.state)
    print(sum(1 for _ in b.polygons()), 'polys')
    print(sum(1 for _ in b.polygons()), 'shapes')
    print(sum(len(p.exterior.coords) for p in b.polygons()), 'points')

    mp = b.multipoly()
    print(f'{b.main().area/mp.area:.3f} main % area')
    print(b.main().centroid, 'centroid')
