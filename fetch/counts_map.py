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


def adj(lat, lon, step=0.2):
    k = int(1 // step) // 2
    for i in range(-k, k):
        for j in range(-k, k):
            yield ('%.3f' % (lat + i * step), '%.3f' % (lon + j * step))


S = set()
T = set()

X = set()
t = 0
for file in sorted(pathlib.Path('raw_data/short/').glob(f'sbux_*.json')):
    t += 1
    [_, lat, lon, _r] = file.name.split('_')
    T.add((lat,lon))


    rslts = {x[0] for x in json.load(file.open())}
    n = len(rslts)

    if n == 50:
        X.add((lat, lon))

    lat = float(lat)
    lon = float(lon)
    if n == 50:
        S |= set(adj(lat, lon))



S_and_T = S & T

for pt in S | T:
    if pt in X:
        clr = 'orange'
    elif pt in S_and_T:
        clr = 'green'
    elif pt in T:
        clr = 'grey'
    elif pt in S:
        clr = 'red'

    folium.CircleMarker(
        location=tuple(map(float,pt)),
        radius=5,
        color=clr,
        fill=True
    ).add_to(m)


m.add_child(folium.LatLngPopup())
m.save('map2.html')

print(t)
print('T', len(T))
print('S', len(S))
print('S | T', len(S | T))
print('S & T', len(S & T), 'green')
print('T - S', len(T - S), 'grey')
print('S - T', len(S - T), 'red')


# json.dump(sorted(S-T), open('to_fetch.json', 'w'), indent=2)
