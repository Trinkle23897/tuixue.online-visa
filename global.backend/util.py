""" Some utility functions and class."""
import os
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import global_var as G


def init_logger(log_name: str, log_dir: str, debug: bool = False):
    """ Initiate a logger."""
    log_fmt = logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s - %(message)s')

    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, f'{log_name}.log'),
        when='midnight',
        interval=1,
    )
    file_handler.suffix = '%Y%m%d'
    file_handler.setFormatter(fmt=log_fmt)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt=log_fmt)

    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO if not debug else logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def construct_data_file_path(
    visa_type: str,
    location: str,
    dt_str: str = datetime.now().strftime('%Y/%m/%d'),
):
    """ Construct data file path."""
    return os.path.join(G.DATA_PATH, visa_type, location, dt_str)


def file_line_to_dt(line: str, fmt: str = '%Y/%m/%d'):
    """ Convert a line in data file to datetime object"""
    return datetime.strptime(line.strip().split()[1], fmt)


def get_earliest_dt(file_path: str):
    """ Get the eariliest date from a visa status data file."""
    with open(file_path) as f:
        dt_lst = [file_line_to_dt(line) for line in f.readlines()]

    if len(dt_lst) == 0:
        raise EmptyDataFile()
    elif len(dt_lst) == 1:
        return dt_lst[0]
    else:
        return min(*dt_lst)

def get_latest_update_dt(file_path: str):
    with open(file_path) as f:
        dt_lst = [file_line_to_dt(line) for line in f.readlines()]

    if len(dt_lst) == 0:
        raise EmptyDataFile()
    else:
        return dt_lst[-1]


class EmptyDataFile(Exception):
    pass
