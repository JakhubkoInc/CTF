import pickle
from typing import TYPE_CHECKING, Any, Callable, Iterator, Union

from .datastore.datastore import Datastore

if TYPE_CHECKING:
    from .sqlite.sqlquery import SQLiteTableQuery
    from .sqlite.sqlitesocket import SQLiteSocket


class SQLiteDatastore(Datastore):
    """
    Extends Datastore. Stores data in sqlite database.

    Natively does NOT store privates in db. You can change this opt via setting 'insert_privates' to True.

    If key is already present in db, its value will be updated.
    """
    _KEY_NAME = "Key"
    _VALUE_NAME = "Value"

    def __init__(self, 
                 socket:'SQLiteSocket',
                 payload:dict[str,Any] = {},
                 create_meta:bool = True,
                 value_type = None,
                 object_wrapper:Callable[[Any], Union[str,bytes]]=pickle.dumps,
                 object_unwrapper:Callable[[Union[str,bytes]], Any]=pickle.loads
                ):
        self.insert_privates = False
        self.wrapper = object_wrapper
        self.value_unwrapper = object_unwrapper
        self.value_type = value_type

        if not self.value_type:
            self.value_type = self._get_value_type_from_wrapper()
        self.socket = socket
        super().__init__(create_meta=create_meta)
        
        self.update(payload)
    
    @property
    def db(self) -> 'SQLiteTableQuery':
        return self.socket.query
    
    def _make_table_schema(self, value_type):
        return f"{SQLiteDatastore._KEY_NAME} TEXT PRIMARY KEY,{SQLiteDatastore._VALUE_NAME} {value_type}"
    
    def _get_value_type_from_wrapper(self) -> str | None:
        try:
            ret = self.wrapper.__annotations__["return"]
            print(f"return annotation for '{self.wrapper}' is '{ret}'")
            if issubclass(ret,int):
                return "INTEGER"
            elif issubclass(ret,float):
                return "REAL"
            elif issubclass(ret,str):
                return "TEXT"
            elif issubclass(ret,bytes):
                return "BLOB"
        except Exception:
            return "BLOB"

    def __getitem__(self, k) -> Union['Datastore', Any]:
        if self.socket.is_open:
            response = self.db.select("Value").where(Key=k).execute().fetchone()
            if response:
                data = self.value_unwrapper(response[0])
                return data
            else:
                return super().__getitem__(k)
        else:
            return None

    def __setitem__(self, k: str, v: Any) -> None:
        if self.socket.is_open:
            if not k.startswith('_') or self.insert_privates:
                response = self.db.select("Value").where(Key=k).execute().fetchone()
                pickled_data = self.wrapper(v)
                if not response:
                    self.db.insert(Key=k,Value=pickled_data).execute()
                else:
                    self.db.update(Value=pickled_data).where(Key=k).execute()
            else:
                super().__setitem__(k,v)

    def __delitem__(self, v: Any) -> None:
        self.db.delete().where(Key=v).execute()

    def __iter__(self) -> 'SqliteDatastoreIterator':
        return SqliteDatastoreIterator(self)
    
    def update(self,dict:dict):
        for k in dict:
            self.__setitem__(k,dict[k])

class SqliteDatastoreIterator(Iterator):
    _COLUMNS_SELECTOR = "Key,Value"

    def __init__(self, sqlite_datastore: SQLiteDatastore) -> None:
        self.datastore = sqlite_datastore
        self._counter = 0

    def __iter__(self) -> Iterator[Any]:
        return self

    def __next__(self) -> Any:
        response = self.datastore.db \
            .select(SqliteDatastoreIterator._COLUMNS_SELECTOR) \
            .limit(1).offset(self._counter) \
            .execute().fetchone()
        if response:
            data = self.datastore.value_unwrapper(response[1])
            self._counter += 1
            return response[0], data
        raise StopIteration
