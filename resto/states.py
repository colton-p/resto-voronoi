USA_48 = [
    'al', 'ar', 'az', 'ca', 'co', 'ct', 'de', 'fl', 'ga', 'ia', 'id', 'il', 'in', 'ks', 'ky', 'la', 'ma', 'md', 'me', 'mi', 'mn', 'mo',
    'ms', 'mt', 'nc', 'nd', 'ne', 'nh', 'nj', 'nm', 'nv', 'ny', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'tx', 'ut', 'va', 'vt', 'wa', 'wi', 'wv', 'wy'
]
USA_50 = USA_48 + ['ak', 'hi']

CANADA = [
    'nl', 'pe', 'ns', 'nb', 'qc', 'on',
    'mb', 'sk', 'ab', 'bc', 'yt', 'nt', 'nu',
]

USA_ALIASES = {
    'usa': USA_48,
}
CANADA_ALIASES = {
    'canada': CANADA,
    'north': ['nt', 'nu', 'yt'],
    'atlantic': ['nl', 'pe', 'nb', 'ns'],
}