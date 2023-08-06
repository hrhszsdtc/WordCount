# -*- coding: utf-8 -*-

import logging
import os
import sys
import datetime


script_path = os.path.abspath(__file__)
script_folder = os.path.dirname(script_path)
os.chdir(script_folder)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
rq = datetime.datetime.now().strftime("%Y%m%d")[:None]
log_path = os.getcwd() + "/logs/"
log_name = log_path + rq + ".log"
logfile = log_name
if not os.path.exists(log_path):
    os.makedirs(log_path)
fh = logging.FileHandler(logfile, encoding="utf-8", mode="a+")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s"
)
fh.setFormatter(formatter)
logger.addHandler(fh)


def info(msg):
    sys.stdout.write(msg)
    logger.info(msg)


def error(msg):
    sys.stderr.write(msg)
    logger.error(msg)


def debug(msg):
    sys.stdout.write(msg)
    logger.debug(msg)


def critical(msg):
    sys.stderr.write(msg)
    logger.critical(msg)


def warning(msg):
    sys.stderr.write(msg)
    logger.warning(msg)
