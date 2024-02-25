import math
from locator_sweep.specs import StoreRecord
from locator_sweep.sweeper import Sweeper
from shapely.geometry import box

class FakeFetcher():
    max_range = 10
    def __init__(self, points):
        self.points = points
    
    def page(self, lat, lon):
        return [
            StoreRecord('', '', '', '', point)
            for point in self.points
            if math.dist((lat, lon), point) < 10
        ][:10]


def test_exists():
    assert Sweeper

def test_works():
    fetcher = FakeFetcher([(1, 1), (9,9)])
    boundary = box(-10, -10, 10, 10)
    sweep = Sweeper(fetcher, boundary)

    points = [rec.point for rec in sweep.sweep_once()]
    assert list(points) == [(1, 1)]

def test_works2():
    fetcher = FakeFetcher([(1, 1), (9,9)])
    boundary = box(-10, -10, 10, 10)
    sweep = Sweeper(fetcher, boundary)

    found = set()
    for _i in range(10):
        it = sweep.sweep_once()
        found |= {r.point for r in it}

    assert found == {(1,1), (9, 9)}