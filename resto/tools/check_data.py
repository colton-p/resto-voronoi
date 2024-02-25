import os

from resto.population import paths

def main():
    if 'RESTO_DATA_DIR' not in os.environ:
        print('!')
    
    if os.path.exists(paths.Canada.population_path()):
        print('canada pop... ok✅')

if __name__ == "__main__":
    main()