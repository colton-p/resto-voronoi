from dataclasses import dataclass
import csv
import shapefile
import pyproj
import itertools
import haversine

from shapely.geometry import Polygon

POP = {}
PREFIX = '4'
with open('census/data/full.csv', 'r') as csvfile:
    for line in csv.reader(csvfile):
        if line[-1] == 'C1_COUNT_TOTAL':
            continue
        POP[line[1]] = int(line[-1] or 0)

sf = shapefile.Reader('shapes/canada_census/lda_000b21a_e')


can_txer = pyproj.Transformer.from_crs(3347, 4326)
def can_tx(x, y): return can_txer.transform(x, y)


def shape_to_polys(shape, tx=can_tx):
    def pairwise(iterable):
        a, b = itertools.tee(iterable)
        next(b, None)
        return tuple(zip(a, b))
    part_ixs = pairwise(list(shape.parts) + [len(shape.points)])

    return [
        [tx(*point) for point in shape.points[start:end]]
        for (start, end) in part_ixs
    ]


@dataclass
class Da:
    id: str
    poly: Polygon
    pop: int

    def points(self):
        return self.poly.exterior.coords


def das_from_sr(sr):
    shape = sr.shape
    record = sr.record

    id = record[0]
    total_pop = POP[id]
    total_area = 0

    polys = [Polygon(points) for points in shape_to_polys(shape)]
    total_area = sum(p.area for p in polys)

    for poly in polys:
        pop = int(total_pop*poly.area / total_area)
        if pop > 0:
            yield Da(
                id=record[0],
                poly=poly,
                pop=pop,
            )


def da_for_prefix(prefix):
    n_shapes = 0
    n_parts = 0
    n_points = 0

    for (ix, sr) in enumerate(sf.iterShapeRecords()):
        if sr.record[0][:len(prefix)] != prefix:
            continue
        n_shapes += 1

        for da in das_from_sr(sr):
            n_parts += 1
            n_points += (len(da.poly.exterior.coords) - 1)

            yield da

    print(f'das: shapes={n_shapes}, parts={n_parts}, points={n_points}')


def da_for_ids(ids):
    n_shapes = 0
    n_parts = 0
    n_points = 0

    for id in ids:
        sr = sf.shapeRecord(id)
        n_shapes += 1

        for da in das_from_sr(sr):
            n_parts += 1
            n_points += (len(da.poly.exterior.coords) - 1)

            yield da

    print(f'das: shapes={n_shapes}, parts={n_parts}, points={n_points}')
