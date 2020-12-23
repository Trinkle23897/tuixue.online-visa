""" A thread-safe global variable getter-setter interface."""

import os
import json
from queue import Queue
from threading import Lock
from collections import defaultdict
from typing import List, Optional, Union
from datetime import timedelta, timezone

DATA_PATH = os.path.join(os.curdir, 'data')  # dir stroing file-based data

with open(os.path.join(os.curdir, 'config', 'secret.json')) as f:
    SECRET = json.load(f)

MAX_EMAIL_SENT = 512  # maximum number of emails sent for one POST to email server

MONGO_CONFIG = {'host': '127.0.0.1', 'port': 27017, 'database': 'tuixue'}

CRAWLER_API = {
    'register': {
        'cgi': '/register/?type={}&place={}',
        'ais': '/ais/register/?code={}&email={}&pswd={}',
    },
    'refresh': {
        'cgi': '/refresh/?session={}',
        'ais': '/ais/refresh/?code={}&id={}&session={}'
    }
}
WAIT_TIME = {'register': 40, 'refresh': 7}

CD_HOURS = 4

SESSION_UPDATE_QUEUE = Queue()

COUTNRY_CODE_TO_UTC_OFFSET = {
    'ARE': 4, 'AUS': 10, 'BRB': -4, 'CAN': -5, 'CHE': 1,
    'CHN': 8, 'COL': -5, 'ECU': -5, 'FRA': 1, 'GBR': 0,
    'GRC': 2, 'JPN': 9, 'KHM': 7, 'KOR': 9, 'MEX': -6,
    'NPL': 5.75, 'SGP': 8, 'SRB': 1, 'THA': 7, 'TUR': 3
}

# Embassy/consulate attributes
# Tuple[name_cn, name_en, code, sys, region, continent, country]
EMBASSY_ATTR = [
    ('北京', 'Beijing', 'bj', 'cgi', 'DOMESTIC', 'ASIA', 'CHN', 8),
    ('上海', 'Shanghai', 'sh', 'cgi', 'DOMESTIC', 'ASIA', 'CHN', 8),
    ('成都', 'Chengdu', 'cd', 'cgi', 'DOMESTIC', 'ASIA', 'CHN', 8),
    ('广州', 'Guangzhou', 'gz', 'cgi', 'DOMESTIC', 'ASIA', 'CHN', 8),
    ('沈阳', 'Shenyang', 'sy', 'cgi', 'DOMESTIC', 'ASIA', 'CHN', 8),
    ('香港', 'Hongkong', 'hk', 'cgi', 'DOMESTIC', 'ASIA', 'CHN', 8),
    ('台北', 'Taipei', 'tp', 'cgi', 'DOMESTIC', 'ASIA', 'CHN', 8),
    ('金边', 'Phnom Penh', 'pp', 'cgi', 'SOUTH_EAST_ASIA', 'ASIA', 'KHM', 7),
    ('新加坡', 'Singapore', 'sg', 'cgi', 'SOUTH_EAST_ASIA', 'ASIA', 'SGP', 8),
    ('首尔', 'Seoul', 'sel', 'cgi', 'EAST_ASIA', 'ASIA', 'KOR', 9),
    ('墨尔本', 'Melbourne', 'mel', 'cgi', 'OCEANIA', 'OCEANIA', 'AUS', 10),
    ('珀斯', 'Perth', 'per', 'cgi', 'OCEANIA', 'OCEANIA', 'AUS', 10),
    ('悉尼', 'Sydney', 'syd', 'cgi', 'OCEANIA', 'OCEANIA', 'AUS', 10),
    ('伯尔尼', 'Bern', 'brn', 'cgi', 'WEST_EUROPE', 'EUROPE', 'CHE', 1),
    ('福冈', 'Fukuoka', 'fuk', 'cgi', 'EAST_ASIA', 'ASIA', 'JPN', 9),
    ('大坂', 'Osaka', 'itm', 'cgi', 'EAST_ASIA', 'ASIA', 'JPN', 9),
    ('那霸', 'Naha', 'oka', 'cgi', 'EAST_ASIA', 'ASIA', 'JPN', 9),
    ('札幌', 'Sapporo', 'cts', 'cgi', 'EAST_ASIA', 'ASIA', 'JPN', 9),
    ('东京', 'Tokyo', 'hnd', 'cgi', 'EAST_ASIA', 'ASIA', 'JPN', 9),
    ('加德满都', 'Kathmandu', 'ktm', 'cgi', 'SOUTH_EAST_ASIA', 'ASIA', 'NPL', 5.75),
    ('曼谷', 'Bangkok', 'bkk', 'cgi', 'SOUTH_EAST_ASIA', 'ASIA', 'THA', 7),
    ('清迈', 'Chiang Mai', 'cnx', 'cgi', 'SOUTH_EAST_ASIA', 'ASIA', 'THA', 7),
    ('贝尔法斯特', 'Belfast', 'bfs', 'ais', 'WEST_EUROPE', 'EUROPE', 'GBR', 0),
    ('伦敦', 'London', 'lcy', 'ais', 'WEST_EUROPE', 'EUROPE', 'GBR', 0),
    ('卡尔加里', 'Calgary', 'yyc', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'CAN', -5),
    ('哈利法克斯', 'Halifax', 'yhz', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'CAN', -5),
    ('蒙特利尔', 'Montreal', 'yul', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'CAN', -5),
    ('渥太华', 'Ottawa', 'yow', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'CAN', -5),
    ('魁北克城', 'Quebec City', 'yqb', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'CAN', -5),
    ('多伦多', 'Toronto', 'yyz', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'CAN', -5),
    ('温哥华', 'Vancouver', 'yvr', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'CAN', -5),
    ('阿布扎比', 'Abu Dhabi', 'auh', 'ais', 'WEST_ASIA', 'ASIA', 'ARE', 4),
    ('迪拜', 'Dubai', 'dxb', 'ais', 'WEST_ASIA', 'ASIA', 'ARE', 4),
    ('贝尔格莱德', 'Belgrade', 'beg', 'ais', 'EAST_EUROPE', 'EUROPE', 'SRB', 1),
    ('巴黎', 'Paris', 'cdg', 'ais', 'WEST_EUROPE', 'EUROPE', 'FRA', 1),
    ('瓜亚基尔', 'Guayaquil', 'gye', 'ais', 'SOUTH_AMERICA', 'SOUTH_AMERICA', 'ECU', -5),
    ('基多', 'Quito', 'uio', 'ais', 'SOUTH_AMERICA', 'SOUTH_AMERICA', 'ECU', -5),
    ('安卡拉', 'Ankara', 'esb', 'ais', 'WEST_ASIA', 'ASIA', 'TUR', 3),
    ('伊斯坦布尔', 'Istanbul', 'ist', 'ais', 'WEST_ASIA', 'ASIA', 'TUR', 3),
    ('雅典', 'Athens', 'ath', 'ais', 'WEST_EUROPE', 'EUROPE', 'GRC', 2),
    ('波哥大', 'Bogota', 'bog', 'ais', 'SOUTH_AMERICA', 'SOUTH_AMERICA', 'COL', -5),
    ('布里奇顿', 'Bridgetown', 'bgi', 'ais', 'NORTH_AMERICA', 'SOUTH_AMERICA', 'BRB', -4),
    ('华雷斯城', 'Ciudad Juarez', 'cjs', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'MEX', -6),
    ('瓜达拉哈拉', 'Guadalajara', 'gdl', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'MEX', -6),
    ('埃莫西约', 'Hermosillo', 'hmo', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'MEX', -6),
    ('马塔莫罗斯', 'Matamoros', 'cvj', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'MEX', -6),
    ('墨西哥城', 'Mexico City', 'mex', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'MEX', -6),
    ('蒙特雷', 'Monterrey', 'mty', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'MEX', -6),
    ('诺加莱斯', 'Nogales', 'ols', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'MEX', -6),
    ('新拉雷多', 'Nuevo Laredo', 'nld', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'MEX', -6),
    ('蒂华纳', 'Tijuana', 'tij', 'ais', 'NORTH_AMERICA', 'NORTH_AMERICA', 'MEX', -6),
]

VISA_TYPES = 'FBHOL'
VISA_TYPE_DETAILS = {'F': 'F1/J1', 'H': 'H1B', 'B': 'B1/B2', 'O': 'O1/O2/O3', 'L': 'L1/L2'}

# CGI/AIS_LOCATION are the parameters sent to crawler backend to retrieve session data
CGI_LOCATION = [emb[0] for emb in EMBASSY_ATTR if emb[3] == 'cgi']
AIS_LOCATION = ['en-gb', 'en-ca', 'en-ae', 'en-rs', 'en-mx', 'en-fr', 'en-ec', 'en-tr', 'en-gr', 'en-co', 'en-bb']
SYS_LOCATION = {'cgi': CGI_LOCATION, 'ais': AIS_LOCATION}

# filter of AIS visa data retrieved from cralwer backend by city
AIS_MONITORING_CITY = [emb[1] for emb in EMBASSY_ATTR if emb[3] == 'ais']

CGI_SESS_POOL_SIZE = {visa_type: 10 if visa_type == 'F' else 5 for visa_type in VISA_TYPES}
AIS_SESS_POOL_SIZE = {visa_type: 1 for visa_type in VISA_TYPES}
SESS_POOL_SIZE = {'cgi': CGI_SESS_POOL_SIZE, 'ais': AIS_SESS_POOL_SIZE}

CGI_FETCH_TIME_INTERVAL = {'F': 60, 'B': 120, 'H': 180, 'O': 180, 'L': 180}
AIS_FETCH_TIME_INTERVAL = {visa_type: 60 for visa_type in VISA_TYPES}
FETCH_TIME_INTERVAL = {'cgi': CGI_FETCH_TIME_INTERVAL, 'ais': AIS_FETCH_TIME_INTERVAL}

LOCK = Lock()


class USEmbassy:
    """ An abstraction represent a U.S. Embassy or Consulate"""
    @classmethod
    def get_embassy_lst(cls) -> List['__class__']:
        """ Return the list of USEmbassy objects."""
        return [cls(*embassy_attr) for embassy_attr in EMBASSY_ATTR]

    @classmethod
    def get_embassy_by_loc(cls, loc: str) -> Optional['__class__']:
        """ Return an USEbassy object by the location property."""
        return next((emb for emb in cls.get_embassy_lst() if emb.location == loc), None)

    @classmethod
    def get_embassy_by_code(cls, code: str) -> Optional['__class__']:
        """ Return an USEbassy object by the code property."""
        return next((emb for emb in cls.get_embassy_lst() if emb.code == code), None)

    @classmethod
    def get_region_mapping(cls) -> List[dict]:
        """ Return a region to embassy code mapping. In JSON convention."""
        return [
            {
                'region': region,
                'embassy_code_lst': [emb.code for emb in cls.get_embassy_lst() if emb.region == region]
            } for region in {emb.region for emb in cls.get_embassy_lst()}
        ]

    @classmethod
    def get_region_country_embassy_tree(cls) -> List[dict]:
        """ Return a region-country-embassy mapping"""
        rce_tree = defaultdict(lambda: defaultdict(list))
        for emb in cls.get_embassy_lst():
            rce_tree[emb.region][emb.country].append(emb.code)

        return [
            {
                'region': region,
                'country_embassy_map': [
                    {
                        'country': country,
                        'embassy_code_lst': embassy_code_lst,
                    } for country, embassy_code_lst in ce_map.items()
                ],
            } for region, ce_map in rce_tree.items()
        ]

    def __init__(
        self,
        name_cn: str,
        name_en: str,
        code: str,
        sys: str,
        region: str,
        continent: str,
        country: str,
        utcoffset: Union[float, int],
    ) -> None:
        self.name_cn = name_cn
        self.name_en = name_en
        self.code = code
        self.sys = sys
        self.region = region
        self.continent = continent
        self.country = country
        self.timezone = timezone(timedelta(hours=utcoffset))

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(name_cn={self.name_cn}, name_en={self.name_en}, code={self.code})'

    @property
    def location(self) -> str:
        """ Return the location value for data storage."""
        return self.name_cn if self.sys == 'cgi' else self.name_en


class GlobalVar:  # Can we just define a dictionary for it?
    """ Global variable class."""
    var_dct = {}


def assign(var_name, var_value):
    """ Assign value to the global variable."""
    with LOCK:
        GlobalVar.var_dct[var_name] = var_value


def value(var_name, default_value):
    """ Get value of the var_name
        Initiate and assign a new one if none exists.
    """
    with LOCK:
        if var_name not in GlobalVar.var_dct:
            GlobalVar.var_dct[var_name] = default_value
            return default_value
    return GlobalVar.var_dct[var_name]
