from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import time

import datetime

from travel_scraper.utils import hover_and_right_click
from travel_scraper.utils import add_meta, create_grid

import logging

logger = logging.getLogger()

TEMPLATE_STRING = (
    "https://travelata.ru/tury#?fromCity=2"
    "&dateFrom={date_from}&dateTo={date_to}"
    "&nightFrom={night_from}&nightTo={night_to}"
    "&adults=2&hotelClass=all&meal=all&sort=priceUp"
    "&f_good=true&toCountries={country}"
)


@add_meta("https://travelata.ru/")
def parse_with_params(
    browser: webdriver.Chrome,
    *,
    country_code: str,
    night_from: int,
    night_to: int,
    debug: bool = False,
    sleep_between_scroll : int = 3,
    sleep_between_click: float = 0.2
) -> None:
    # TODO unify for different parsers
    stat = {}

    logger.info(f"Parsing {country_code} nights {night_from} to {night_to}")

    today = datetime.date.today()
    fmt = "%d.%m.%Y"
    date_from = (today + datetime.timedelta(days=1)).strftime(fmt)
    date_to = (today + datetime.timedelta(days=31)).strftime(fmt)
    stat["date_from"] = date_from
    stat["date_to"] = date_to

    url = TEMPLATE_STRING.format(
        country=country_code,
        date_from=date_from,
        date_to=date_to,
        night_from=night_from,
        night_to=night_to,
    )
    stat["search_url"] = url
    logger.info(f"Travelling to {url}")
    browser.get(url)
    logger.info("Sleeping")
    time.sleep(2)
    logger.info("Waking up")

    content = browser.page_source
    soup = BeautifulSoup(content, "html.parser")
    banner = soup.find("p", class_="marketing-banner__label")
    logger.info("Check if a banner is present")
    if banner is not None:
        logger.info("Clicking the banner")
        button = browser.find_element(
            By.CSS_SELECTOR, "div.btn.btnOrange.btnFlat.js-popup-close"
        )
        if button.is_displayed() and button.is_enabled():
            logger.info("Button is clickable")
            button.click()

    logger.info("Sleeping")
    time.sleep(10)
    logger.info("Waking up")

    if debug:
        logger.info("debug mode, exiting")
        logger.info("Downloading page source")
        content = browser.page_source
        return content, stat

    logger.info("Scrolling")
    old_height = 0
    delta = 0.25 * browser.execute_script("return document.body.scrollHeight")
    second_chance = True
    while True:
        browser.execute_script(
            f"window.scrollTo(0, document.body.scrollHeight - {delta});"
        )
        time.sleep(sleep_between_scroll)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = browser.execute_script("return document.body.scrollHeight")
        logger.info(f"New height is {new_height}")
        time.sleep(sleep_between_scroll)
        if new_height == old_height:
            if second_chance:
                old_height = new_height
                browser.execute_script(
                    f"window.scrollTo(0, document.body.scrollHeight - {delta});"
                )
                logger.info("Second chance")
                second_chance = False
                time.sleep(6)
            else:
                logger.info("Scrolling finished!")
                break
        else:
            old_height = new_height

    time.sleep(4)
    logger.info("Trying to get links")

    elements = browser.find_elements(
        By.CSS_SELECTOR, "a.serpHotelCard__title.goToHotel"
    )

    for element in elements:
        hover_and_right_click(browser, element)
        time.sleep(sleep_between_click)
        href = element.get_attribute("href")
        logger.info(f"extracting url {href}")

    logger.info("Downloading page source")
    content = browser.page_source

    return content, stat


def grid_option(grid_config: dict, night_interval: int = 0) -> list:
    if night_interval < 0:
        raise ValueError("Night interval should be > 0")

    grid = create_grid(grid_config)

    return list(
        map(
            lambda x: {
                "country_code": x["country_code"],
                "night_from": x["nights"],
                "night_to": x["nights"] + night_interval,
            },
            grid,
        )
    )
