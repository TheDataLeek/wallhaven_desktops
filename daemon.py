#!/usr/bin/env python3.8

import sys
import os
import pathlib
from pprint import pprint as pp
import time
import signal

import daemonize
import yaml
import requests


PIDFILE = pathlib.Path('/tmp/wallpapers.pid')

BASE_URL = "https://wallhaven.cc/api/v1/search"

DOWNLOAD_DIR = pathlib.Path().home() / ".wallpapers"

if not DOWNLOAD_DIR.exists():
    os.mkdir(DOWNLOAD_DIR)


# TODO actually include this...?
CONFIG = DOWNLOAD_DIR / "config.yaml"


def main():
    while True:
        get_wallpapers()
        time.sleep(60 * 60)    # once an hour


def get_wallpapers():
    api_key = os.environ.get("WH_KEY", None)

    args = {}

    if api_key:
        args["apikey"] = api_key

    args["q"] = "cyberpunk"

    args["categories"] = "111"
    args["purity"] = "111"
    args["atleast"] = "1920x1080"
    args["ratios"] = "16x9"
    args["sorting"] = "random"

    how_many_to_fetch = 2
    fetched = []

    r = requests.get(BASE_URL, params=args)
    data = r.json()
    for blob in data["data"]:
        img_path = blob["path"]
        theoretical_path = DOWNLOAD_DIR / img_path.split("/")[-1]
        if not theoretical_path.exists():
            img = requests.get(img_path)
            theoretical_path.write_bytes(img.content)
            fetched.append(theoretical_path)

            if len(fetched) >= how_many_to_fetch:
                break

    return fetched


if __name__ == "__main__":
    if PIDFILE.exists():
        print('Daemon OFF')
        os.kill(int(PIDFILE.read_text()), signal.SIGINT)
    else:
        print('Daemon ON')
        daemon = daemonize.Daemonize(app='wallpapers', pid=PIDFILE, action=main)
        daemon.start()