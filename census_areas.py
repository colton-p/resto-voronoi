from dataclasses import dataclass
from tkinter import W
import shapefile
import itertools
import argparse
import pyproj

import folium
import population as Pop

from shapely.geometry import Polygon


def shape_to_polys(shape, tx):
    def pairwise(iterable):
        a, b = itertools.tee(iterable)
        next(b, None)
        return tuple(zip(a, b))
    part_ixs = pairwise(list(shape.parts) + [len(shape.points)])

    return [
        [tx(*point) for point in shape.points[start:end]]
        for (start, end) in part_ixs
    ]


PROV_PREFIX = {'nl': 10, 'pe': 11, 'ns': 12, 'nb': 13, 'qc': 24, 'on': 35,
               'mb': 46, 'sk': 47, 'ab': 48, 'bc': 59, 'yt': 60, 'nt': 61, 'nu': 62,
               'atlantic': 1,
               'prairies': 4,
               'north': 6,
               'canada': '',
               'row': '3530'
               }

STATE_CODE = {
    'al': '01', 'ak': '02', 'az': '04', 'ar': '05', 'ca': '06', 'co': '08', 'ct': '09',
    'de': 10, 'fl': 12, 'ga': 13, 'hi': 15, 'id': 16, 'il': 17, 'in': 18, 'ia': 19,
    'ks': 20, 'ky': 21, 'la': 22, 'me': 23, 'md': 24, 'ma': 25, 'mi': 26, 'mn': 27, 'ms': 28, 'mo': 29,
    'mt': 30, 'ne': 31, 'nv': 32, 'nh': 33, 'nj': 34, 'nm': 35, 'ny': 36, 'nc': 37, 'nd': 38, 'oh': 39,
    'ok': 40, 'or': 41, 'pa': 42, 'ri': 44, 'sc': 45, 'sd': 46, 'tn': 47, 'tx': 48, 'ut': 49,
    'vt': 50, 'va': 51, 'wa': 53, 'wv': 54, 'wi': 55, 'wy': 56,
}


@dataclass
class CensusArea:
    id: str
    poly: Polygon
    pop: int

    def points(self):
        return self.poly.exterior.coords


class CensusAreas:

    @staticmethod
    def for_state(state):

        if state in STATE_CODE:
            code = STATE_CODE[state]
            path = f'shapes/us_census/cb_2021_{code}_bg_500k/cb_2021_{code}_bg_500k'
            return UsCensusAreas(path, Pop.pop_dict(state))

        code = PROV_PREFIX[state]
        path = 'shapes/canada_census/lda_000b21a_e'

        return CanadaCensusAreas(path, Pop.pop_dict(state), str(code))

    def __init__(self, filepath, population, prefix=None):
        self.sf = shapefile.Reader(filepath)
        self.population = population
        self.prefix = prefix

    def areas(self):
        n_shapes = 0
        n_parts = 0
        n_points = 0

        for sr in self.sf.iterShapeRecords():
            if self.prefix and not self.geo_id(sr.record).startswith(self.prefix):
                continue
            n_shapes += 1

            for da in self.areas_from_sr(sr):
                n_parts += 1
                n_points += (len(da.poly.exterior.coords) - 1)

                yield da

        print(f'das: shapes={n_shapes}, parts={n_parts}, points={n_points}')

    def areas_from_sr(self, sr):
        shape = sr.shape
        record = sr.record

        id = self.geo_id(record)
        total_pop = self.population[id]
        total_area = 0

        polys = [Polygon(points)
                 for points in shape_to_polys(shape, self.pt_tx)]
        total_area = sum(p.area for p in polys)

        for (part_ix, poly) in enumerate(polys):
            pop = int(total_pop*poly.area / total_area)
            if pop > 0:
                yield CensusArea(
                    id=f'{id}-{part_ix}',
                    poly=poly,
                    pop=pop,
                )


class UsCensusAreas(CensusAreas):
    def geo_id(self, record):
        return record[5]

    @staticmethod
    def pt_tx(x, y): return (y, x)


can_txer = pyproj.Transformer.from_crs(3347, 4326)


class CanadaCensusAreas(CensusAreas):
    def geo_id(self, record):
        return record[0]

    @staticmethod
    def pt_tx(x, y):
        return can_txer.transform(x, y)


def main(args):
    das = list(CensusAreas.for_state(args.state).areas())

    m = folium.Map(location=das[0].points()[0])
    for da in das:
        folium.Polygon(
            da.points(),
            color='blue',
            fill=True,
            weight=1,
            dash_array='4',
            tooltip=f'{da.id} {da.pop}'
        ).add_to(m)

    m.save('out.html')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('state')
    main(parser.parse_args())
