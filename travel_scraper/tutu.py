import time
import logging
import datetime

from selenium import webdriver
from travel_scraper.utils import add_meta, create_grid
from selenium.common.exceptions import ElementNotInteractableException

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
        date_begin,
        date_end,
        min_nights,
        max_nights,
        adults,
        children,
        times_scrolled,
        debug=False,
        sleep_between_scroll: int = 3
):
    stat = {}

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
        return content, stat

    one_link_counter = 0
    loop_counter = 0

    # main scrolling loop
    while one_link_counter < times_scrolled:
        try:
            time.sleep(2)
            next_button_element = browser.find_elements("xpath", "//*[contains(text(), 'Показать больше предложений')]")[2]
            browser.execute_script("arguments[0].scrollIntoView();", next_button_element)
            webdriver.ActionChains(browser).move_to_element(next_button_element).click(next_button_element).perform()

            logger.info("Successful iteration -> sleeping between scroll")
            time.sleep(sleep_between_scroll)
        except Exception as e:
            if type(e) == ElementNotInteractableException or type(e) == IndexError:
                one_link_counter -= 1
                time.sleep(5)
                pass
            else:
                logger.error(f"Scrolling loop exception: {e}")
            pass
        one_link_counter += 1
        loop_counter += 1

        if loop_counter > times_scrolled+5:
            logger.warning("Stuck on this link -> skipping")
            break

    logger.info(f"Scrolling finished with amount of iterations: {loop_counter}")
    logger.info("Downloading page source")
    content = browser.page_source
    return content, stat


def grid_option(grid_config: dict, times_scrolled, night_interval: int = 0, days_from: int = 2,
                days_to: int = 30) -> list:
    if night_interval < 0:
        raise ValueError("Night interval should be > 0")

    start_date = datetime.datetime.now() + datetime.timedelta(days=days_from)
    date_grid = [start_date + datetime.timedelta(days=x) for x in range(0, days_to)]
    date_grid = [t.strftime('%d.%m.%Y') for t in date_grid]
    grid_config['dates'] = date_grid

    grid = create_grid(grid_config)

    return list(
        map(
            lambda x: {
                "arrival_country_id": x["arrival_country_id"],
                "departure_country_id": x["departure_country_id"],
                'date_begin': x['dates'],
                'date_end': x['dates'],
                "adults": x["adults"],
                "children": x["children"],
                "min_nights": x["nights"],
                "max_nights": x["nights"] + night_interval,
                "times_scrolled": times_scrolled,
            },
            grid,
        )
    )
