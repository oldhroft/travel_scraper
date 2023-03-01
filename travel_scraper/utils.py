from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

def hover_and_right_click(browser:  webdriver.Chrome, element):
    hover = ActionChains(browser).move_to_element(element).context_click(element)
    hover.perform()

from typing import Callable
from functools import wraps
import datetime
import uuid

def add_meta(website: str, time_fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> Callable:
    def dec_outer(fn):
        @wraps(fn)
        def somedec_inner(*args, **kwargs):
            meta = {}
            meta["parsing_datetime"] = datetime.datetime.now().strftime(time_fmt)
            result, stat = fn(*args, **kwargs)
            stat["parsing_ended"] = datetime.datetime.now().strftime(time_fmt)
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
        os.mkdir(path)

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

