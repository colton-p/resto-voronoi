# shapefile to polygons
import itertools
import logging
import os
from typing import Iterator, List, Tuple

import pyproj
from shapely.geometry import Polygon
import shapefile

from resto.shapes.prefixes import PROV_PREFIX, STATE_PREFIX

SHAPES_DIR = os.path.join(
    os.environ['RESTO_DATA_DIR'],
    'input',
    'shapes'
)

def _shape_to_polys(shape, tx):
    part_ixs = itertools.pairwise(list(shape.parts) + [len(shape.points)])
    return [
        Polygon([(tx(*point)) for point in shape.points[start:end]])
        for (start, end) in part_ixs
    ]


def load_borders_from_shapefile(filepath, prefix, pt_tx, get_id) -> Iterator[Tuple[str, List[Polygon]]]:
    sf_path = os.path.join(SHAPES_DIR, filepath)
    sf = shapefile.Reader(sf_path, encoding="latin1")
    logging.info(filepath)
    logging.info(sf)
    def shapes():
        for sr in sf.iterShapeRecords():
            geo_id = get_id(sr.record)
            if geo_id.startswith(prefix):
                yield geo_id, sr.shape

    for (geo_id, shape) in shapes():
        polys = [
            poly.simplify(10**-3)
            for poly in
            _shape_to_polys(shape, pt_tx)
        ]
        yield geo_id, polys

class ShapeLoader:
    @staticmethod
    def for_state(state):
        if state in STATE_PREFIX:
            return UsaShapeLoader(state)
        if state in PROV_PREFIX:
            return CanadaShapeLoader(state)

    def __init__(self, state) -> None:
        self.state = state

class CanadaShapeLoader(ShapeLoader):
    @property
    def geo_prefix(self):
        return str(PROV_PREFIX[self.state])
    @property
    def point_transform(self):
        can_txer = pyproj.Transformer.from_crs(3347, 4326)
        return can_txer.transform
    @property
    def state_shapefile(self):
        return 'canada/lpr_000a21a_e'
    @property
    def census_shapefile(self):
        return 'canada_census/lda_000b21a_e'
    @property
    def census_record_id(self):
        return lambda record: record[0]

class UsaShapeLoader(ShapeLoader):
    @property
    def geo_prefix(self):
        return str(STATE_PREFIX[self.state])
    @property
    def point_transform(self):
        return lambda x, y: (y, x)
    @property
    def state_shapefile(self):
        if self.state == 'usa':
            return 'us/cb_2018_us_nation_20m'
        return 'us/cb_2018_us_state_20m'
    @property
    def census_shapefile(self):
        prefix = STATE_PREFIX[self.state]
        return f'us_census/cb_2021_{prefix}_bg_500k/cb_2021_{prefix}_bg_500k'
    @property
    def census_record_id(self):
        return lambda record: record[5]


def state_borders(state):
    logging.info('load state borders for %s', state)
    loader = ShapeLoader.for_state(state)
    return load_borders_from_shapefile(
        loader.state_shapefile,
        loader.geo_prefix,
        loader.point_transform,
        lambda record: record[0],
    )

def census_borders(state):
    logging.info('load census borders for %s', state)
    loader = ShapeLoader.for_state(state)
    return load_borders_from_shapefile(
        loader.census_shapefile,
        loader.geo_prefix,
        loader.point_transform,
        loader.census_record_id
    )
