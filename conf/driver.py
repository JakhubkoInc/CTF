###     This file defines static configuration for testing webapi, resources and data 

import os
from datetime import timedelta
from pathlib import Path
from .env import *

# few most used opts are here: 
FIREFOX_DRIVER_URL = os.getenv(FIREFOX_DRIVER_URL_NAME)
FIREFOX_BINARY_URL = os.getenv(FIREFOX_BIN_NAME)
BROWSER_MAXIMALIZE = False
RUN_HEADLESS = False


# defines FirefoxDriver & Webapi settings
class Driver:
    IMPLICIT_WAIT = 15
    SHORT_WAIT = 4
    DEFAULT_WAIT = 5
    MID_WAIT = 6
    LONG_WAIT = 12
    WIN_SIZE = (1920, 1080)
    DO_RUN_HEADLESS = RUN_HEADLESS
    DO_CLOSE_IN_TEARDOWN = True

    class Firefox:
        DRIVER_PATH = FIREFOX_DRIVER_URL
        BINARY_PATH = FIREFOX_BINARY_URL
        class Capabilities:
            DEFAULT_PROXY_IP = "0.0.0.0"
            DEFAULT_PROXY_PORT = 0
            USE_MARRIONETE = True
            USE_PROXY = False

# defines Webapi settings
class WebapiConfig:
    DO_HOVER = False
    DO_SCROLL_TO = False
    DO_AWAIT_VISIBLE = False
    LOGGER_NAME = "FirefoxWebapi"
    
    # defines setting for downloading files
    class Download:
        FIND_FILE_TIMEOUT = timedelta(seconds=5)
        DOWNLOADING_TIMEOUT = timedelta(seconds=30)
        NO_SPEED_TIMEOUT = timedelta(seconds=10)
        MAX_FILE_CHANGE_AGE = timedelta(seconds=10)

# defines metadata for generic data creation
class GenericMetadata:
    FILEPATH = Path("assets/config/webapi_ds.json")
    MAKE_PATH_ABSOLUTE = True
