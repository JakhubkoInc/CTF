import logging 

ENCODING = "utf-8"
class Log:
  
  MSG_FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
  STDOUT_LOG_LEVEL = logging.DEBUG
  FILE_PATH = "logs/{0}.log"
