import logging
import os
import sys
from pathlib import Path

from ... import conf as cfg


class LoggerBuilder:
    
    def __init__(self):
        return Exception("Cannot create LoggerBuilder instance")
  
    @classmethod
    def build(cls:'LoggerBuilder', 
              name:str,
              file_path:str=cfg.Common.Log.FILE_PATH,
              msg_format:str=cfg.Common.Log.MSG_FORMAT,
              stream_log_level=cfg.Common.Log.STDOUT_LOG_LEVEL):
        log = logging.getLogger(name)
        logFormatter = logging.Formatter(msg_format)

        logdir = Path(file_path).parent
        if not logdir.exists():        
            os.makedirs(logdir, exist_ok=True)

        file_handler = logging.FileHandler(file_path.format(name),encoding=cfg.Common.ENCODING)
        file_handler.setFormatter(logFormatter)
        file_handler.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logFormatter)
        stream_handler.setLevel(stream_log_level)

        log.addHandler(file_handler)
        log.addHandler(stream_handler)
        log.setLevel(logging.DEBUG)
        log.debug(f"Log '{name}' built.")

        return log
    
    
def sync_default_log_format():
    logging.basicConfig(level=logging.INFO,format=cfg.Common.Log.MSG_FORMAT)

