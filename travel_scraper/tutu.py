import time
import logging
import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from travel_scraper.utils import add_meta, create_grid, scroll_bottom, return_height

from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger()

TEMPLATE_URL = ("https://tours.tutu.ru/hot_tours/?departure={departure_country_id}&"
                "arrival_id={arrival_country_id}&arrival_type=country&date_begin={date_begin}&"
                "date_end={date_end}&nights_min={min_nights}&nights_max={max_nights}&"
                "adults={adults}&children={children}&isArrivalIsHome=false&search=1&"
                "isArrivalIsScenario=false&sort=price")


@add_meta("https://tours.tutu.ru/hot_tours/")
def parse_with_params(
    browser: webdriver.Chrome,
    *,
    departure_country_id,
    arrival_country_id
    min_nights,
    max_nights,
    debug=False,
    sleep_between_scroll: int = 0.5,
):
    today = datetime.date.today()
    fmt = "%d.%m.%Y"
    stat = {}
    after = (today + datetime.timedelta(days=1)).strftime(fmt)
    before = (today + datetime.timedelta(days=31)).strftime(fmt)
    stat["after"] = after
    stat["before"] = before

    url = TEMPLATE_URL.format(
        before=before,
        after=after,
        min_nights=min_nights,
        max_nights=max_nights,
        country_id=country_id,
    )
    stat["search_url"] = url

    logger.info(f"Travelling to {url}")
    browser.get(url)
    logger.info(f"Waiting")
    time.sleep(5)

    if debug:
        logger.info("Debug mode, exiting")
        logger.info("Downloading page source")
        content = browser.page_source
        return content, {"url": url}

    scroll_bottom(browser)
    time.sleep(2)
    old_heigth = return_height(browser)
    while True:
        try:
            button = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.load-more"))
            )
        except TimeoutException as e:
            logger.info("Catching timeout exception")
            break

        if button.is_displayed() and button.is_enabled():
            logger.info("Button is clickable")
            button.click()
        else:
            logger.info("Button is not clickable")

        logger.info("Sleeping between scroll")
        time.sleep(sleep_between_scroll)
        scroll_bottom(browser)
        new_height = return_height(browser)
        logger.info(f"new height is {new_height}")
        if old_heigth == new_height:
            break
        else:
            old_heigth = new_height

    time.sleep(1)
    logger.info("Downloading page source")
    content = browser.page_source
    return content, {"url": url}


def grid_option(grid_config: dict) -> list:
    grid = create_grid(grid_config)
    return grid


def grid_option(grid_config: dict, night_interval: int = 0) -> list:
    if night_interval < 0:
        raise ValueError("Night interval should be > 0")

    grid = create_grid(grid_config)

    return list(
        map(
            lambda x: {
                "country_id": x["country_id"],
                "min_nights": x["nights"],
                "max_nights": x["nights"] + night_interval,
            },
            grid,
        )
    )
