from collections import namedtuple
import logging
import json
import os
from typing import Dict, List

import haversine
from shapely.geometry import box as Box, Point

from locator_sweep.fetcher import load_store_record
from locator_sweep.specs import LatLon
from resto.borders import Borders

Location = namedtuple('Location', ['tag', 'name', 'state', 'point'])

def _location_from_data(data, tag):
    record = load_store_record(data)
    return Location(tag, record.name, record.state, record.point)


def from_predicate(tags, pred=lambda x, y: True) -> Dict[str, List[Location]]:
    all_data = {}
    for tag in tags:
        path = os.path.join(os.environ['RESTO_DATA_DIR'], f'output/locations/{tag}.json')
        with open(path, 'r', encoding='utf8') as f:
            records = (_location_from_data(r, tag) for r in json.load(f))
            all_data[tag] = [
                rec for rec in records
                if pred(*rec.point)
            ]
            logging.info('%d locations for %s', len(all_data[tag]), tag)
    return all_data

def nearby(tags, pt=(43.5, -80.5), dist=50):
    def nearby_pred(lat, lon):
        return haversine.haversine((lat, lon), pt) < dist

    return from_predicate(tags, nearby_pred)

def within(tags, box=Box(43, -81, 44, -80)):
    def within_pred(lat, lon):
        return box.contains(Point(lat, lon))

    return from_predicate(tags, within_pred)

def for_state(tags, state):
    return within(tags, Borders.for_state(state).multipoly())
