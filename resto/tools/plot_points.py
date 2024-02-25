import folium

from resto.borders import Borders
from resto.census_area import CensusArea
from resto.map import Map
from resto import locations as location_loader
from resto.overlap import compute_overlaps2, compute_overlaps_strtree
from resto.voronoi import Vor

COLOR = {'mc-us': 'yellow', 'sb-us': 'blue'}


def plot_points(m, points_dict):
    for (tag, points) in points_dict.items():
        for pt in points:
            m.plot_location(pt)

m = Map()
# border shape --> Borders
# swept data --> Location --Vor--> VorRegion --> |
# census shape                                   | compute overlap --> PopRegion
# population  |  -->      CensusArea        ---> |
#

import sys
import logging
ST = sys.argv[1]

logging.basicConfig(level=logging.INFO)

bounds = Borders.for_state(ST)
census_areas = list(CensusArea.for_state(ST))

# points = location_loader.for_state(['sb-us', 'mc-us'], ST)
points = location_loader.within(['sb-us', 'mc-us'], bounds.multipoly())
print(len(census_areas), 'census areas')
vor_regions = Vor(points).clipped_regions(bounds.hull(), finite=True)
print(len(vor_regions), 'locations')

overlaps = compute_overlaps_strtree(census_areas, vor_regions)


m.plot_border(bounds)
#for (tag, region) in vor_regions:
#    m.plot_region(tag, region)
#m.plot_census_areas(census_areas)
for x in overlaps:
    m.plot_pop_region(x)
plot_points(m, points)

m.m.save('out.html')

from collections import Counter
rslt = Counter()
for o in overlaps:
    rslt[o.tag] += o.pop

for x in rslt.most_common():
    print(x)
