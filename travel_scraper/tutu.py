import time
import logging
import datetime

from selenium import webdriver
from travel_scraper.utils import add_meta, create_grid

logger = logging.getLogger()

TEMPLATE_URL = ('https://tours.tutu.ru/hot_tours/?departure=491&'
                'arrival_id={arrival_country_id}&arrival_type=country&date_begin={date_begin}&'
                'date_end={date_end}&nights_min={min_nights}&nights_max={max_nights}&'
                'adults={adults}&children={children}&isArrivalIsHome=false&search=1&'
                'isArrivalIsScenario=false&sort=price')


@add_meta("https://tours.tutu.ru/hot_tours/")
def parse_with_params(
        browser: webdriver.Chrome,
        *,
        arrival_country_id,
        departure_country_id,
        min_nights,
        max_nights,
        adults,
        children,
        times_scrolled,
        debug=False,
        sleep_between_scroll: int = 5,
):
    stat = {}
    fmt = "%d.%m.%Y"
    today = datetime.date.today()
    date_begin = (today + datetime.timedelta(days=1)).strftime(fmt)
    date_end = (today + datetime.timedelta(days=31)).strftime(fmt)

    url = TEMPLATE_URL.format(
        arrival_country_id=arrival_country_id,
        departure_country_id=departure_country_id,
        date_begin=date_begin,
        date_end=date_end,
        min_nights=min_nights,
        max_nights=max_nights,
        adults=adults,
        children=children
    )

    logger.info(f"Travelling to {url}")

    stat["search_url"] = url
    stat["date_begin"] = date_begin
    stat["date_end"] = date_end

    browser.get(url)
    time.sleep(5)

    if debug:
        logger.info("Debug mode -> exiting -> downloading page source")
        content = browser.page_source
        return content, {"url": url}

    # main scrapping loop
    for _ in range(times_scrolled):
        try:
            next_button_element = browser.find_elements("xpath", "//*[contains(text(), 'Показать больше предложений')]")[2]
            browser.execute_script("arguments[0].scrollIntoView();", next_button_element)
            webdriver.ActionChains(browser).move_to_element(next_button_element).click(next_button_element).perform()
        except Exception as e:
            logger.error(f"Scrolling loop exception: {e}")
            pass

        logger.info("Successful iteration -> sleeping between scroll")
        time.sleep(sleep_between_scroll)

    logger.info("Downloading page source")
    content = browser.page_source
    return content, {"url": url}


def grid_option(grid_config: dict, night_interval: int = 0) -> list:
    if night_interval < 0:
        raise ValueError("Night interval should be > 0")

    grid = create_grid(grid_config)

    return list(
        map(
            lambda x: {
                "departure_country_id": x["departure_country_id"],
                "arrival_country_id": x["arrival_country_id"],
                "adults": x["adults"],
                "children": x["children"],
                "min_nights": x["nights"],
                "max_nights": x["nights"] + night_interval,
                "times_scrolled": x["times_scrolled"],
            },
            grid,
        )
    )
