###     This file defines generically created configuration for testing api, resources, data and tests themselves
###     There is also asset file called 'webapi_ds.json' which is later on loaded into Webapi's Datastore 
###       and serves the same purpose as this file with the exception that it can be changed runtime (see FirefoxWebapi.build for more info)
import os
from pathlib import Path
from typing import Union
 
import pytest
import testprog_common.lib.auxiliary as auxiliary
from selenium import webdriver
from testprog_common.lib.datastore.datastore import Datastore

from . import driver as cfg
from . import env


class Common:
    
    def get_env() -> dict[str,str]:
        d = {}
        for k,v in env.__dict__:
            d[k] = os.getenv(v)
        return d

# creates specific generic data for FirefoxDriver/Webapi
class Driver:

    @staticmethod
    def _get_firefox_capabilities_proxy():
        """
        Returns firefox proxy setting.
        """
        proxy = (cfg.Driver.Firefox.Capabilities.DEFAULT_PROXY_IP,cfg.Driver.Firefox.Capabilities.DEFAULT_PROXY_PORT)
        proxystr = f"{proxy[0]}:{proxy[1]}"
        return {
            "proxyType": "MANUAL",
            "httpProxy": proxystr,
            "ftpProxy": proxystr,
            "sslProxy": proxystr
        }

    @staticmethod
    def get_firefox_options():
        firefox_opt = webdriver.FirefoxOptions()
        for arg in Driver._get_geckodriver_args():
            firefox_opt.add_argument(arg)
        if cfg.Driver.Firefox.BINARY_PATH:
            firefox_opt.binary = cfg.Driver.Firefox.BINARY_PATH
        return firefox_opt
    
    @staticmethod
    def _get_firefox_profile_args():
        data = DatastoreHelper.recompose_datastore_from_conf_file()
        args = Datastore.filter(self=data["driver"]["firefoxprofileargs"],names=[],white_list=False)
        for key in args:
            if type(args[key]) == str:
                args[key] = args[key].format(**os.environ)
                print(args[key])
        return args
    
    @staticmethod
    def get_firefox_profile():
        firefox_profile = webdriver.FirefoxProfile()
        profileargs = Driver._get_firefox_profile_args()
        for name in profileargs:
            if name == "browser.download.dir":
                arg = profileargs[name]
                if cfg.GenericMetadata.MAKE_PATH_ABSOLUTE:
                    arg = str(Path(profileargs[name]).absolute()).replace("/","\\")
                if not os.path.exists(arg):
                    os.makedirs(arg, exist_ok=True)
            else:
                arg = profileargs[name]
            firefox_profile.set_preference(name, arg)
        return firefox_profile
    
    @staticmethod
    def get_firefox_capabilities():
        firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        firefox_capabilities['marionette'] = cfg.Driver.Firefox.Capabilities.USE_MARRIONETE
        if cfg.Driver.Firefox.Capabilities.USE_PROXY:
            firefox_capabilities['proxy'] = Driver._get_firefox_capabilities_proxy()
            print(f"setting proxy to:\n {firefox_capabilities['proxy']}")
        return firefox_capabilities
    
    @staticmethod
    def _get_geckodriver_args():
        json = DatastoreHelper.recompose_datastore_from_conf_file()
        args:list = json["driver"]["geckodriverargs"]
        if cfg.Driver.DO_RUN_HEADLESS: 
            args.append("--headless")
        return args


class DatastoreHelper:

    @staticmethod
    def recompose_datastore_from_conf_file(filepath=cfg.GenericMetadata.FILEPATH): 
        datastore = Datastore(payload=auxiliary.load_json_file(filepath))
        def recompose_dict_to_datastore(datast):
            for key in datast:
                if type(datast[key]) is dict and "_type" in datast[key] and datast[key]["_type"] == "Datastore":
                    datast[key] = Datastore(payload=datast[key])
                    recompose_dict_to_datastore(datast[key])
        recompose_dict_to_datastore(datastore)
        return datastore

