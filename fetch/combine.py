import pathlib
import json


def combine_full(tag):
    results = {}
    for file in pathlib.Path('raw_data/full/').glob(f'{tag}_*.json'):

        data = json.load(file.open())

        results = {**results, **data}

        print(len(results), len(data))

    with open(f'data/{tag}_full.json', 'w') as f:
        json.dump(list(results.values()), f, indent=2)


def combine(tag):
    results = {}
    count = 0
    for file in pathlib.Path('raw_data/short/').glob(f'{tag}_*.json'):
        data = {row[0]: row for row in json.load(file.open())}
        results = {**results, **data}
        count += len(data)

    print(tag, len(results), count)

    with open(f'data/{tag}.json', 'w') as f:
        json.dump(list(results.values()), f, indent=2)


combine_full('tims')
combine_full('mcds')
combine_full('sbux')
