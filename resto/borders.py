import argparse
import logging
from resto.shapes.loader import state_borders

import shapely
from shapely.geometry import Polygon, MultiPolygon

class Borders:
    @staticmethod
    def for_state(state):
        def polys():
            for _geoid, polys in state_borders(state):
                for poly in polys:
                    yield poly # TODO: simplify?

        return Borders(list(polys()))

    def __init__(self, polys):
        self.polys = polys

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

    def polygons(self):
        return self.polys
    
    def _geo_id(self, record):
        return record[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('state')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    b = Borders.for_state(args.state)

    print(args.state)
    print(sum(1 for _ in b.polygons()), 'polys')
    print(sum(len(p.exterior.coords) for p in b.polygons()), 'points')

    mp = b.multipoly()
    print(f'{b.main().area/mp.area:.3f} main % area')
    print(b.main().centroid, 'centroid')
