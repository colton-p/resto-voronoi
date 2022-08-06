#import matplotlib
import near
import csv
import shapefile
import pyproj
import folium
import itertools
import haversine


def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b, None)
    return tuple(zip(a, b))


can_txer = pyproj.Transformer.from_crs(3347, 4326)
def can_tx(x, y): return can_txer.transform(x, y)
def us_tx(x, y): return y, x


# us = shapefile.Reader('shapes/us/cb_2018_us_nation_20m')
# can = shapefile.Reader('shapes/canada/lpr_000a21a_e', encoding='latin1')
m = folium.Map(location=[43.5, -80.5])


def rect(lat1, lat2, lon1, lon2, step=1):
    points = []
    for lat_ix in range(int(lat1/step), int(lat2/step)):
        for lon_ix in range(int(lon1/step), int(lon2/step)):
            lat = lat_ix * step
            lon = lon_ix * step
            points += [(lat, lon)]
    return points


def shape_to_polys(shape, tx):
    part_ixs = pairwise(list(shape.parts) + [len(shape.points)])

    return [
        [tx(*point) for point in shape.points[start:end]]
        for (start, end) in part_ixs
    ]


def sf_to_polys(sf, tx):
    for shape in sf.iterShapes():
        for poly in shape_to_polys(shape, tx):
            yield poly


def plot_shape(m, shape, tx):
    for (ix, poly) in enumerate(shape_to_polys(shape, tx)):
        folium.Polygon(poly).add_to(m)


def plot_sf(m, sf, tx):
    for poly in sf_to_polys(sf, tx):
        folium.Polygon(poly).add_to(m)


PREFIX = '3530'
POP = {}
with open('census/data/full.csv', 'r') as csvfile:
    for line in csv.reader(csvfile):
        if line[1][:4] == PREFIX:
            POP[line[0]] = int(line[-1])

sf = shapefile.Reader('shapes/canada_census/lda_000b21a_e')

for (ix, sr) in enumerate(sf.iterShapeRecords()):
    shape = sr.shape

    if sr.record[0][:4] != '3530':
        continue
    polys = shape_to_polys(shape, can_tx)
    if len(polys) > 1:
        continue
    poly = polys[0]

    pt = poly[0]
    if haversine.haversine(pt, (43.46, -80.53)) > 10:
        continue

    folium.Polygon(
        poly,
        fill=True,
        popup=f'id={sr.record[0]} pop={POP[sr.record[1]]}'
    ).add_to(m)
    print(ix, sr.record)

# near.near(m, (43.46, -80.53), 20)

m.save('shapes.html')


def xmain():
    paths = []
    good_points = []
    for shape in can.shapes():  # [:10]:
        paths += [
            matplotlib.path.Path(poly)
            for poly in shape_to_polys(shape, can_tx)
        ]
    paths += [
        matplotlib.path.Path(poly)
        for (ix, poly) in enumerate(sf_to_polys(us, us_tx))
        if ix == 35
    ]

    print(len(paths))
    c, t = 0, 0
    # for pt in rect(20, 65, -140, -50, step=0.5):
    for pt in rect(59, 75, -145, -55, step=0.5):
        t += 1
        if any(path.contains_points([pt])[0] for path in paths):
            c += 1
            good_points += [pt]
            folium.Circle(pt, color='red').add_to(m)
        else:
            folium.Circle(pt, color='grey').add_to(m)
    print(t, c)

    print(good_points)
    m.save('shapes.html')


#
# main()
#print('shapes:', len(us.shapes()))
