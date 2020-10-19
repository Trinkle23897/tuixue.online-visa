""" A thread-safe global variable getter-setter interface."""

import os
from queue import Queue
from typing import List
from threading import Lock

DATA_PATH = os.path.join(os.curdir, 'data')
EMAIL_SUBSCRIPTION_PATH = os.path.join(os.curdir, 'data', 'subscription.json')

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

SESSION_UPDATE_QUEUE = Queue()

REGION_LOCATION_MAPPING = {
    'SOUTH_EAST_ASIA': ['pp', 'sg', 'bkk', 'cnx'],
    'EAST_ASIA': [
        'sel', 'fuk', 'itm', 'oka', 'cts', 'hnd',
        'bj', 'sh', 'cd', 'gz', 'sy', 'hk', 'tp',
    ],
    'WEST_ASIA': ['auh', 'dxb', 'esb', 'ist'],
    'SOUTH_ASIA': ['ktm'],
    'OCEANIA': ['mel', 'per', 'syd'],
    'WEST_EUROPE': ['brn', 'bfs', 'lcy', 'cdg', 'ath'],
    'EAST_EUROPE': ['beg'],
    'NORTH_AMERICA': [
        'yyc', 'yhz', 'yul', 'yow', 'yqb', 'yyz', 'yvr',
        'bgi', 'cjs', 'gdl', 'hmo', 'cvj', 'mid', 'mex',
        'mty', 'ols', 'nld', 'tij'
    ],
    'SOUTH_AMERICA': ['gye', 'uio', 'bog']
}

CONTINENT_COUNTRY_LOCATION_MAPPING = {
    'ASIA': {
        'CHN': ['bj', 'sh', 'cd', 'gz', 'sy', 'hk', 'tp'],
        'SGP': ['sg'],
        'KHM': ['pp'],
        'KOR': ['sel'],
        'JPN': ['fuk', 'itm', 'oka', 'cts', 'hnd'],
        'NPL': ['ktm'],
        'THA': ['bkk', 'cnx'],
        'ARE': ['auh', 'dxb'],
        'TUR': ['esb', 'ist'],
    },
    'OCEANIA': {
        'AUS': ['mel', 'per', 'syd'],
    },
    'EUROPE': {
        'CHE': ['brn'],
        'GBR': ['bfs', 'lcy'],
        'SRB': ['beg'],
        'FRA': ['cdg'],
        'GRC': ['ath'],
    },
    'NORTH_AMERICA': {
        'CAN': ['yyc', 'yhz', 'yul', 'yow', 'yqb', 'yyz', 'yvr'],
        'MEX': ['cjs', 'gdl', 'hmo', 'cvj', 'mid', 'mex', 'mty', 'ols', 'nld', 'tij'],
    },
    'SOUTH_AMERICA': {
        'ECU': ['gye', 'uio'],
        'COL': ['bog'],
        'BRB': ['bgi'],
    }
}

EMBASSY_LOC = [
    ('北京', 'Beijing', 'bj', 'cgi'),
    ('上海', 'Shanghai', 'sh', 'cgi'),
    ('成都', 'Chengdu', 'cd', 'cgi'),
    ('广州', 'Guangzhou', 'gz', 'cgi'),
    ('沈阳', 'Shenyang', 'sy', 'cgi'),
    ('香港', 'Hongkong', 'hk', 'cgi'),
    ('台北', 'Taipei', 'tp', 'cgi'),
    ('金边', 'Phnom Penh', 'pp', 'cgi'),
    ('新加坡', 'Singapore', 'sg', 'cgi'),
    ('首尔', 'Seoul', 'sel', 'cgi'),
    ('墨尔本', 'Melbourne', 'mel', 'cgi'),
    ('珀斯', 'Perth', 'per', 'cgi'),
    ('悉尼', 'Sydney', 'syd', 'cgi'),
    ('伯尔尼', 'Bern', 'brn', 'cgi'),
    ('福冈', 'Fukuoka', 'fuk', 'cgi'),
    ('大坂', 'Osaka', 'itm', 'cgi'),
    ('那霸', 'Naha', 'oka', 'cgi'),
    ('札幌', 'Sapporo', 'cts', 'cgi'),
    ('东京', 'Tokyo', 'hnd', 'cgi'),
    ('加德满都', 'Kathmandu', 'ktm', 'cgi'),
    ('曼谷', 'Bangkok', 'bkk', 'cgi'),
    ('清迈', 'Chiang Mai', 'cnx', 'cgi'),
    ('贝尔法斯特', 'Belfast', 'bfs', 'ais'),
    ('伦敦', 'London', 'lcy', 'ais'),
    ('卡尔加里', 'Calgary', 'yyc', 'ais'),
    ('哈利法克斯', 'Halifax', 'yhz', 'ais'),
    ('蒙特利尔', 'Montreal', 'yul', 'ais'),
    ('渥太华', 'Ottawa', 'yow', 'ais'),
    ('魁北克城', 'Quebec City', 'yqb', 'ais'),
    ('多伦多', 'Toronto', 'yyz', 'ais'),
    ('温哥华', 'Vancouver', 'yvr', 'ais'),
    ('阿布扎比', 'Abu Dhabi', 'auh', 'ais'),
    ('迪拜', 'Dubai', 'dxb', 'ais'),
    ('贝尔格莱德', 'Belgrade', 'beg', 'ais'),
    ('巴黎', 'Paris', 'cdg', 'ais'),
    ('瓜亚基尔', 'Guayaquil', 'gye', 'ais'),
    ('基多', 'Quito', 'uio', 'ais'),
    ('安卡拉', 'Ankara', 'esb', 'ais'),
    ('伊斯坦布尔', 'Istanbul', 'ist', 'ais'),
    ('雅典', 'Athens', 'ath', 'ais'),
    ('波哥大', 'Bogota', 'bog', 'ais'),
    ('布里奇顿', 'Bridgetown', 'bgi', 'ais'),
    ('华雷斯城', 'Ciudad Juarez', 'cjs', 'ais'),
    ('瓜达拉哈拉', 'Guadalajara', 'gdl', 'ais'),
    ('埃莫西约', 'Hermosillo', 'hmo', 'ais'),
    ('马塔莫罗斯', 'Matamoros', 'cvj', 'ais'),
    ('梅里达', 'Merida', 'mid', 'ais'),
    ('墨西哥城', 'Mexico City', 'mex', 'ais'),
    ('蒙特雷', 'Monterrey', 'mty', 'ais'),
    ('诺加莱斯', 'Nogales', 'ols', 'ais'),
    ('新拉雷多', 'Nuevo Laredo', 'nld', 'ais'),
    ('蒂华纳', 'Tijuana', 'tij', 'ais'),
]

VISA_TYPES = 'FBHOL'
VISA_TYPE_DETAILS = {'F': 'F1/J1', 'H': 'H1B', 'B': 'B1/B2', 'O': 'O1/O2/O3', 'L': 'L1/L2'}

# CGI/AIS_LOCATION are the parameters sent to crawler backend to retrieve session data
CGI_LOCATION_DOMESTIC = ['北京', '成都', '广州', '上海', '沈阳', '香港', '台北']
CGI_LOCATION_GLOBAL = ['金边', '新加坡', '首尔', '墨尔本', '珀斯', '悉尼', '伯尔尼', '福冈', '大坂', '那霸', '札幌', '东京', '加德满都', '曼谷', '清迈']
CGI_LOCATION = CGI_LOCATION_DOMESTIC + CGI_LOCATION_GLOBAL
AIS_LOCATION = ['en-gb', 'en-ca', 'en-ae', 'en-rs', 'en-mx', 'en-fr', 'en-ec', 'en-tr', 'en-gr', 'en-co', 'en-bb']
SYS_LOCATION = {'cgi': CGI_LOCATION, 'ais': AIS_LOCATION}

AIS_MONITORING_CITY = [  # filter of AIS visa data retrieved from cralwer backend by city
    'Belfast', 'London', 'Calgary', 'Halifax', 'Montreal',
    'Ottawa', 'Quebec City', 'Toronto', 'Vancouver', 'Abu Dhabi',
    'Dubai', 'Belgrade', 'Ankara', 'Istanbul', 'Athens',
    'Bogota', 'Bridgetown', 'Ciudad Juarez', 'Guadalajara', 'Hermosillo',
    'Matamoros', 'Merida', 'Mexico City', 'Monterrey', 'Nogales',
    'Nuevo Laredo', 'Tijuana', 'Paris', 'Guayaquil', 'Quito'
]

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
    def get_embassy_lst(cls):
        """ Return the list of USEmbassy objects."""
        return [cls(*embassy_attr) for embassy_attr in EMBASSY_LOC]

    def __init__(self, name_cn: str, name_en: str, code: str, sys: str):
        self.name_cn = name_cn
        self.name_en = name_en
        self.code = code
        self.sys = sys

    @property
    def location(self):
        """ Return the location value for data storage."""
        return self.name_cn if self.is_cgi else self.name_en

    @property
    def country(self):
        """ Return the ISO 3166-3 country code of the Embassy/Consulate."""
        for continent, country_dct in CONTINENT_COUNTRY_LOCATION_MAPPING.items():
            for country, embassy_lst in country_dct.items():
                if self.code in embassy_lst:
                    return country

    @property
    def continent(self):
        """ Return the continent UPPER_SNAKE_CASE of the Embassy/Consulate."""
        for continent, country_dct in CONTINENT_COUNTRY_LOCATION_MAPPING.items():
            for country, embassy_lst in country_dct.items():
                if self.code in embassy_lst:
                    return continent

    @property
    def region(self):
        """ Return the region UPPER_SNAKE_CASE of the Embassy/Consulate."""
        for region, embassy_lst in REGION_LOCATION_MAPPING.items():
            if self.code in embassy_lst:
                return region

    @property
    def is_ais(self):
        """ Return True if the embassy/consulate uses AIS system."""
        return self.sys == 'ais'

    @property
    def is_cgi(self):
        """ Return True if the embassy.consulate uses CGI system."""
        return self.sys == 'cgi'


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
