from .logger_gen import LoggerBuilder

global STATIC_LOGGER 

STATIC_LOGGER = LoggerBuilder.build("static")