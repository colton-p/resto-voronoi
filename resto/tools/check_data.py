import os

from resto.population import paths
from resto.shapes import loader as shape_loader
from resto.locations import DB_PATH

def shape_path(path):
    return os.path.join(
        shape_loader.SHAPES_DIR,
        path + '.shp'
    )


reqs = [
    (
        "canada census tables",
        paths.Canada.table_path(),
        "need 98-401-X2021006 from https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm?Lang=E",
    ),
    (
        "canada population",
        paths.Canada.population_path(),
        "run population/extract_pop_canada.py",
    ),
    (
        "us census tables",
        paths.US.table_path("wy"),
        'need state .pl files from https://www.census.gov/data/datasets/2020/dec/2020-census-redistricting-summary-file-dataset.html ("Legacy Format")',
    ),
    (
        "us population",
        paths.US.population_path("wy"),
        "run population/extract_pop_us.py",
    ),
    (
        "canada province shapes",
        shape_path(shape_loader.CanadaShapeLoader("on").state_shapefile),
        "province boundaries: https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?year=21",
    ),
    (
        "canada census shapes",
        shape_path(shape_loader.CanadaShapeLoader("on").census_shapefiles[0]),
        "dissemination area boundaries: https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?year=21",
    ),
    (
        "us state shapes",
        shape_path(shape_loader.UsaShapeLoader("wy").state_shapefile),
        "States 1:20,000,000 (national) from https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2022.html",
    ),
    (
        "us census shapes",
        shape_path(shape_loader.UsaShapeLoader("wy").census_shapefiles[0]),
        "Census Block Groups 1:500,000 (state) from https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2022.html",
    ),
    (
        "locations db",
        DB_PATH,
        "create data/output/locations/locations.db from data/output/locations/locations_schema.sql"
    )
]

def main():
    if "RESTO_DATA_DIR" not in os.environ:
        print("set RESTO_DATA_DIR to path_to_repo/data/")
        return

    for label, path, help in reqs:
        if os.path.exists(path):
            print(f"{label}... ok✅")
        else:
            print(f"{label}... ng❌")
            print(f"\t{path} missing")
            print(f"\t{help}")


if __name__ == "__main__":
    main()
