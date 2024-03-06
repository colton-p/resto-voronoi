from resto.shapes import loader as shape_loader

def test_state_border_us():
    ((geo_id, polys),) = shape_loader.state_borders('wy')
    assert geo_id == '56'
    assert len(polys) == 1
    (poly,) = polys
    assert len(poly.exterior.coords) == 34

def test_state_border_ca():
    ((geo_id, polys),) = shape_loader.state_borders('sk')
    assert geo_id == '47'
    assert len(polys) == 1
    (poly,) = polys
    assert len(poly.exterior.coords) == 119

def test_census_border():
    rslt = list(shape_loader.census_borders('wy'))

    assert len(rslt) == 457
    (geo_id, polys) = rslt[0]
    assert geo_id == '560099566001'
    assert len(polys) == 1

def test_census_border_ca():
    return
    rslt = list(shape_loader.census_borders('sk'))

    assert len(rslt) == 2625
    (geo_id, polys) = rslt[0]
    assert geo_id == '47010137'
    assert len(polys) == 1