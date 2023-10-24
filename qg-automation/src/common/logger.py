import logging
from logging.handlers import RotatingFileHandler
import sys

def get_logger(name = None):
    """ 
    function to set logger properties.
    parameter: name - default Value: None - Logs will be written to qg_executor.log file
    (In case user needs a different log file, then log_map should be updated with the required file name
     and the key to that file should be passed when logging is initialized)
    """
    
    formatter = logging.Formatter('%(asctime)s %(funcName)s(%(lineno)d) %(levelname)s: %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
    log_map = {"default": "qg_executor.log"}
    if name == None:
        name = "default"
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        fh = RotatingFileHandler(log_map[name], mode='w',encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(formatter)
        logger.addHandler(sh)
        logger.setLevel(logging.INFO)
    return logger