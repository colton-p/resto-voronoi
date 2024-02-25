from typing import List
import folium
from resto.census_area import CensusArea
from resto.locations import Location
from resto.overlap import PopRegion
from resto.voronoi import VorRegion
from shapely.geometry import Polygon

from resto.borders import Borders

COLOR = {
    'sb-us': 'green',
    'sb-ca': 'green',
    'mc-us': 'yellow',
    'mc-ca': 'yellow',
}


class Map:
    def __init__(self) -> None:
        self.m = folium.Map(prefer_canvas=True)

    def plot_border(self, borders: Borders):
        folium.Polygon(
            borders.main().buffer(0.01).exterior.coords,
            color="cyan"
        ).add_to(self.m)
    
    def plot_census_areas(self, census_areas: List[CensusArea]):
        for ca in census_areas:
            folium.Polygon(
                ca.points(),
                color='blue',
                fill=False,
                weight=1,
                dash_array='4',
                tooltip=f'{ca.id} {ca.pop}'
            ).add_to(self.m)

    def plot_location(self, location: Location):
        folium.CircleMarker(
            location=location.point,
            color='black',#COLOR.get(location.tag, 'black'),
            radius=5,
            fill=False,
            tooltip=f'{location.name}'
        ).add_to(self.m)

    def plot_polygon(self, region: Polygon, color=None, desc=None):
        folium.Polygon(
            region.exterior.coords,
            color=color,
            radius=5,
            fill=True,
            tooltip=desc,
            # fill_color='white',
            # fill_opacity=0,
        ).add_to(self.m)
    
    def plot_vor_region(self, vor_region: VorRegion):
        self.plot_polygon(vor_region.poly, COLOR[vor_region.tag])
    
    def plot_pop_region(self, pop_region: PopRegion):
        (tag, poly, reg_pop, reg_n) = pop_region
        self.plot_polygon(
            poly,
            color=COLOR[tag],
            desc=f'tag={tag} pop={reg_pop} n={reg_n}'
        )
