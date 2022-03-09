from typing import Any

from testprog_common.lib.datastore.datastore import (Datastore,
                                                 DatastoreRootProvider,
                                                 DatastoreSubscriber)
from testprog_common.lib.sqldatastore import SQLiteDatastore


class Context(Datastore):
    """
    Extends Datastore. Implements default payload.

    Key should be string.
    """
    def __init__(self, payload:dict[str,Any]={}, **kwargs):
        super().__init__(self)
        self.update(payload,**kwargs)
    

class ContextRootProvider(DatastoreRootProvider):

    def __init__(self, payload={}) -> None:
        self._datastore = Context(payload)
    
    @DatastoreRootProvider.datastore.getter
    def context(self) -> Context:
        return self._datastore    
    

class ContextSubscriber(DatastoreSubscriber):

    def __init__(self, id:str=None) -> None:
        super().__init__(id=id)
    
    @DatastoreSubscriber.datastore.getter
    def subscribedContext(self) -> Context:
        return self._provider.datastore[self.id]
    
    @DatastoreSubscriber.parent_datastore.getter
    def parentContext(self) -> Context:
        return self._provider.datastore


class SQLiteContext(SQLiteDatastore):

    def __init__(self, db_path:str, table_name:str, payload: dict={}, create_meta: bool=True) -> None:
        super().__init__(db_path, table_name, payload=payload, create_meta=create_meta)

