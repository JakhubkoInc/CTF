import atexit
from sqlite3.dbapi2 import Connection
from typing import TYPE_CHECKING

from testprog_common.lib.logging.static_log import STATIC_LOGGER as log


if TYPE_CHECKING:
    from sqlite3 import Cursor


class SQLiteSocket(Connection):
    """
    Expands sqlite3 connection api
    """
    
    def __init__(self, db_path:str):
        """
        Args:
            db_path (str): path to database file
        """
        super().__init__(db_path)
        self._db_path = db_path
        self.is_open = True
        self._open_query = None
        atexit.register(self.close)
    
    @property
    def cursor(self) -> 'Cursor':
        """
        Returns new cursor.
        """
        if self.is_open:
            return super().cursor()

        raise ConnectionError("SqliteSocket is not connected to the database, cannot create cursor.")
    

    def close(self):
        """
        If socket is alive, commits transactions and closes connection.\n
        Natively called at program exit.
        """
        if self.is_open:
            self.save()
            super().close()
            self.is_open = False
    
    def discard(self):
        """
        If socket is alive, closes connection without commiting transactions.\n
        """
        if self.is_open:
            self.close()
            self.is_open = False
    
    def save(self):
        """
        If socket is still alive, commits executed transactions.
        """
        if self.is_open:
            self.commit()
    
    
    
    