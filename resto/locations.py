from collections import namedtuple
import logging
import json
import os
import sqlite3
from typing import Dict, List

import haversine
from shapely.geometry import box as Box, Point

from locator_sweep.fetcher import load_store_record
from locator_sweep.specs import LatLon
from resto.borders import Borders
from resto.states import USA_ALIASES, CANADA_ALIASES

Location = namedtuple('Location', ['tag', 'name', 'state', 'point'])

DB_PATH = os.path.join(os.environ['RESTO_DATA_DIR'], 'output', 'locations', 'locations.db')

def _location_from_data(data, tag):
    record = load_store_record(data)
    return Location(tag, record.name, record.state, record.point)

def from_predicate(tags, pred=lambda x, y: True) -> Dict[str, List[Location]]:
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        res = cur.execute(
            f"SELECT tag, name, state, lat, lon from locations where tag IN ({','.join('?' for _ in tags)})",
            tags
        )
        records = [
            Location(tag, name, state, LatLon(lat, lon))
            for (tag, name, state, lat, lon) in res
        ]
        logging.info('%d records from db', len(records))

        return [rec for rec in records if pred(*rec.point)]

def nearby(tags, pt=(43.5, -80.5), dist=50):
    def nearby_pred(lat, lon):
        return haversine.haversine((lat, lon), pt) < dist

    return from_predicate(tags, nearby_pred)

def within(tags, box=Box(43, -81, 44, -80)):
    def within_pred(lat, lon):
        return box.contains(Point(lat, lon))

    return from_predicate(tags, within_pred)

def for_state_borders(tags, state):
    return within(tags, Borders.for_state(state).multipoly())

def for_state(tags, state):
    states = (CANADA_ALIASES | USA_ALIASES).get(state, [state])
    query = f"SELECT tag, name, state, lat, lon from locations WHERE tag IN ({','.join('?' for _ in tags)})"
    query += f" AND state IN ({','.join('?' for _ in states)})"
    args = tags + [st.upper() for st in states]

    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        res = cur.execute(query, args)
        records = [
            Location(tag, name, state, LatLon(lat, lon))
            for (tag, name, state, lat, lon) in res
        ]
        logging.info('%d records from db', len(records))

        return records
