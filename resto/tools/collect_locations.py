import argparse
import logging
import json

from shapely.geometry import box

from locator_sweep.specs import Spec
from locator_sweep.fetcher import Fetcher
from locator_sweep.sweeper import Sweeper
from locator_sweep.sweep import collect_points, collect_points_visualize

from shapes.borders import Borders


def main(args):
    spec = Spec.for_tag(args.tag)
    fetcher = Fetcher(spec)
    boundary = Borders.for_state(args.state).main()
    if args.state == 'canada':
        boundary = boundary.intersection(box(40, -150, 75, -40))

    sweeper = Sweeper(fetcher, boundary)

    if args.visualize:
        (points, folium_map) = collect_points_visualize(sweeper, args.iters)
        folium_map.save(args.visualize)
    else:
        (points) = collect_points(sweeper, args.iters)

    with open(args.outfile, 'w', encoding='utf8') as fp:
        json.dump((points), fp)

    logging.info('%.3f area covered', sweeper.percent_covered())
    logging.info('found %d points in %d queries', len(points), sweeper.queries)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tag")
    parser.add_argument("state")
    parser.add_argument("--iters", type=int, default=5)
    parser.add_argument("--visualize")
    parser.add_argument("--outfile")

    logging.basicConfig(level=logging.INFO)

    main(parser.parse_args())
