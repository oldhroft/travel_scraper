import yaml
from travel_scraper.travelata import grid_option

if __name__ == "__main__":
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    config = config["parsers"]["travelata"]
    print(list(grid_option(config["parsing"], **config["parsing_params"])))
