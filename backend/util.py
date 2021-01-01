""" Some utility functions and class."""
import os
import logging
from typing import Tuple
from datetime import datetime, timezone
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

    # Commenting out the stdout streaming for production server.
    # stream_handler = logging.StreamHandler()
    # stream_handler.setFormatter(fmt=log_fmt)

    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO if not debug else logging.DEBUG)
    logger.addHandler(file_handler)
    # logger.addHandler(stream_handler)

    return logger


def construct_data_file_path(
    visa_type: str,
    location: str,
    dt_str: str = datetime.now().strftime('%Y/%m/%d'),
) -> str:
    """ Construct data file path."""
    return os.path.join(G.DATA_PATH, visa_type, location, dt_str)


def file_line_to_dt(line: str) -> Tuple[datetime, datetime]:
    """ Convert a line in data file to datetime object"""
    time_of_update, available_dt = line.strip().split()
    return datetime.strptime(time_of_update, '%H:%M').time(), datetime.strptime(available_dt, '%Y/%m/%d')


def dt_to_utc(dt: datetime, remove_second: bool = False) -> int:
    """ Convert datetime to utc timestamp, for write_time."""
    if remove_second:
        dt = dt.replace(second=0, microsecond=0)
    return int(1000 * dt.replace(tzinfo=timezone.utc).timestamp())
