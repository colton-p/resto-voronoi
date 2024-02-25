"""
a Spec holds API details and can unpack into StoreRecord[]
"""

from collections import namedtuple
from bs4 import BeautifulSoup

StoreRecord = namedtuple("StoreRecord", ["id", "name", "state", "country", "point"])
LatLon = namedtuple("LatLon", ["lat", "lon"])


class Spec:
    base_url = None
    max_range = 20_000
    method = 'get'

    @staticmethod
    def for_tag(tag):
        return _spec_map[tag]()

    def query_args(self, _lat, _lon):
        return {}

    def headers(self):
        return {}

    def unpack(self, _data) -> dict:
        return

    def clean(self, _node) -> StoreRecord: ...


class McDonalds(Spec):
    base_url = "https://www.mcdonalds.com/googleappsv2/geolocation"
    max_range = 20_000
    country = None

    def query_args(self, lat, lon):
        return {
            "latitude": lat,
            "longitude": lon,
            "radius": 1000,
            "maxResults": 1000,
            "country": self.country,
            "language": "en-ca",
            "showClosed": True,
        }

    def unpack(self, data):
        return {node["properties"]["id"]: node for node in data["features"]}

    def clean(self, node):
        props = node["properties"]
        store_id = props["id"]
        name = (
            props.get("name") or props.get("customAddress") or props["longDescription"]
        )

        return StoreRecord(
            id=store_id,
            name=name,
            state=node["properties"]["subDivision"],
            country=store_id.split("-")[1],
            point=LatLon(
                lat=node["geometry"]["coordinates"][1],
                lon=node["geometry"]["coordinates"][0],
            ),
        )


class McDonaldsCA(McDonalds):
    country = "ca"


class McDonaldsUS(McDonalds):
    country = "us"


class Starbucks(Spec):
    base_url = "https://www.starbucks.ca/bff/locations"
    max_range = 80_000

    def query_args(self, lat, lon):
        return {
            "lat": lat,
            "lng": lon,
            "mop": "true",
        }

    def headers(self):
        return {
            "Accept": "application/json",
            "x-requested-with": "XMLHttpRequest",
        }

    def unpack(self, data):
        return {node["id"]: node for node in data["stores"]}

    def clean(self, node) -> StoreRecord:
        return StoreRecord(
            id=node["id"],
            name=node["name"],
            state=node["address"]["countrySubdivisionCode"],
            country=node["address"]["countryCode"],
            point=LatLon(
                lat=node["coordinates"]["latitude"],
                lon=node["coordinates"]["longitude"],
            ),
        )


class CanadianTire(Spec):
    base_url = "https://apim.canadiantire.ca/v1/store/stores"

    def query_args(self, lat, lon):
        return {
            "maxCount": 50,
            "type": "CTR_STORE",
            "latitude": float(lat),
            "longitude": float(lon),
            "language": "en_CA",
            "banner": "CTR",
        }

    def headers(self):
        return {
            "ocp-apim-subscription-key": "c01ef3612328420c9f5cd9277e815a0e",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "bannerid": "CTR",
            "basesiteid": "CTR",
        }

    def unpack(self, data):
        return {node["id"]: node for node in data["stores"]}

    def clean(self, node):
        (state, country) = node["address"]["region"]["isocode"].split("-")
        return StoreRecord(
            id=node["id"],
            name=node["displayName"],
            state=state,
            country=country,
            point=LatLon(
                lat=node["geoPoint"]["latitude"],
                lon=node["geoPoint"]["longitude"],
            ),
        )


class LCBO(Spec):
    base_url = "https://www.lcbo.com/en/amlocator/index/ajax/"
    method = "post"

    def query_args(self, _lat, _lon):
        return {}

    def form_body(self, lat, lon):
        return {
            "lat": float(lat),
            "lng": float(lon),
        }

    def headers(self):
        return {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
        }

    def unpack(self, data):
        return {node["id"]: node for node in data["items"]}

    def clean(self, node):
        soup = BeautifulSoup(node["popup_html"], "html.parser")
        desc = soup.find(class_="amlocator-info-address").get_text()
        return StoreRecord(
            id=node["id"],
            name=desc,
            state="",
            country="",
            point=LatLon(lat=float(node["lat"]), lon=float(node["lng"])),
        )


_spec_map = {
    "sb": Starbucks,
    "ct": CanadianTire,
    "mc-ca": McDonaldsCA,
    "mc-us": McDonaldsUS,
    "lcbo": LCBO,
}
