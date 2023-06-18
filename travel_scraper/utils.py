from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


def hover_and_right_click(browser: webdriver.Chrome, element):
    hover = ActionChains(browser).move_to_element(element).context_click(element)
    hover.perform()


from typing import Callable
from functools import wraps
import datetime
import uuid

import logging

logger = logging.getLogger()


def add_meta(website: str, time_fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> Callable:
    def dec_outer(fn):
        @wraps(fn)
        def somedec_inner(*args, **kwargs):
            meta = {}
            meta["parsing_started"] = datetime.datetime.now().strftime(time_fmt)
            try:
                result, stat = fn(*args, **kwargs)
                meta["failed"] = False
            except Exception as e:
                meta["failed"] = True
                meta["exception"] = str(e)
                logger.exception(e)
                stat = None
                result = None
                
            meta["parsing_ended"] = datetime.datetime.now().strftime(time_fmt)
            meta["stat"] = stat
            meta["website"] = website
            meta["parsing_id"] = str(uuid.uuid4())
            if "browser" in kwargs:
                kwargs.pop("browser")
            meta["func_args"] = kwargs
            return result, meta

        return somedec_inner

    return dec_outer


import os
import json


def safe_mkdir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def dump_json(data: list, path: str):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file)


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def dump_result_and_meta(base_dir: str, result: str, meta: dict):
    parsing_id = meta["parsing_id"]
    dirname = os.path.join(base_dir, parsing_id)
    safe_mkdir(dirname)
    dump_json(meta, os.path.join(dirname, "meta.json"))
    with open(os.path.join(dirname, "content.html"), "w", encoding="utf-8") as file:
        file.write(result)


import boto3
from typing import Union


def load_to_s3(data: Union[str, dict, list], Key, Bucket, is_json=False):
    boto_session = boto3.session.Session(
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )

    s3 = boto_session.client(
        service_name="s3",
        endpoint_url=os.environ["AWS_ENDPOITNT_URL"],
        region_name=os.environ["AWS_REGION_NAME"],
    )

    if isinstance(data, list) or isinstance(data, dict):
        if is_json:
            data = json.dumps(data)
        else:
            raise ValueError("You should explicitly specify is_json option")
    elif isinstance(data, str):
        pass
    else:
        raise ValueError("data should be str, list or dict")
    s3.put_object(Body=data, Bucket=Bucket, Key=Key)


def dump_result_and_meta_s3(Bucket: str, base_dir: str, result: str, meta: dict):
    parsing_id = meta["parsing_id"]
    dirname = os.path.join(base_dir, parsing_id)
    load_to_s3(
        meta, Key=os.path.join(dirname, "meta.json"), Bucket=Bucket, is_json=True
    )
    if result is not None:
        load_to_s3(result, Key=os.path.join(dirname, "content.html"), Bucket=Bucket)
    else:
        logger.info("Null result, not dumping to s3")


from itertools import product


def create_grid(params: dict) -> map:
    return map(lambda x: dict(zip(params.keys(), x)), product(*params.values()))


import sys
import logging


def config_logger(logger, name: str, folder: str) -> None:
    handler = logging.StreamHandler(sys.stdout)

    log_folder = os.path.join(folder, f"logs_{name}")
    safe_mkdir(log_folder)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = os.path.join(log_folder, f"log_{now}.log")
    file_handler = logging.FileHandler(filename, mode="w", encoding="utf-8")

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)

import time

def infinite_scroll(browser, sleep_between_scroll, delta=0.25):

    logger.info("Scrolling")
    old_height = 0
    delta = delta * browser.execute_script("return document.body.scrollHeight")
    logger.info(f"delta = {delta}")
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

def scroll_bottom(browser: webdriver.Chrome):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

def return_height(browser: webdriver.Chrome):
    return browser.execute_script("return document.body.scrollHeight")