from haversine import inverse_haversine
import folium
import math
import pathlib
import json
m = folium.Map(location=[43.5, -80.5])


def circle(lat, lon, r=100):
    points = []
    for ix in range(0, 24):
        heading = math.pi*2 * ix / 24
        points += [inverse_haversine((lat, lon), r, heading)]

    return points


ALL = set()
for file in sorted(pathlib.Path('raw_data/short/').glob(f'sbux_*.json')):
    [_, lat, lon, _r] = file.name.split('_')
    lat = float(lat)
    lon = float(lon)

    locals = {x[0] for x in json.load(file.open())}
    n_local = len(locals)
    # n_uniq = len(locals - ALL)

    ALL |= locals

    folium.CircleMarker(
        location=(lat, lon),
        tooltip=f'{n_local}',
        radius=5,
        fill=True
    ).add_to(m)


m.save('map2.html')
