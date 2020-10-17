""" RESTful API for http://tuixue.online/global/"""

import os
from enum import Enum
from typing import Optional, List
from datetime import datetime, timedelta

from fastapi import FastAPI

import util
from global_var import USEmbassy, CGI_LOCATION_DOMESTIC

EMBASSY_LST = USEmbassy.get_embassy_lst()
app = FastAPI()


# These classes serve for the purpose of path/query parameter type chechking for FastAPI
class VisaType(str, Enum):
    F = 'F'
    B = 'B'
    H = 'H'
    O = 'O'
    L = 'L'


class System(str, Enum):
    CGI = 'cgi'
    AIS = 'ais'


class Region(str, Enum):
    SOUTH_EAST_ASIA = 'SOUTH_EAST_ASIA'
    EAST_ASIA = 'EAST_ASIA'
    WEST_ASIA = 'WEST_ASIA'
    SOUTH_ASIA = 'SOUTH_ASIA'
    OCEANIA = 'OCEANIA'
    WEST_EUROPE = 'WEST_EUROPE'
    EAST_EUROPE = 'EAST_EUROPE'
    NORTH_AMERICA = 'NORTH_AMERICA'
    SOUTH_AMERICA = 'SOUTH_AMERICA'


class Continent(str, Enum):
    ASIA = 'ASIA'
    OCEANIA = 'OCEANIA'
    EUROPE = 'EUROPE'
    NORTH_AMERICA = 'NORTH_AMERICA'
    SOUTH_AMERICA = 'SOUTH_AMERICA'


class Country(str, Enum):
    CHN = 'CHN'
    SGP = 'SGP'
    KHM = 'KHM'
    KOR = 'KOR'
    JPN = 'JPN'
    NPL = 'NPL'
    THA = 'THA'
    ARE = 'ARE'
    TUR = 'TUR'
    AUS = 'AUS'
    CHE = 'CHE'
    GBR = 'GBR'
    SRB = 'SRB'
    FRA = 'FRA'
    GRC = 'GRC'
    CAN = 'CAN'
    MEX = 'MEX'
    ECU = 'ECU'
    COL = 'COL'
    BRB = 'BRB'


def generate_tabular_data(
    visa_type: str,
    embassy_lst: List[USEmbassy],
    date_range: List[datetime]
):
    """ Generate tabular visa status data from given visa_type, embassy list and date range."""
    tabular_data = []
    for date in date_range:
        data_row = {'date': date.strftime('%Y/%m/%d'), 'availability': []}
        for embassy in embassy_lst:
            file_path = util.construct_data_file_path(visa_type, embassy.location, date.strftime('%Y/%m/%d'))
            if not os.path.exists(file_path):
                data_row['availability'].append({'location': embassy.code, 'earliest': None, 'latest': None})
                continue

            try:
                earliest_dt = util.get_earliest_dt(file_path).strftime('%Y/%m/%d')
            except util.EmptyDataFile:
                earliest_dt = None

            try:
                latest_dt = util.get_latest_update_dt(file_path).strftime('%Y/%m/%d')
            except util.EmptyDataFile:
                latest_dt = None

            data_row['availability'].append({'location': embassy.code, 'earliest': earliest_dt, 'latest': latest_dt})

        tabular_data.append(data_row)

    return tabular_data


@app.get('/')
def handshake():
    """ Index page that returns a 200 status with a OK message."""
    return {'status_code': 200, 'msg': 'OK'}


@app.get('/backend/global')
def get_global_visa_status(
    visa_type: VisaType = VisaType.F,
    sys: System = System.CGI,
    region: Optional[Region] = None,
    # continent: Optional[Continent] = None,
    # country: Optional[Country] = None,
    exclude_domestic: bool = True,
    skip: int = 0,
    take: int = 15,
):
    """ Get the global visa appointment status with given query."""

    today = datetime.today()
    dt_range = [today - timedelta(days=skip + d) for d in range(take)]

    embassy_lst = [embassy for embassy in EMBASSY_LST if embassy.sys == sys]
    if exclude_domestic:
        embassy_lst = [embassy for embassy in embassy_lst if embassy.location not in CGI_LOCATION_DOMESTIC]
    if region is not None:
        embassy_lst = [embassy for embassy in embassy_lst if embassy.region == region]

    tabular_data = generate_tabular_data(visa_type, embassy_lst, dt_range)

    return {'visa_type': visa_type, 'region': region, 'sys': sys, 'visa_status': tabular_data}


@app.get('/backend/domestic')
def get_domestic_visa_status(visa_type: VisaType = VisaType.F, skip: int = 0, take: int = 15):
    """ Get the domestic visa appointment status with given query."""
    today = datetime.today()
    dt_range = [today - timedelta(days=skip + d) for d in range(take)]

    embassy_lst = [embassy for embassy in EMBASSY_LST if embassy.location in CGI_LOCATION_DOMESTIC]

    tabular_data = generate_tabular_data(visa_type, embassy_lst, dt_range)
    return {'visa_type': visa_type, 'visa_status': tabular_data}
