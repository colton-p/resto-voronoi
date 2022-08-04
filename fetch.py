import map
import requests
import json
import os


class Tims:
    tag = 'tims'

    def fetch(lat=43.5, lon=-80.5, radius=100, first=1000):
        def get_restaurants_gql(lat=43.5, lon=-80.5, radius=5000, first=100):
            url = 'https://use1-prod-th.rbictg.com/graphql'

            headers = {
                'content-type': 'application/json'
            }

            data = [{
                "operationName": "GetRestaurants",
                "variables": {
                    "input": {
                        "filter": "NEARBY",
                        "coordinates": {"userLat": lat, "userLng": lon, "searchRadius": radius},
                        "first": first
                    }
                },
                "query": "query GetRestaurants($input: RestaurantsInput) {\n  restaurants(input: $input) {\n    pageInfo {\n      hasNextPage\n      endCursor\n      __typename\n    }\n    totalCount\n    nodes {\n      ...RestaurantNodeFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment RestaurantNodeFragment on RestaurantNode {\n  _id\n  storeId\n  isAvailable\n  posVendor\n  chaseMerchantId\n  curbsideHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  deliveryHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  diningRoomHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  distanceInMiles\n  drinkStationType\n  driveThruHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  driveThruLaneType\n  email\n  environment\n  franchiseGroupId\n  franchiseGroupName\n  frontCounterClosed\n  hasBreakfast\n  hasBurgersForBreakfast\n  hasCatering\n  hasCurbside\n  hasDelivery\n  hasDineIn\n  hasDriveThru\n  hasTableService\n  hasMobileOrdering\n  hasLateNightMenu\n  hasParking\n  hasPlayground\n  hasTakeOut\n  hasWifi\n  hasLoyalty\n  id\n  isDarkKitchen\n  isFavorite\n  isHalal\n  isRecent\n  latitude\n  longitude\n  mobileOrderingStatus\n  name\n  number\n  parkingType\n  phoneNumber\n  physicalAddress {\n    address1\n    address2\n    city\n    country\n    postalCode\n    stateProvince\n    stateProvinceShort\n    __typename\n  }\n  playgroundType\n  pos {\n    vendor\n    __typename\n  }\n  posRestaurantId\n  restaurantImage {\n    asset {\n      _id\n      metadata {\n        lqip\n        palette {\n          dominant {\n            background\n            foreground\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    crop {\n      top\n      bottom\n      left\n      right\n      __typename\n    }\n    hotspot {\n      height\n      width\n      x\n      y\n      __typename\n    }\n    __typename\n  }\n  restaurantPosData {\n    _id\n    __typename\n  }\n  status\n  vatNumber\n  __typename\n}\n\nfragment OperatingHoursFragment on OperatingHours {\n  friClose\n  friOpen\n  monClose\n  monOpen\n  satClose\n  satOpen\n  sunClose\n  sunOpen\n  thrClose\n  thrOpen\n  tueClose\n  tueOpen\n  wedClose\n  wedOpen\n  __typename\n}\n"
            }]

            data_raw = '[{"operationName":"GetRestaurants","variables":{"input":{"filter":"NEARBY","coordinates":{"userLat":43.5,"userLng":-80.5,"searchRadius":100000},"first":2000}},"query":"query GetRestaurants($input: RestaurantsInput) {\n  restaurants(input: $input) {\n    pageInfo {\n      hasNextPage\n      endCursor\n      __typename\n    }\n    totalCount\n    nodes {\n      ...RestaurantNodeFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment RestaurantNodeFragment on RestaurantNode {\n  _id\n  storeId\n  isAvailable\n  posVendor\n  chaseMerchantId\n  curbsideHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  deliveryHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  diningRoomHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  distanceInMiles\n  drinkStationType\n  driveThruHours {\n    ...OperatingHoursFragment\n    __typename\n  }\n  driveThruLaneType\n  email\n  environment\n  franchiseGroupId\n  franchiseGroupName\n  frontCounterClosed\n  hasBreakfast\n  hasBurgersForBreakfast\n  hasCatering\n  hasCurbside\n  hasDelivery\n  hasDineIn\n  hasDriveThru\n  hasTableService\n  hasMobileOrdering\n  hasLateNightMenu\n  hasParking\n  hasPlayground\n  hasTakeOut\n  hasWifi\n  hasLoyalty\n  id\n  isDarkKitchen\n  isFavorite\n  isHalal\n  isRecent\n  latitude\n  longitude\n  mobileOrderingStatus\n  name\n  number\n  parkingType\n  phoneNumber\n  physicalAddress {\n    address1\n    address2\n    city\n    country\n    postalCode\n    stateProvince\n    stateProvinceShort\n    __typename\n  }\n  playgroundType\n  pos {\n    vendor\n    __typename\n  }\n  posRestaurantId\n  restaurantImage {\n    asset {\n      _id\n      metadata {\n        lqip\n        palette {\n          dominant {\n            background\n            foreground\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    crop {\n      top\n      bottom\n      left\n      right\n      __typename\n    }\n    hotspot {\n      height\n      width\n      x\n      y\n      __typename\n    }\n    __typename\n  }\n  restaurantPosData {\n    _id\n    __typename\n  }\n  status\n  vatNumber\n  __typename\n}\n\nfragment OperatingHoursFragment on OperatingHours {\n  friClose\n  friOpen\n  monClose\n  monOpen\n  satClose\n  satOpen\n  sunClose\n  sunOpen\n  thrClose\n  thrOpen\n  tueClose\n  tueOpen\n  wedClose\n  wedOpen\n  __typename\n}\n"}]' \

            resp = requests.post(url, headers=headers, data=json.dumps(data))
            print(resp.status_code)

            result = resp.json()
            return result

        data = get_restaurants_gql(lat, lon, radius*1000, first)

        total = data[0]['data']['restaurants']['totalCount']
        nodes = data[0]['data']['restaurants']['nodes']

        if total > len(nodes):
            print('!!!', (lat, lon, radius, first),
                  f'got {len(nodes)} of {total} total')

        return {node['_id']: node for node in nodes}

    def clean(data):
        # id,name,lat,lon
        return [
            (id, node['name'], node['latitude'], node['longitude'])
            for (id, node) in data.items()
        ]


class Mcds:
    tag = 'mcds'

    def fetch(lat=43.5, lon=-80.5, radius=100, first=1000):
        def _fetch(ctry, lat=43.5, lon=-80.5, radius=100, first=1000):
            url = 'https://www.mcdonalds.com/googleappsv2/geolocation'
            # query = f'?latitude={lat}&longitude={lon}&radius={radius}&maxResults={first}&showClosed=true'
            query = f'?latitude={lat}&longitude={lon}&radius={radius}&maxResults={first}&country={ctry}&language=en-ca&showClosed=true'

            resp = requests.get(url + query)
            try:
                data = resp.json()
            except:
                data = {'features': []}

            return {node['properties']['id']: node for node in data['features']}

        us = _fetch('us', lat, lon, radius, first)
        can = _fetch('ca', lat, lon, radius, first)
        return {**us, **can}

    def clean(data):
        return [
            (id, node['properties'].get('name') or node['properties'].get('customAddress') or node['properties']['longDescription'],
             node['geometry']['coordinates'][1],  # lat
             node['geometry']['coordinates'][0]  # lon
             ) for (id, node) in data.items()
        ]


class Sbux:
    tag = 'sbux'

    def fetch(lat=43.5, lon=-80.5, radius=100, first=1000):
        url = f'https://www.starbucks.ca/bff/locations?lat={lat}&lng={lon}&mop=true'  # &mop=true&place=Kitchener%2C%20ON%2C%20Canada' \

        headers = {
            'authority': 'www.starbucks.ca',
            'accept': 'application/json',
            'x-requested-with': 'XMLHttpRequest',
        }

        resp = requests.get(url, headers=headers)
        print(resp.status_code)

        result = resp.json()

        return {node['id']: node for node in result['stores']}

    def clean(data):
        return [
            (id, node['name'],
             node['coordinates']['latitude'],  # lat
             node['coordinates']['longitude']  # lon
             ) for (id, node) in data.items()
        ]


def fetch(cls, lat, lon, radius=100):
    filename = f'{cls.tag}_{lat:.3f}_{lon:.3f}_{radius}.json'

    if os.path.exists(f'raw_data/full/{filename}'):
        return -1

    data = cls.fetch(lat, lon, radius, first=1000)
    short = cls.clean(data)

    with open(f'raw_data/full/{filename}', 'w') as f:
        json.dump(data, f, indent=2)
    with open(f'raw_data/short/{filename}', 'w') as f:
        json.dump(short, f, indent=2)

    return len(data)


def main():
    pp = []

    #N = len(map.ALL_POINTS)
    N = len(map.NORTH)
    # for (ix, (lat, lon)) in enumerate(map.ALL_POINTS):
    for (ix, (lat, lon)) in enumerate(map.NORTH):
        print(f'{1+ix}/{N}', (lat, lon),
              fetch(Tims, lat, lon, radius=100),
              fetch(Mcds, lat, lon, radius=100),
              fetch(Sbux, lat, lon, radius=100)
              )


main()
