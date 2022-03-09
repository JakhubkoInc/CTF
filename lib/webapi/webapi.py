import logging
import os
import sys
import uuid
from datetime import datetime, timedelta
from time import sleep

import testprog_common.conf as cfg
from testprog_common.lib import auxiliary
from testprog_common.lib.datastore.datastore import DatastoreRootProvider
from testprog_common.lib.logging.logger_gen import LoggerBuilder
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from . import expected_conditions as adhocEC


class Webapi(DatastoreRootProvider):

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.id = str(uuid.uuid4())[:8]
        super().__init__()
        self.log = LoggerBuilder.build(cfg.Webapi.WebapiConfig.LOGGER_NAME)
    
    
    def _awaitUntil(self, condition, timeout=cfg.Webapi.Driver.DEFAULT_WAIT, poll_frequency=0.5):
        try:
            WebDriverWait(self.driver, timeout, poll_frequency=poll_frequency).until(condition)
            return True
        except TimeoutException:
            self.log.info(f"Timeout! Condition {condition} not met in {timeout}s.")
            return False

    def _awaitUntilNot(self, condition, exp_wait=cfg.Webapi.Driver.DEFAULT_WAIT, poll_frequency=0.5):
        try:
            WebDriverWait(self.driver, exp_wait, poll_frequency=poll_frequency).until_not(condition)
            return True
        except TimeoutException:
            self.log.info(f"Timeout! Condition {condition} not met in {exp_wait}s.")
            return False

    def implicitly_wait(self, time=cfg.Webapi.Driver.IMPLICIT_WAIT):
        self.driver.implicitly_wait(time)

    def go_to_url(self, url):
        self.driver.get(url)
        self.implicitly_wait()

    def hover(self, locator):
        if cfg.Webapi.WebapiConfig.DO_HOVER:
            element = self.find(locator)
            hov = ActionChains(self.driver).move_to_element(element)
            hov.perform()
    
    def double_click(self, locator):
        self.await_visible(locator)
        self.await_clickable(locator)
        element = self.find(locator)
        dclick = ActionChains(self.driver).double_click(element)
        dclick.perform()
        self.log.info(f"Action: double click on {locator}")

    def repeated_click(self, locator, repetitions = 2):
        self.await_visible(locator)
        self.await_clickable(locator)
        for _ in range(repetitions):
            self.driver.find_element(*locator).click()
        self.log.info(f"Action: repeated click on {locator}, {repetitions} repetitions")

    def hover_and_click(self, locator):
        self.hover(locator)
        self.await_visible(locator)
        self.await_clickable(locator)
        self.driver.find_element(*locator).click()

    def safe_click(self, locator):
        self.await_visible(locator)
        self.await_clickable(locator)
        self.driver.find_element(*locator).click()
        self.log.info(f"clicked on {locator}")

    def hover_and_click_first(self, locator):
        elements = self.driver.find_element(*locator)
        hov = ActionChains(self.driver).move_to_element(elements[0])
        if cfg.Webapi.WebapiConfig.DO_HOVER:
            hov.perform()
        elements[0].click()
        self.log.info(f"Action: click on first element of {locator}")

    def is_visible(self, locator, exp_wait=cfg.Webapi.Driver.DEFAULT_WAIT):
        try:
            visible = self.await_visible(locator, exp_wait=exp_wait)
            if visible:
                return True
            else:
                self.log.warning(f'Locator {locator} still not visible after {exp_wait} seconds.')
                return False
        except:
            self.log.error(f'Locator {locator} not found.')
            return False

    def scroll_into_view(self, locator):
        self.implicitly_wait()
        if not self.await_present(locator):
            self.log.warning(f"locator {locator} still not present")
            return
        
        elem = self.driver.find_element(*locator)
        if cfg.Webapi.WebapiConfig.DO_SCROLL_TO:
            self.driver.execute_script('arguments[0].scroll_into_view({behavior: "smooth", block: "center", inline: "center"});', elem)
        
        if not self.await_visible(locator):
            self.log.warning(f"Element {locator} still not visible ")
        
        if not self.await_clickable(locator):
            self.log.warning(f"Scrolled to {locator} but element is not clickable")
        else:
            self.log.info(f"Scrolled to {locator}.")

    def scroll_first_into_view(self, locator):
        self.implicitly_wait()
        self.await_present(locator)
        elem = self.find_all(locator)
        if cfg.Webapi.WebapiConfig.DO_SCROLL_TO:
            self.driver.execute_script('arguments[0].scroll_into_view({behavior: "smooth", block: "center", inline: "center"});', elem[0])
        self.await_clickable(locator)

    def scroll_n_click(self, locator):
        self.scroll_into_view(locator)
        self.safe_click(locator)

    def click_on_first_safe(self, locator):
        self.scroll_first_into_view(locator)
        self.hover_and_click_first(locator)

    def safe_send_keys(self, locator, keys, do_clear=True, send_enter=True):
        self.scroll_into_view(locator)
        element = self.find(locator)
        if not element.is_displayed():
            self.implicitly_wait()
        if do_clear:
            element.clear()
        element.send_keys(keys)
        self.implicitly_wait()
        if send_enter:
            element.send_keys(Keys.ENTER)
        self.log.info(f"sent keys '{keys}' to {locator}")

    def find(self, locator):
        return self.driver.find_element(*locator)

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    def await_downloaded(self,
                         down_dir = None,
                         tick_time = 0.2,
                         print_rate = 1):
    
        chars = ('|', '/', '-', '\\')
        
        if down_dir == None:
            down_dir = self.datastore["_preferences"]["profile"].default_preferences["browser.download.dir"]
            self.log.info(f"No download dir set, defaulting to webapi conf: down_dir: {down_dir}")
            
        elapsed_time = avg_speed = no_download_stopwatch = file_size = last_tick_file_size = find_file_counter = 0
        is_downloading = True
        filepath = None
        print_time = tick_time * print_rate
        
        self.log.info(f"Looking for downloading file in {down_dir}")
        while is_downloading:
            sleep(tick_time)
            
            if elapsed_time > cfg.Webapi.WebapiConfig.Download.DOWNLOADING_TIMEOUT.seconds:
                msg = f"Download exceeded {cfg.Webapi.WebapiConfig.Download.DOWNLOADING_TIMEOUT}"
                self.log.error(msg)
                raise Exception(msg)
            
            if find_file_counter > cfg.Webapi.WebapiConfig.Download.FIND_FILE_TIMEOUT:
                msg = f"""Cannot find downloading file in {down_dir}
                                      not older than {cfg.Webapi.WebapiConfig.Download.MAX_FILE_CHANGE_AGE}
                                      after {find_file_counter}s."""
                self.log.error(msg)
                raise FileNotFoundError(msg)
            
            if filepath == None or not os.path.exists(filepath):
                filelist = auxiliary.list_file_paths(down_dir)
                if len(filelist) > 0:
                    filepath = max(filelist, key=os.path.getctime)
                    if(datetime.fromtimestamp(os.path.getmtime(filepath)) - datetime.now() > cfg.Webapi.WebapiConfig.Download.MAX_FILE_CHANGE_AGE):
                        filepath = None
                        find_file_counter += tick_time
                        self.log.info(f"""Cannot find downloading file in {down_dir}
                                      not older than {cfg.Webapi.WebapiConfig.Download.MAX_FILE_CHANGE_AGE}
                                      after {find_file_counter}s.""")
                        continue
                else:
                    find_file_counter += tick_time
                    self.log.info(f"""Cannot find downloading file in {down_dir}
                                      after {find_file_counter}s,
                                      directory is empty.""")
                    continue
            
            if elapsed_time % print_time < 1:
                tick_char = chars[(elapsed_time/tick_time)%4]
                print(f"[{tick_char}] downloading {elapsed_time}s, size: {file_size:.3f}KB, avg: {avg_speed:.3f}KB", end="\r")
            
            file_size = os.path.getsize(filepath)/(8*1024)
            avg_speed = (avg_speed * elapsed_time + (file_size - last_tick_file_size)) / (elapsed_time + tick_time)
            elapsed_time += tick_time
                
            if file_size == last_tick_file_size:
                no_download_stopwatch += tick_time
            else:
                no_download_stopwatch = 0
                last_tick_file_size = file_size
                
            if not filepath.endswith("download"):
                is_downloading = False
                self.log.info(f"downloaded '{filepath}' in {elapsed_time}s, size: {file_size:.3f}KB")
                break
            
            if no_download_stopwatch > cfg.Webapi.WebapiConfig.Download.NO_SPEED_TIMEOUT.seconds:
                os.remove(filepath)
                raise Exception("Seems not to be downloading; skipping and deleting file")
                
        return (filepath, file_size)

    def await_visible(self, locator, exp_wait=cfg.Webapi.Driver.DEFAULT_WAIT):
        return self._awaitUntil(EC.visibility_of_element_located(locator), timeout=exp_wait)

    def await_not_visible(self, locator):
        return self._awaitUntilNot(EC.visibility_of_element_located(locator))

    def await_present(self, locator):
        return self._awaitUntil(EC.presence_of_element_located(locator))

    def await_until_not_found(self, locator):
        return self._awaitUntilNot(adhocEC.can_find(locator))

    def await_until_not_found_any(self, locator):
        return self._awaitUntilNot(adhocEC.can_find_any(locator))

    def await_clickable(self, locator):
        return self._awaitUntil(EC.element_to_be_clickable(locator))

    def await_element_visible(self, locator):
        return self._awaitUntil(EC.visibility_of_all_elements_located(locator))

    def await_element_property_value_to_be(self, locator, property_name, property_value):
        return self._awaitUntil(adhocEC.property_value_to_be(locator, property_name, property_value))

    def await_element_property_value_to_contain(self, locator, property_name, property_value, exp_wait=cfg.Webapi.Driver.DEFAULT_WAIT):
        return self._awaitUntil(adhocEC.property_value_to_contain(locator, property_name, property_value), timeout=exp_wait)

    def await_element_property_value_not_to_contain(self, locator, property_name, property_value):
        return self._awaitUntilNot(adhocEC.property_value_to_contain(locator, property_name, property_value))

    def await_element_comply_to_lambda_condition(self, locator, condition):
        return self._awaitUntil(adhocEC.lambda_condition(locator, condition))

    def is_displayed(self, locator):
        try:
            element = self.driver.find_element(*locator)
            if element.is_displayed():
                return True
            else:
                self.log.info(f'Element {locator} found, but not displayed')
                return False
        except:
            self.log.info(f'Element {locator} not found')
            return False

    def close_browser(self):
        self.driver.close()
        self.log.info("Browser closed")
    
    def await_url(self, page_url):
        self._awaitUntil(EC.url_to_be(page_url))
        
    

class FirefoxWebapi(Webapi):
    
    _lock = object()

    def __init__(self, driver: WebDriver, _lock=None):
        if _lock is not self._lock:
            raise PermissionError("FirefoxWebapi object can be composed only via `FirefoxWebapi.build()` method.")
        super().__init__(driver)

    @classmethod    
    def build(cls) -> 'Webapi':
        ## setup firefox driver
        options = cfg.Generic.Driver.get_firefox_options()
        profile = cfg.Generic.Driver.get_firefox_profile()
        capabilities = cfg.Generic.Driver.get_firefox_capabilities()
        driverpath = cfg.Webapi.Driver.Firefox.DRIVER_PATH
        binpath = cfg.Webapi.Driver.Firefox.BINARY_PATH

        driver = webdriver.Firefox(options=options,
                                   firefox_profile=profile,
                                   capabilities=capabilities,
                                   executable_path=driverpath,
                                   firefox_binary=binpath)

        if cfg.Webapi.BROWSER_MAXIMALIZE:
            driver.maximize_window()
        else:
            driver.set_window_size(*cfg.Webapi.Driver.WIN_SIZE)
        
        ## setup FirefoxWebapi instance
        webapi = FirefoxWebapi(driver, cls._lock)
        webapi.log.info(f"""Webapi setup:
                        executable in {driverpath}
                        profile: {profile}
                        options: {options}
                        capabalities: {capabilities}""")
        
        # these preferences are not used anymore by selenium driver itself but still stored for sake of object transparency
        webapi.datastore["_preferences"].update({
            "options": options,
            "profile": profile,
            "capabilities": capabilities
        })
        
        # TODO: use sqlite datastore (2 tables, one for this specific datastore, other as save from last run)
        # update webapi datastore with recomposed datastore object from conf json file
        webapi.datastore.update(cfg.Generic.DatastoreHelper.recompose_datastore_from_conf_file())
        webapi.log.info(f"Updated webapi datastore: {webapi.datastore}")
        return webapi

    