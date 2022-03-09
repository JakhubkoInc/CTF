import json
from typing import Union

from testprog_common.lib.datastore.context import Context, SQLiteContext


class HistoryContext(Context[str,list[str]]):

    def __init__(self, iterable=(), **kwargs):
        super().__init__(payload=iterable, **kwargs)
    
    def __setitem__(self, name: str, value: Union[str, list[str]]) -> None:
        if name in self:
            if type(value) is str:
                self[name].append(value)
            else:
                self[name].update(value)
        else:
            if type(value) is str:
                super().__setitem__(name, [value])
            else:
                super().__setitem__(name, value)
    

class SQLiteHistoryContext(SQLiteContext[str,list[str]]):

    def __init__(self, db_path: str, table_name: str, payload: dict={}, create_meta: bool=True) -> None:
        super().__init__(db_path, table_name, payload=payload, create_meta=create_meta)
    
    def __setitem__(self, name: str, value: Union[str, list[str]]) -> None:
        if name in self:
            newvalue = self[name]
            if type(value) is str:
                newvalue.append(value)
            else:
                newvalue.update(value)
            super().__setitem__(name, newvalue)
        else:
            if type(value) is str:
                super().__setitem__(name, [value])
            else:
                super().__setitem__(name, value)
    
    def __str__(self) -> str:
        dic = {}
        for item in self:
            dic[item[0]] = item[1]
        return json.dumps(dic, indent=4)
    
    def save(self):
        self.socket.save()
