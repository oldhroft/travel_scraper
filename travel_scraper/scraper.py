from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import yaml
import os
import click

import logging

from travel_scraper.utils import (
    dump_result_and_meta,
    dump_result_and_meta_s3,
    config_logger,
)

logger = logging.getLogger()

from importlib import import_module


def get_method(module_name, func_name):
    method = getattr(import_module(f"travel_scraper.{module_name}"), func_name)
    return method


@click.command()
@click.option(
    "--config_path", help="Path to config", type=click.STRING, default="config.yaml"
)
@click.option("--parser", help="Parser", type=click.STRING, default="travelata")
def run_selenium(config_path: str, parser: str):
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    config_logger(logger, parser, config["log_folder"])

    options = Options()
    for option in config["options"]:
        options.add_argument(option)

    EXEC_PATH = os.environ["CHROME_PATH"]
    browser = webdriver.Chrome(EXEC_PATH, chrome_options=options)

    debug_option = config["debug"]
    parser_config = config["parsers"][parser]

    parse_func = get_method(parser, "parse_with_params")
    grid_fn = get_method(parser, "grid_option")
    logger.info(f"Parser {parser}")

    for param in grid_fn(parser_config["parsing"], **parser_config["parsing_params"]):
        result, meta = parse_func(browser, debug=debug_option, **param)

        dump_result_and_meta_s3(
            Bucket=parser_config["s3_options"]["Bucket"],
            base_dir=parser_config["s3_options"]["base_dir"],
            result=result,
            meta=meta,
        )
