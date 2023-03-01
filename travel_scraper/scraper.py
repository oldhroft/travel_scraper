from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import yaml
import os
import click

import logging

from travel_scraper.travelata import parse_with_params
from travel_scraper.utils import dump_result_and_meta

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger()

@click.command()
@click.option("--config_path", help="Path to config", type=click.STRING, required=True)
@click.option("--basedir", help="Path to config", type=click.STRING, default='./result')
def run_selenium(config_path: str, basedir: str):
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    options = Options()
    for option in config["options"]:
        options.add_argument(option)

    EXEC_PATH = os.environ["CHROME_PATH"]
    browser = webdriver.Chrome(
        EXEC_PATH, chrome_options=options)

    codes = list(config["countries"].values())

    for code in codes:
        result, meta = parse_with_params(
            browser, country_code=code, night_from=7, night_to=7, debug=True)
        dump_result_and_meta(basedir, result, meta)
        
