from haversine import inverse_haversine
import folium
import math
m = folium.Map(location=[43.5, -80.5])


def circle(lat, lon, r=100):
    points = []
    for ix in range(0, 24):
        heading = math.pi*2 * ix / 24
        points += [inverse_haversine((lat, lon), r, heading)]

    return points


def rect(lat1, lat2, lon1, lon2, step=1):
    points = []
    for lat_ix in range(int(lat1/step), int(lat2/step)):
        for lon_ix in range(int(lon1/step), int(lon2/step)):
            lat = lat_ix * step
            lon = lon_ix * step
            points += [(lat, lon)]
            # points += [(lat, lon)]  # circle(lat, lon)]
    return points


xALL_POINTS = [
    (rect(43, 49, -84, -75), 100, 'grey'),
    (rect(43, 45, -80, -78, 0.5), 50, 'grey'),
    (rect(49, 65, -140, -50), 100, 'grey'),
    (rect(45, 49, -75, -50), 100, 'purple'),
    ([(44, -65)], 100, 'red'),
]

if __name__ == "__main__":
    for (lat, lon) in []:
        folium.Polygon(
            circle(lat, lon, 50),
            color='purple',
            width=1,
            fill=True).add_to(m)

    m.save('map.html')
    exit()
