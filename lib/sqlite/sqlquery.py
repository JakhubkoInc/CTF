import sqlite3
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

import testprog_common.lib.auxiliary as utils
from testprog_common.lib.logging.static_log import STATIC_LOGGER as log

from .sqlitesocket import SQLiteSocket

if TYPE_CHECKING:
    from sqlite3.dbapi2 import Cursor
    from .resources import SQLiteDatatype, SQLiteTags


@dataclass
class TableColumn:
    _type:'SQLiteDatatype'
    _tags:list
    
    def __set_name__(self, owner, name:str):
      self._name = name
    
    def __str__(self):
      return f"{self._name} {self._type} {' '.join(self._tags)}"      
    
def col(type:'SQLiteDatatype', *tags:'SQLiteTags'):
    "Generates SQL table column scheme."
    return TableColumn(type, tags)

class TableScheme(dict[str, TableColumn]):
    
    def __new__(cls, **columns:TableColumn) -> 'TableScheme':
        obj = super().__new__(cls)
        obj.update(columns)
        return obj
    
    def __init__(self, **_columns:TableColumn):
        for name, col in self.items():
            col._name = name
    
    @property
    def columns(self):
        return [str(column) for column in self.values()]
    
    @property
    def rows(self):
        return list(self.keys())


class QueryPartType(IntEnum):
    STATEMENT = 0
    CREATE = 1
    INSERT = 2
    UPDATE = 3
    SELECT = 4
    DELETE = 5
    
    CONDITION = 10
    ADDITIONAL = 20
    END = 30
    
    @staticmethod
    def is_statement(T:'QueryPartType'):
        return T < QueryPartType.CONDITION


class Selectors:
    ALL = "*"
    ID = "ID"


# TODO: make SQLiteQuery an exlusive class for building the query (socket should not be passed) -> refactor this to e.g. SqliQueryGenerator
class SQLiteQuery:
    """
    Sql query generator which then executes it via passed SqliteSocket
    
    ---
    
    * this has not been tested on large datasets (extesive usage), recommended only for small datasets (e.g. for storing configuration) for now
    """

    EXECUTE_TIMEOUT = 15

    def __init__(self, connection:'SQLiteSocket') -> None:
        self._queries = []
        self._vars = []
        self._statements = []
        self._statement_cursor = 0
        self._supplements = {}
        self._execute_timeout = SQLiteQuery.EXECUTE_TIMEOUT
        
        assert isinstance(connection, SQLiteSocket), "The argument 'connection' must be an instance of SqliteSocket."
        self._connection = connection

    def compose(self) -> tuple:
        # append ';' after each main statement if not already in place
        for main_st_list in self._statements:
            main_st_list.sort(key=lambda tuple: tuple[0])
            for statement in main_st_list:
                if QueryPartType.is_statement(statement[0]) and not QueryPartType.END == statement[0]:
                    main_st_list.append((QueryPartType.END,";",()))
        
        # concat parts for each main statement into a query and vars 
        nodes = []           
        for statement in self._statements:
            types, words, vars = zip(*statement)
            query = " ".join(words)
            query = query.format(**self._supplements)
            self._queries.append(query)
            self._vars.append(tuple(utils.flatten(vars)))
            
            # create nodes to provide simple composition structure diagram
            node = "<"
            node += " ".join([t.name.lower() for t in types if t != QueryPartType.END])
            node += ">"
            nodes.append(node)
        structure = " --> ".join(nodes)
        

        log.debug(f"composition structure: {structure}")
            
        # log and check for consistency
        log.info(f"composed query:\n '{self._queries}'\n  vars: {self._vars}")
        
        #if self.check():
        #    log.info(f"query composed successfully")
            
        return (self._queries, self._vars)

    def timeout(self, timeout) -> 'SQLiteQuery':
        self._execute_timeout = timeout
        return self
    
    def _clear(self):
        self._queries = []
        self._statements = []
        self._vars = []
        self._responses = []

    def flush(self):
        self.compose()
        
        query = self._queries
        vars = self._vars
        
        self._clear()
        
        return query, vars   
    
    def execute(self, do_commit=True) -> list['Cursor']:
        responses = []
        
        self.compose()
        
        i = 0        
        for query in zip(self._queries, self._vars):
            log.debug(f"executing statement ({i}): {query}")
            try:            
                response = self._connection.cursor.execute(*query)  
                responses.append(response)
            except Exception as e:
                log.error(f"error when executing statement ({i}): {e}, skipping this response.")
            i+=1
            
        if do_commit:
            self._connection.save()
        
        self._clear()
        
        return responses

    def check(self) -> bool:
        with sqlite3.connect(self._connection._db_path, timeout=SQLiteQuery.EXECUTE_TIMEOUT) as temp_db:
            try:
                log.debug("executing temp query with execute") 
                for query in zip(self._queries, self._vars):
                    log.debug(f"executing query: {query}")              
                    temp_db.execute(*query)
                return True
            except Exception as e:
                log.warning(f"Query composition error:\n {e}")
                return False

    def select(self, _selector:str, _from:str, *vars) -> 'SQLiteQuery':
        self._add_part(QueryPartType.SELECT, f"SELECT {_selector} FROM {_from}", vars)
        return self
    
    def delete(self, _from:str, *vars) -> 'SQLiteQuery':
        self._add_part(QueryPartType.DELETE, f"DELETE FROM {_from}", vars)
        return self
    
    def insert(self, _into:str, **kvars ) -> 'SQLiteQuery':
        names = kvars.keys()
        values = kvars.values()
        valstr = ", ".join(["?"]*len(values))
        
        self._add_part(QueryPartType.INSERT, f"INSERT INTO {_into} ({','.join(names)}) VALUES ({valstr})", values)
        return self
    
    def update(self, _table:str, **kvars) -> 'SQLiteQuery':
        names = kvars.keys()
        values = kvars.values()
        valstr = ", ".join([f"{name}=?" for name in names])
        
        self._add_part(QueryPartType.UPDATE, f"UPDATE {_table} SET {valstr}", values)
        return self

    def where(self, **kvars) -> 'SQLiteQuery':
        names = kvars.keys()
        vars = kvars.values()
        valstr = ",".join([f"{name}=?" for name in names])
        
        self._add_part(QueryPartType.CONDITION, f"WHERE {valstr}", vars)
        return self

    def create_table(self, _name:str, _scheme:TableScheme, *vars):
        supplement = self._make_supplement("CREATE_TABLE_SUPPLEMENT")
        columns = ', '.join(_scheme.columns)
        
        self._add_part(QueryPartType.CREATE, f"CREATE TABLE {supplement} {_name} ({columns})", vars)
        return self
        

    def limit(self, _limit, *vars):
        self._add_part(QueryPartType.ADDITIONAL, f"LIMIT {_limit}", vars)
        return self

    def offset(self, _offset, *vars):
        self._add_part(QueryPartType.ADDITIONAL, f"OFFSET {_offset}", vars)
        return self
    
    def if_not_exists(self):
        self._set_supplement("CREATE_TABLE_SUPPLEMENT","IF NOT EXISTS")
        return self
    
    def next(self):
        self._add_part(QueryPartType.END,";",{},())
        return self
    
    def _add_part(self, type:QueryPartType, query:str, vars:list=()) -> bool:
        if QueryPartType.is_statement(type):
            self._statement_cursor = len(self._statements)
            self._statements.append([(type, query, vars)])
            return True
        else:
            if len(self._statements) > 0:
                self._statements[self._statement_cursor].append((type, query, vars))
                return True
            else:
                log.error("Cannot append statement-part when no statement added.")
                return False
        
    
    def _make_supplement(self, name, fallback_value=""):
        id = f"{name}_{self._statement_cursor}"
        self._supplements[id] = fallback_value
        return f"{{{id}}}"
    
    def _set_supplement(self, name, value):
        id = f"{name}_{self._statement_cursor}"
        self._supplements[id] = value

class SQLiteTableQuery(SQLiteQuery):

    def __new__(cls: type['SQLiteTableQuery'], _socket:'SQLiteSocket', _table_name:str, _table_scheme:TableScheme) -> 'SQLiteTableQuery':
        obj = super().__new__(cls)
        """
        cols_as_args = [col._name+":'"+col._type+"'=None" for col in _table_scheme.values()]
        cols_as_list = [col._name+"="+col._name for col in _table_scheme.values()]
        _globals = sys.modules[cls.__module__].__dict__
        _locals = locals()
        _locals.update({"self":obj})
        _insert = create_fn("insert", ["self"]+cols_as_args, 
            [f"return super().insert(self.table_name, {', '.join(cols_as_list)})"],
            globals=_globals,
            locals=_locals)
        setattr(obj, "insert", _insert) 
        """
    
        return obj

    def __init__(self, socket:'SQLiteSocket', table_name:str, table_scheme:TableScheme):
        super().__init__(socket)
        self.table_name = table_name
        self.table_scheme = table_scheme

    def select(self, _selector:str, *vars) -> 'SQLiteTableQuery':
        return super().select(_selector, self.table_name, *vars)   

    def update(self, **kvars) -> 'SQLiteTableQuery':
        return super().update(self.table_name, **kvars)
    
    def insert(self, **kvars) -> 'SQLiteTableQuery':
        return super().insert(self.table_name, **kvars)
    
    def delete(self, *vars) -> 'SQLiteTableQuery':
        return super().delete(self.table_name, *vars)
    
    def create_table(self, *vars) -> 'SQLiteTableQuery':
        return super().create_table(self.table_name, self.table_scheme, *vars)
        
