'''
Created on 2009-4-16

@author: mingqi
'''
import logging
import sys

def get_logger(name):
    logger = logging.getLogger(name)
    hdlr = logging.StreamHandler(sys.stdout)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)
    return logger