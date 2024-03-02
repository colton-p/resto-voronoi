import math
from locator_sweep.specs import StoreRecord
from locator_sweep.sweeper import Sweeper
from shapely.geometry import box

class FakeFetcher():
    def __init__(self, points):
        self.points = points
    
    def max_range(self, lat, lon):
        return 10_000

    def page(self, lat, lon):
        print(lat, lon)
        return [
            StoreRecord('', '', '', '', '', point)
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
