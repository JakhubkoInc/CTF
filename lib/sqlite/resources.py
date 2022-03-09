class SQLiteTags:
    
    PRIMARY_KEY = "PRIMARY KEY"

class SQLiteDatatype:
    
    INTEGER = "INT"
    "The value is a signed integer, stored in 1, 2, 3, 4, 6, or 8 bytes depending on the magnitude of the value."
    
    REAL = "REAL"
    "The value is a floating point value, stored as an 8-byte IEEE floating point number."
    
    TEXT = "TEXT"
    "The value is a text string, stored using the database encoding (UTF-8, UTF-16BE or UTF-16LE)."
    
    BLOB = "BLOB"
    "The value is a blob of data, stored exactly as it was input."
    
    
class MySQLDatatype:
  
    CHAR = lambda size=1: f"CHAR({int(size)})" 
    """
    A FIXED length string (can contain letters, numbers, and special characters).
    The size parameter specifies the column length in characters - can be from 0 to 255.
    Default is 1.
    """
    
    VARCHAR = lambda size=1: f"VARCHAR({int(size)})" 
    """
    A VARIABLE length string (can contain letters, numbers, and special characters).
    The size parameter specifies the maximum column length in characters - can be from 0 to 65535.
    Default is 1.
    """
    
    BINARY = lambda size=1: f"BINARY({int(size)})" 
    """
    Equal to CHAR(), but stores binary byte strings. The size parameter specifies the column length in bytes.
    Default is 1.
    """
    
    VARBINARY = lambda size=1: f"VARBINARY({int(size)})" 
    """
    Equal to VARCHAR(), but stores binary byte strings.
    The size parameter specifies the maximum column length in bytes.
    Default is 1.
    """
    
    TINYBLOB = "TINYBLOB"
    """
    For BLOBs (Binary Large Objects).
    Max length: 255 bytes
    """
    
    TINYTEXT = "TINYTEXT"
    """
    Holds a string with a maximum length of 255 characters.
    """
    
    TEXT = lambda size: f"TEXT({int(size)})" 
    """
    Holds a string with a maximum length of 65,535 bytes.
    """
    
    BLOB = lambda size: f"BLOB({int(size)})" 
    """
    For BLOBs (Binary Large Objects). Holds up to 65,535 bytes of data
    """
    
    MEDIUMTEXT = "MEDIUMTEXT"
    """
    Holds a string with a maximum length of 16,777,215 character.
    """

    MEDIUMBLOB = "MEDIUMBLOB"
    """
    For BLOBs (Binary Large Objects). Holds up to 16,777,215 bytes of data.
    """
    
    LONGTEXT = "LONGTEXT"
    """
    Holds a string with a maximum length of 4,294,967,295 characters.
    """
    
    LONGBLOB = "LONGBLOB"
    """
    For BLOBs (Binary Large Objects). Holds up to 4,294,967,295 bytes of data.
    """
    
    ENUM = lambda *vals: f"ENUM({', '.join(vals)})" 
    """
    A string object that can have only one value, chosen from a list of possible values.
    You can list up to 65535 values in an ENUM list.
    If a value is inserted that is not in the list, a blank value will be inserted.
    The values are sorted in the order you enter them.
    """
    
    SET = lambda *vals: f"SET({', '.join(vals)})" 
    """
    A string object that can have 0 or more values, chosen from a list of possible values. You can list up to 64 values in a SET list.
    """
    
    