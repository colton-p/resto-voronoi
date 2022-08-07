import time
from collections import Counter
import da_shapes
import folium

from shapely.geometry import Polygon, MultiPolygon, box as Box, Point
from voronoi import Vor

COLOR = {
    'tims': 'crimson',
    'mcds': 'yellow',
    'sbux': 'green',
}


def plot_points(points_dict):
    for (tag, points) in points_dict.items():
        for pt in points:
            folium.CircleMarker(
                location=pt,
                color=COLOR[tag],
                radius=5,
                fill=False
            ).add_to(m)


def plot_region(m: folium.Map, tag, region: Polygon, desc=''):
    folium.Polygon(
        region.exterior.coords,
        color=COLOR[tag],
        # fill_color='white',
        radius=5,
        fill=True,
        tooltip=desc,
        # fill_opacity=0,
    ).add_to(m)


def plot_overlap(tag, overlap):
    if isinstance(overlap, MultiPolygon):
        polys = list(overlap.geoms)
    else:
        polys = [overlap]
    for poly in polys:
        folium.Polygon(
            poly.exterior.coords,
            color=COLOR[tag],
            radius=5,
            fill=True,
            weight=0,
        ).add_to(m)


def hull_for_das(das):
    all_das = MultiPolygon(da.poly for da in das)
    return all_das.convex_hull


def overlap_pop(region, da):
    overlap = region.intersection(da.poly)
    pct = overlap.area / da.poly.area
    pop = round(pct*da.pop)

    return pop


def compute_overlaps(regions, das):
    n_overlaps = 0
    totals = Counter()

    for (ix, (tag, region)) in enumerate(regions):
        if ix % 100 == 0:
            print('\t', ix, '...')

        reg_pop = 0
        reg_n = 0
        for da in das:
            if not region.intersects(da.poly):
                continue

            pop = overlap_pop(region, da)
            n_overlaps += 1
            reg_n += 1
            reg_pop += pop
            totals[tag] += pop
        plot_region(m, tag, region, f'tag={tag} pop={reg_pop} n={reg_n}')

    return totals, n_overlaps


def compute_overlaps2(regions, das):
    n_overlaps = 0
    totals = Counter()

    remaining_das = {da.id: da for da in das}

    for (ix, (tag, region)) in enumerate(regions):
        if ix % 1000 == 0:
            print('\t', ix, '...', len(remaining_das))

        reg_pop = reg_n = 0
        covered_das = set()
        for da in remaining_das.values():
            if not region.intersects(da.poly):
                continue

            if region.covers(da.poly):
                covered_das.add(da.id)

            pop = overlap_pop(region, da)
            n_overlaps += 1
            reg_n += 1
            reg_pop += pop
            totals[tag] += pop
        plot_region(m, tag, region, f'tag={tag} pop={reg_pop} n={reg_n}')

        # for k in covered_das:
        #    del remaining_das[k]
        remaining_das = {
            k: v for (k, v) in remaining_das.items() if k not in covered_das}

    print(len(das), '-->', len(remaining_das))
    return totals, n_overlaps


PREFIX = '3530'
PLOT_DAS = True
PLOT_POINTS = True


t0 = time.time()
das = list(da_shapes.da_for_prefix(PREFIX))
t1 = time.time()
print('das time:', t1-t0)
das_hull = hull_for_das(das)

m = folium.Map(location=das_hull.representative_point().coords[0])

if PLOT_DAS:
    for da in das:
        folium.Polygon(da.poly.exterior.coords, color='blue',
                       fill=False, weight=1, dash_array='4').add_to(m)

V = Vor.within(das_hull)
points = V.points
print('points:', ' '.join(f'{t}={len(p)}' for (t, p) in points.items()))
if PLOT_POINTS:
    plot_points(points)

regions = V.clipped_regions(das_hull, finite=True)
print(
    f'regions:', f'shapes={len(regions)} points={sum(len(r[1].exterior.coords) for r in regions)}'
)


t0 = time.time()
totals, n_overlaps = compute_overlaps2(regions, das)
t1 = time.time()
print('overlap time:', t1-t0)

print(f'overlaps={n_overlaps}')
print('')
print(f'total={sum(totals.values())} da_total={sum(da.pop for da in das)}')
print(dict(totals))
m.save('overlap.html')
