import logging
import json
import os
import requests
import time

from locator_sweep.specs import Spec, StoreRecord, LatLon

CACHE_DIR = os.environ.get('RESTO_CACHE_DIR', os.environ['HOME'] + '/.resto-cache')

def load_store_record(data):
    (id, name, city, state, country, (lat, lon)) = data
    return StoreRecord(
        id, name, city, state, country,
        point=LatLon(lat, lon)
    )

def _retried_fetch(func, retries=5, delay=10):
    tries = 0
    while tries < retries:
        try:
            resp = func()
            if resp.status_code != 200:
                print(resp.status_code)
                print(resp.text)
                raise Exception(resp.status_code, resp.text)
            return resp
        except Exception as err:
            tries += 1
            logging.error('fetch %d failed: %s', tries, err)
            logging.info('retry in %d s', delay)
            time.sleep(delay)
            delay *= 2
    
    assert False
    return None

class Fetcher:
    def __init__(self, spec: Spec):
        self.spec: Spec = spec

    def max_range(self, lat, lon):
        return self.spec.max_range(lat, lon)

    def url(self, lat, lon):
        # TODO: build properly
        qs = '&'.join(f'{k}={v}' for (k, v) in self.spec.query_args(lat, lon).items())
        return f'{self.spec.base_url}?{qs}'

    def page(self, lat, lon, force=False):
        filename = f'{self.spec.__class__.__name__}_{lat:.4f}_{lon:.4f}.json'
        path = os.path.join(CACHE_DIR, filename)

        if os.path.exists(path) and not force:
            with open(path, 'r', encoding='utf8') as infile:
                return [load_store_record(r) for r in json.load(infile)]

        data = self._page(lat, lon)

        json.dump(data, open(path, 'w', encoding='utf8'))
        return data

    def _page(self, lat, lon):
        url = self.url(lat, lon)
        headers = self.spec.headers()

        logging.info('fetch %s', url)
        if self.spec.method == 'post':
            body = '&'.join(f'{k}={v}' for (k, v) in self.spec.form_body(lat, lon).items())
            func = lambda: requests.post(url, headers=headers, data=body, timeout=30)
  
        else:
            func = lambda: requests.get(url,headers=headers, timeout=10)
        resp = _retried_fetch(func)
        if resp.status_code != 200:
            print(resp.status_code)
            print(resp.text)
            raise Exception(resp.status_code, resp.text)
        result = resp.json()

        full = self.spec.unpack(result)
        return [self.spec.clean(node) for node in full.values()]