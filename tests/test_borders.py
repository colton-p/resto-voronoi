from resto.borders import Borders

def test_borders():
    b = Borders.for_state('wy')
    assert len(b.polygons()) == 1

def test_borders_us():
    b = Borders.for_state('usa')
    (min_lat, min_lon, max_lat, max_lon) = b.hull().bounds
    print(b.hull().bounds)
    assert 24 <= min_lat <= 25
    assert 49 <= max_lat <= 50
    assert -125 <= min_lon <= -124
    assert -67 <= max_lon <= -66
