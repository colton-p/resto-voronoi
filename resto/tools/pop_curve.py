import argparse
import logging

from locator_sweep.sweeper import circle
from shapely.geometry import Polygon
from shapely.ops import unary_union

from resto.borders import Borders
from resto.census_area import CensusArea
from resto import locations as location_loader
from resto.overlap import compute_overlaps_strtree
from resto.voronoi import VorRegion
from resto.population_curve import PopulationCurve


def main(args):
    if not args.quiet:
        logging.basicConfig(level=logging.INFO)

    curve = PopulationCurve.for_state(args.state, args.tag)

    print(args.state, f"pop={curve.total_pop} areas={len(curve.census_areas)} pts={len(curve.locations)}")
    for dist in args.dists:
        (pct_covered, covered_pop, n_covered_polys) = curve.distance(dist)
        print(f"{args.state} {args.tag} {dist:3d} {pct_covered:.3f} {covered_pop:8d} {n_covered_polys}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--state")
    parser.add_argument("--tag")
    parser.add_argument("--quiet", action='store_true')
    parser.add_argument("--dists", nargs='+', default=[1, 10, 100], type=int)

    args = parser.parse_args()
    main(args)
