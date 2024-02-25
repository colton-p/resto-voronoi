import logging

from locator_sweep.visualizer import Visualizer
from locator_sweep.sweeper import Sweeper

def collect_points(sweeper: Sweeper, max_iters=10):
    out_points = set()
    for points in sweeper.sweep(max_iters):
        out_points |= points
    return list(out_points)

def collect_points_visualize(sweeper: Sweeper, max_iters=10):
    viz = Visualizer(sweeper)

    out_points = set()
    for (ix, points) in enumerate(sweeper.sweep(max_iters)):
        out_points |= points
        logging.info('iter=%d queries=%d points=%d covered=%.3f', ix, sweeper.queries, len(out_points), sweeper.percent_covered())

        viz.add_features(sweeper, points)
    
    viz.add_points(out_points)
    viz.finalize()

    return list(out_points), viz.map