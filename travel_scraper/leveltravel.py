from selenium import webdriver
from selenium.webdriver.common.by import By
import time

from travel_scraper.utils import add_meta, create_grid, infinite_scroll

import logging

logger = logging.getLogger()

TEMPLATE_URL = (
    "https://level.travel/search"
    "/Moscow-RU-to-Any-AE-departure-from-10.03.2023..12.03.2023"
    "-to-19.03.2023..22.03.2023-2-adults-0-kids-1..5-stars"
    "-package-type-10.03.2023-19.03.2023"
)

@add_meta("https://level.travel")
def parse_with_params(browser: webdriver.Chrome, *, param, debug=False):
    url = TEMPLATE_URL
    logger.info(f"Travelling to {url}")
    browser.get(url)
    logger.info(f"Waiting")
    time.sleep(10)
    logger.info("Downloading page source")
    content = browser.page_source
    infinite_scroll(browser,  5, delta=0.90)
    return content, {"url": url}

def grid_option(grid_config: dict) -> list:
    grid = create_grid(grid_config)

    return grid