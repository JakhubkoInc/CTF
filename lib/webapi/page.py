from ..datastore.datastore import (
    DatastoreLinkFieldDescriptor, DatastoreSubscriber)

from .webapi import FirefoxWebapi


class POMElement(DatastoreSubscriber):
    """
    Defines basic POM element component, each instance has unique uuid.
    """

    def __init__(self, webapi: FirefoxWebapi, id:str=None):
        super().__init__(id)
        self.webapi = webapi
        self.subscribe(provider=webapi)
        self.created = DatastoreLinkFieldDescriptor(self, "_created")
        
        # debug log - creation of new container
        parent_id = "<root provider>"
        if hasattr(self.parent_datastore, 'id'):
            parent_id = self.parent_datastore.id 
        self.webapi.log.debug(f"""created {self.datastore['_subtype']}[id:{self.id}] 
                              in {self.parent_datastore['_type']}[id:{parent_id}]
                              at {self.created}""")
        
    @property
    def driver(self):
        return self.webapi.driver

    @property
    def log(self):
        return self.webapi.log

class Page(POMElement):
    """
    Defines POM element in role of web page with specific url.
    """

    def __init__(self, webapi: FirefoxWebapi, page_url:str, datastore_id:str=None):
        super().__init__(webapi, datastore_id)
        self.url = page_url
        self.datastore["url"] = self.url
    
    @property
    def url(self) -> str:
        return self.datastore["url"]
    
    def open(self) -> None:
        self.webapi.log.info(f"url: {self.url}")
        self.driver.get(self.url)

    def check_right_url(self) -> bool:
        return self.driver.current_url == self.url

    def await_page_loaded(self) -> None:
        self.webapi.await_url(self.url)
    
    def load(self) -> bool:
        self.open()
        self.await_page_loaded()
        return self.check_right_url()

class Container(POMElement):
    """
    Defines POM element in role of standalone document inside parent POM element.
    """

    def __init__(self, parent: POMElement, app_locator: tuple):
        self.app_locator = app_locator
        self.parent = parent
        super().__init__(parent.webapi)
        self.subscribe(parent)
    
    def await_visible(self):
        self.webapi.await_element_visible(self.app_locator)
    
    def find_inside(self, locator):
        return self.webapi.find(self.app_locator).find_element(*locator)
