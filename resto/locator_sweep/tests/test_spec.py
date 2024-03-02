import json
import os

import pytest

from locator_sweep.specs import LatLon, Spec

def clean_data(tag):
    data = json.load(open(f'resto/locator_sweep/tests/fixtures/{tag}.json'))
    spec = Spec.for_tag(tag)
    nodes = spec.unpack(data)
    return spec.clean(list(nodes.values())[0])

def test_sb():
    rslt = clean_data('sb')

    assert rslt.id == '1026093'
    assert rslt.name == '1935 Paris Street'
    assert rslt.city == 'Sudbury'
    assert rslt.state == 'ON'
    assert rslt.country == 'CA'
    assert rslt.point == LatLon(46.45326, -81.00264)

def test_subway():
    rslt = clean_data('subway')

    assert rslt.id == '16854'
    assert rslt.name == '275 Hillside Drive South'
    assert rslt.city == 'Elliot Lake'
    assert rslt.state == 'ON'
    assert rslt.country == 'CA'
    assert rslt.point == LatLon(46.3793, -82.6608)