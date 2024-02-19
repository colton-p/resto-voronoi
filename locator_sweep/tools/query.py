import argparse
import logging

from locator_sweep.specs import Spec
from locator_sweep.fetcher import Fetcher


def main(args):
    spec = Spec.for_tag(args.tag)
    f = Fetcher(spec)

    rslt = f.page(args.lat, args.lon)
    for (ix, rec) in enumerate(rslt):
        print(ix, rec)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tag")
    parser.add_argument("lat", type=float)
    parser.add_argument("lon", type=float)
    logging.basicConfig(level=logging.INFO)
    main(parser.parse_args())
