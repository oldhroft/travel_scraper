import boto3
import os

from travel_scraper.utils import add_meta, config_logger
import logging
logger = logging.getLogger()

@add_meta("website.org")
def parse_with_params_test(browser, *, some_param):
    raise ValueError("Very erroneous error!")

if __name__ == "__main__":
    config_logger(logger, "parser", "logs")
    browser = "Browser"
    param = "param"
    parse_with_params_test(browser, some_param=param)