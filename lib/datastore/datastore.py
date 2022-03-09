
import json
import pickle
import uuid
from datetime import datetime
from enum import Enum
from typing import (Any, Generic, Iterable, KeysView, Mapping, Type, TypeVar,
                    Union)
from dataclasses import dataclass

    

class Datastore(dict):
    """
    Expands dict. Adds filtering and metadata.

    On value set: if the key is not in the set, it will be added to the set, instantiated as Datastore.

    There are two types of keys: public and private keys. Private keys starts with '_'
    """
    
    def __init__(self, payload:dict=None, create_meta:bool=True) -> None:
        if create_meta:
            # TODO: [BT-13] create metadata dataclasse DatastoreMeta instead of creating a dict
                # all metadata should be accessible the same way
            meta = {
                "_created": datetime.utcnow().timestamp(),
                "_type": self.__class__.__name__,
                # `_nest` defaults to 0 because not yet subscribed to any datastore -> this is the root
                "_nest": 0
            }
            self.update(meta)
        if payload:
            self.update(payload)
    
    def __getitem__(self, k:Any) -> Union['Datastore',Any]:
        if not k in self:
            super().__setitem__(k,Datastore({"_nest": self["_nest"]+1}))
        return super().__getitem__(k)
    
    def __str__(self) -> str:

        outp = json.dumps(self, indent=4, default=str, ensure_ascii=False)
        return outp

    def filter(self, names: list, white_list=True, show_private=False) -> 'Datastore':
        """
        filters out specified vars names based on whether to act as a whitelist/blacklist

        implicitly ignores private vars (starts with '_')

        can be used for any dict
        """
        payload = {}
        for key in self:
            if key.startswith("_"):
                if show_private:
                    payload[key] = self[key]
            else:
                if white_list:
                    if key in names:
                        payload[key] = self[key]
                else:
                    if not key in names:
                        payload[key] = self[key]
        return Datastore(payload=payload, create_meta=False)
    
    def privates(self) -> 'Datastore':
        """[summary]
        returns all private vars (starts with '_')
        """
        payload = {}
        for key in self:
            if key.startswith("_"):
                payload[key] = self[key]
        return Datastore(payload=payload, create_meta=False)
    
    def publics(self) -> 'Datastore':
        """[summary]
        returns all public vars
        """
        payload = {}
        for key in self:
            if not key.startswith("_"):
                payload[key] = self[key]
        return Datastore(payload=payload, create_meta=False)
    
    def translate(self, names: dict) -> 'Datastore':
        """[summary]
        returns translated variable names into new names as declared by specified dict, not specified names are preserved
        """
        payload = {}
        for name in self:
            if name in names:
                payload[names[name]] = self[name]
            else:
                payload[name] = self[name]
        return Datastore(payload=payload, create_meta=False)
    
    def first(self) -> Any:
        """[summary]
        returns first public item, if none return None
        Returns:
            Any: [description]
        """
        if len(self.publics()) > 0:
            return self.publics()[0]
        else:
            return None

    def update(self, val:Union[dict, 'Datastore']):
        """
        Recursively updates self and all vars instantiated as `Mapping`
        """
        for k,v in val.items():
            if isinstance(v, Mapping):
                self[k].update(v)
            else:
                self[k] = v

# TODO: WIP
class QueryDatastore(Datastore):
    
    def __init__(self, parent:Datastore):
        super().__init__(create_meta=True)

class DatastoreProvider:
    """
    Propagates datastore to subcribers
    """
    def __init__(self, attr_name, payload={}) -> None:
        self._attr_name = attr_name
        self.datastore.update(payload)
    
    @property
    def datastore(self) -> Datastore:
        return self.__getattribute__(self._attr_name)

class DatastoreRootProvider(DatastoreProvider):
    """
    Datastore provider with root instance of Datastore
    """
    def __init__(self, payload={}) -> None:
        self._datastore = Datastore()
        super().__init__("_datastore",{
            "_nest":0
        })
        self.datastore.update(payload)

class DatastoreSubscriber():
    """
    DatastoreSubscriber can input its data to propagated Datastore when subscribed to a DatastoreProvider.\n
    Also propagetes the Datastore further.
    """
    def __init__(self, id:str=None) -> None:
        if id != None:
            self.id = str(id)
        else:
            self.id = str(uuid.uuid4())
        self._is_subscribed = False

    @property
    def is_subscribed(self) -> bool:
        return self._is_subscribed

    @property
    def datastore(self) -> Datastore:
        return self._provider.datastore[self.id]
    
    @property
    def parent_datastore(self) -> Datastore:
        return self._provider.datastore
    
    def subscribe(self, provider: DatastoreProvider, payload:Mapping={}):
        """
        Subscribe to provider ds.
        """
        if not self.is_subscribed:
            self._provider = provider
            self.datastore.update({
                "_subtype": self.__class__.__name__,
                "_subbases": [_class.__name__ for _class in self.__class__.__bases__],
                "_subfrom":  datetime.utcnow().timestamp(),
                "_nest": provider.datastore["_nest"] + 1
            })
            self._is_subscribed = True
            self.datastore.update(payload)
    
    def unsubscribe(self, pop_datastore=False) -> Union['Datastore',dict]:
        """
        Unsubscribe means that this instance of datastore sub will no longer
        change any content that has been written to parent ds so far.
        
        * To pop datastore means to remove it from parent datastore completely.
        """
        # 
        if self.is_subscribed:
            try:
                if pop_datastore:
                    return self._provider.datastore.pop(self.id)
                else:
                    meta = {
                        "_subtype": self.datastore.pop("_subtype"),
                        "_subbases": self.datastore.pop("_subbases"),
                        "_subfrom": self.datastore.pop("_subfrom"),
                        # `_nest` should not be popped as this datastore is still accessible from parent datastore
                        "_nest": self.datastore["_nest"] 
                    }
                    return meta
            finally:
                self._provider = None
                self._is_subscribed = False
    
    def pop(self) -> 'Datastore':
        self.unsubscribe(pop_datastore=True)
    
    

class DumpAs(Enum):
        JSON = 1
        PICKLE = 2
class DumpDatastore(Datastore):

    def __init__(self,file_path:str, payload: dict={}, create_meta: bool=True) -> None:
        super().__init__(payload=payload, create_meta=create_meta)
        self._file_path = file_path
    
    def dump(self, dump_as=DumpAs.PICKLE):
        if dump_as == DumpAs.JSON:
            json.dump(self,self._file_path)
        elif dump_as == DumpAs.PICKLE:
            pickle.dump(self,self._file_path)

datastoreFieldDescriptorType = TypeVar("datastoreFieldDescriptorType")

class DatastoreLinkFieldDescriptor(Generic[datastoreFieldDescriptorType]):
    """
    Defines link to datastore property - enables to expose it as property.
    """
    
    def __init__(self, ds:Union[Datastore, DatastoreProvider, DatastoreSubscriber], field_name:str, default_value=None):
        if isinstance(ds, DatastoreProvider) or isinstance(ds, DatastoreSubscriber):
            self._datastore = ds.datastore
        else:
            self._datastore = ds
        self._field_name = field_name
        self._default_value = default_value
        self._is_initialized = False
        # TODO: this implementation is wrong - should not be needed
        self._last_val = default_value
    
    def __get__(self, instance, owner) -> datastoreFieldDescriptorType:
        if instance == None:
            return super().__get__(instance, owner)
        else:
            if not self._is_initialized:
                self._datastore[self._field_name] = self._default_value
                self._is_initialized = True
            return self._datastore[self._field_name]
    
    def __set__(self, instance, value:Type[datastoreFieldDescriptorType]):
        assert instance != None, "Instace should not be None"
        self._datastore[self._field_name] = value
        self._last_val = value
    
    def __getattribute__(self, __name: str) -> Any:
        if __name[0] == '_':
            return super().__getattribute__(__name)
        else:
            return getattr(self._datastore[self._field_name], __name)
    
    def __repr__(self):
        return repr(self._last_val)
