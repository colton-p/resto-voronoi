import os

DATA_DIR = os.environ['RESTO_DATA_DIR']
BASE_DIR = os.path.join(DATA_DIR, 'input', 'census')
class US:
    @staticmethod
    def header_path(state):
        return os.path.join(
            BASE_DIR,
            'us',
            f'{state}2020.pl',
            f'{state}geo2020.pl'
        )

    @staticmethod
    def table_path(state):
        return os.path.join(
            BASE_DIR,
            'us',
            f'{state}2020.pl',
            f'{state}000012020.pl'
        )

    @staticmethod
    def population_path(state):
        return os.path.join(
            DATA_DIR,
            'output',
            'population',
            f'us_{state}_pop.csv'
        )


class Canada:
    # dissemation area level population
    table = '98-401-X2021006'
    # table = '98-401-X2021001' # province level
    @staticmethod
    def table_path():
        return os.path.join(
            BASE_DIR,
            'canada',
            f'{Canada.table}_eng_CSV',
        )
    @staticmethod
    def data_path():
        return os.path.join(
            Canada.table_path(),
            f'{Canada.table}_English_CSV_data.csv'
        )

    @staticmethod
    def start_row_path():
        return os.path.join(
            Canada.table_path(),
            f'{Canada.table}_Geo_starting_row.csv'
        )
    
    @staticmethod
    def population_path():
        return os.path.join(
            DATA_DIR,
            'output',
            'population',
            'canada_das_pop.csv'
        )