import logging
import json
import os
import requests

from locator_sweep.specs import Spec, StoreRecord

class Fetcher:
    def __init__(self, spec: Spec):
        self.spec: Spec = spec

    @property
    def max_range(self):
        return self.spec.max_range

    def url(self, lat, lon):
        # TODO: build properly
        qs = '&'.join(f'{k}={v}' for (k, v) in self.spec.query_args(lat, lon).items())
        return f'{self.spec.base_url}?{qs}'

    def page(self, lat, lon):
        filename = f'{self.spec.__class__.__name__}_{lat:.4f}_{lon:.4f}.json'
        path = f'./.cache/{filename}'

        if os.path.exists(path):
            with open(path, 'r', encoding='utf8') as infile:
                return [StoreRecord(*r) for r in json.load(infile)]

        data = self._page(lat, lon)

        json.dump(data, open(path, 'w', encoding='utf8'))
        return data

    def _page(self, lat, lon):
        url = self.url(lat, lon)
        headers = self.spec.headers()

        logging.info('fetch %s', url)
        if self.spec.method == 'post':
            body = '&'.join(f'{k}={v}' for (k, v) in self.spec.form_body(lat, lon).items())
            resp = requests.post(url, headers=headers, data=body, timeout=10)
  
        else:
            resp = requests.get(url,headers=headers, timeout=10)
        if resp.status_code != 200:
            print(resp.status_code)
            print(resp.text)
            raise Exception(resp.status_code, resp.text)
        result = resp.json()

        full = self.spec.unpack(result)
        return [self.spec.clean(node) for node in full.values()]