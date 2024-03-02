"""
a Spec holds API details and can unpack into StoreRecord[]
"""

from collections import namedtuple
import json
import urllib.parse
from bs4 import BeautifulSoup

StoreRecord = namedtuple("StoreRecord", ["id", "name", "city", "state", "country", "point"])
LatLon = namedtuple("LatLon", ["lat", "lon"])


class Spec:
    base_url = None
    _max_range = 50_000
    method = 'get'

    @staticmethod
    def for_tag(tag):
        return _spec_map[tag]()
    
    def max_range(self, _lat, _lon):
        return self._max_range

    def query_args(self, _lat, _lon):
        return {}

    def headers(self):
        return {}

    def data(self, result):
        return result.json()

    def unpack(self, _data) -> dict:
        return

    def clean(self, _node) -> StoreRecord: ...


class McDonalds(Spec):
    base_url = "https://www.mcdonalds.com/googleappsv2/geolocation"
    _max_range = 20_000
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
            city=node["properties"]["address3"],
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
    _max_range = 80_000

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
            city=node["address"]["city"],
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
        (country, state) = node["address"]["region"]["isocode"].split("-")
        return StoreRecord(
            id=str(node["id"]),
            name=node["displayName"],
            city=node['address']['town'],
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

    def body(self, lat, lon):
        body = {
            "lat": float(lat),
            "lng": float(lon),
        }

        return '&'.join(f'{k}={v}' for (k, v) in body.items())

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
        address_el = soup.find(class_="amlocator-info-address")
        desc = soup.find(class_="amlocator-store-map-name").get_text()
        return StoreRecord(
            id=str(node["id"]),
            name=desc,
            city=list(address_el.stripped_strings)[-1],
            state="ON",
            country="CA",
            point=LatLon(lat=float(node["lat"]), lon=float(node["lng"])),
        )


class TimHortons(Spec):
    base_url = "https://use1-prod-th.rbictg.com/graphql"
    method = 'post'
    max_range = 100_000

    def max_range(self, lat, lon):
        return 100_000
        if lat >= 60:
            return 500_000
        if lat >= 50:
            return 100_000
        if lat >= 45:
            return 50_000
        return 20_000

    def query_args(self, _lat, _lon):
        return {}
    
    def body(self, lat, lon):
        rad = self.max_range(lat, lon)
        body = [
            {"operationName": "GetRestaurants",
             "variables":{"input":{"filter":"NEARBY","coordinates":{"userLat":lat,"userLng":lon,"searchRadius":rad},"first":100,"status":"OPEN"}},
             "query": "query GetRestaurants($input: RestaurantsInput) {\n  restaurants(input: $input) {\n    pageInfo {\n      hasNextPage\n      endCursor\n      __typename\n    }\n    totalCount\n    nodes {\n      ...RestaurantNodeFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment RestaurantNodeFragment on RestaurantNode {\n  _id\n  storeId\n  isAvailable\n  posVendor\n  chaseMerchantId\n  cateringHours {\n    ...OperatingHoursFragment\n    ...OperatingHoursFragment\n    __typename\n  }\n  curbsideHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  cateringHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  timezone\n  deliveryHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  diningRoomHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  distanceInMiles\n  drinkStationType\n  driveThruHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  driveThruLaneType\n  email\n  environment\n  franchiseGroupId\n  franchiseGroupName\n  frontCounterClosed\n  hasBreakfast\n  hasBurgersForBreakfast\n  hasCatering\n  hasCurbside\n  hasDelivery\n  hasDineIn\n  hasDriveThru\n  hasTableService\n  hasMobileOrdering\n  hasLateNightMenu\n  hasParking\n  hasPlayground\n  hasTakeOut\n  hasWifi\n  hasLoyalty\n  id\n  isDarkKitchen\n  isFavorite\n  isHalal\n  isRecent\n  latitude\n  longitude\n  mobileOrderingStatus\n  name\n  number\n  parkingType\n  phoneNumber\n  physicalAddress {\n    address1\n    address2\n    city\n    country\n    postalCode\n    stateProvince\n    stateProvinceShort\n    __typename\n  }\n  playgroundType\n  pos {\n    vendor\n    __typename\n  }\n  posRestaurantId\n  restaurantImage {\n    asset {\n      _id\n      metadata {\n        lqip\n        palette {\n          dominant {\n            background\n            foreground\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    crop {\n      top\n      bottom\n      left\n      right\n      __typename\n    }\n    hotspot {\n      height\n      width\n      x\n      y\n      __typename\n    }\n    __typename\n  }\n  restaurantPosData {\n    _id\n    __typename\n  }\n  status\n  vatNumber\n  timezone\n  __typename\n}\n\nfragment OperatingHoursFragment on OperatingHours {\n  friClose\n  friOpen\n  monClose\n  monOpen\n  satClose\n  satOpen\n  sunClose\n  sunOpen\n  thrClose\n  thrOpen\n  tueClose\n  tueOpen\n  wedClose\n  wedOpen\n  __typename\n}\n",
            }
        ]
        return json.dumps(body)


    def headers(self):
        return {'content-type': 'application/json'}

    def unpack(self, data) -> dict:
        return {node['storeId']: node for node in data[0]['data']['restaurants']['nodes']}

    def clean(self, node) -> StoreRecord:
        return StoreRecord(
            id=node['storeId'],
            name=node['physicalAddress']['address1'],
            city=node['physicalAddress']['city'],
            state=node['physicalAddress']['stateProvinceShort'],
            country=node['physicalAddress']['country'],
            point=LatLon(lat=float(node["latitude"]), lon=float(node["longitude"])),
        )

class Subway(Spec):
    base_url = "https://locator-svc.subway.com/v3/GetLocations.ashx"
    _max_range = 200_000

    def query_args(self, lat, lon):
        query = {
            "InputText": "",
            "GeoCode": {
                "Latitude": lat,
                "Longitude": lon,
            },
            "DetectedLocation": {"Latitude": 0, "Longitude": 0, "Accuracy": 0},
            "Paging": {"StartIndex": 1, "PageSize": 50},
            "ConsumerParameters": {
                "metric": True, "culture": "en-US", "size": "D", "template": "order2modal", "rtl": False, "clientId": "31", "key": "SUBWAY_ORDER_PROD",
            },
            "Filters": [],
            "LocationType": 1,
            "behavior": "",
            "FavoriteStores": None,
            "RecentStores": None,
            "Stats": { "abc": "geo,A", "src": "geocode", "act": "enter", "c": "subwayLocator", "pac": "0,0", },
        }
        encoded_query = urllib.parse.quote(json.dumps(query))
        return {
            "callback": "jQuery31107413341582997099_1709388434457",
            "q": encoded_query,
        }

    def headers(self):
        return {
            "authority": "locator-svc.subway.com",
            "referer": "https://www.subway.com/",
        }
    
    def data(self, result):
        # result is jQuery31107413341582997099_1709388434457(json)
        return json.loads(result.text[41:-1])

    def unpack(self, data):
        return {node["LocationId"]["StoreNumber"]: node for node in data["ResultData"]}

    def clean(self, node) -> StoreRecord:
        address = node["Address"]
        return StoreRecord(
            id=str(node["LocationId"]["StoreNumber"]),
            name=address["Address1"],
            city=address["City"],
            state=address["StateProvCode"],
            country=address["CountryCode"],
            point=LatLon(
                lat=node["Geo"]["Latitude"],
                lon=node["Geo"]["Longitude"],
            ),
        )



_spec_map = {
    "sb": Starbucks,
    "ct": CanadianTire,
    "mc-ca": McDonaldsCA,
    "mc-us": McDonaldsUS,
    "lcbo": LCBO,
    "tims": TimHortons,
    "subway": Subway,
}
