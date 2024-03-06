# shapefile to polygons
import itertools
import logging
import os
from typing import Iterator, List, Tuple

import pyproj
from shapely.geometry import Polygon
import shapefile

from resto.shapes.prefixes import PROV_PREFIX, STATE_PREFIX
from resto.states import USA_48, USA_ALIASES

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


def load_borders_from_shapefiles(filepaths, pt_tx, get_id, pred) -> Iterator[Tuple[str, List[Polygon]]]:
    for filepath in filepaths:
        sf_path = os.path.join(SHAPES_DIR, filepath)
        sf = shapefile.Reader(sf_path, encoding="latin1")
        logging.info(filepath)
        logging.info(sf)
        def shapes():
            for sr in sf.iterShapeRecords():
                geo_id = get_id(sr.record)
                if pred(geo_id):
                    yield geo_id, sr.shape
                #if geo_id.startswith(prefix):
                #    yield geo_id, sr.shape

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
    def record_predicate(self):
        prefix = self.geo_prefix
        return lambda record_id: record_id.startswith(prefix)
    @property
    def point_transform(self):
        can_txer = pyproj.Transformer.from_crs(3347, 4326)
        return can_txer.transform
    @property
    def state_shapefile(self):
        return 'canada/lpr_000a21a_e'
    @property
    def census_shapefiles(self):
        return ['canada_census/lda_000b21a_e']
    @property
    def census_record_id(self):
        return lambda record: record[0]

class UsaShapeLoader(ShapeLoader):
    @property
    def record_predicate(self):
        if self.state == 'usa':
            # exclude ak, hi, usvi
            prefixes = {str(STATE_PREFIX[st]) for st in USA_48}
            return lambda record_id: record_id[0:2] in prefixes

        prefix = self.geo_prefix
        return lambda record_id: record_id.startswith(prefix)
    @property
    def geo_prefix(self):
        return str(STATE_PREFIX[self.state])
    @property
    def point_transform(self):
        return lambda x, y: (y, x)
    @property
    def state_shapefile(self):
        return 'us/cb_2018_us_state_20m'
    @property
    def census_shapefiles(self):
        states = USA_ALIASES.get(self.state, [self.state])
        def _files():
            for state in states:
                prefix = STATE_PREFIX[state]
                yield f'us_census/cb_2021_{prefix}_bg_500k/cb_2021_{prefix}_bg_500k'
        return list(_files())
    @property
    def census_record_id(self):
        return lambda record: record[5]


def state_borders(state):
    logging.info('load state borders for %s', state)
    loader = ShapeLoader.for_state(state)
    return load_borders_from_shapefiles(
        [loader.state_shapefile],
        pt_tx=loader.point_transform,
        get_id=lambda record: record[0],
        pred=loader.record_predicate,
    )

def census_borders(state):
    logging.info('load census borders for %s', state)
    loader = ShapeLoader.for_state(state)
    return load_borders_from_shapefiles(
        loader.census_shapefiles,
        pt_tx=loader.point_transform,
        get_id=loader.census_record_id,
        pred=loader.record_predicate,
    )
