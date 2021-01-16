""" Class and functions to handle url manipulation."""
from typing import Any, AnyStr, Optional, Union, Generator
from collections.abc import Iterable
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


class URLQueryParam:
    """ A class that mimic the behavior of javascript's built-in Web API
        URLSearchParam class in a pythonic way.
    """
    @staticmethod
    def parse_query(query: str) -> dict[str, Union[str, int, float, list[Union[str, int, float]]]]:
        """ Parse the query, return a dictionary. The keys of returned dict
            will ALWAYS be `str`. The values can be list of str or list of
            number (int or float).
        """
        def str_to_number(s: str) -> Union[str, int, float]:
            """ convert string to int or float if possible."""
            try:
                float(s)
            except ValueError:
                return s
            else:
                number = float(s)
                return int(number) if number.is_integer() else number

        query_dct = {}
        for key, value in parse_qsl(query):
            if key in query_dct:
                if isinstance(query_dct[key], list):
                    query_dct[key].append(str_to_number(value))
                else:
                    query_dct[key] = [query_dct[key], str_to_number(value)]
            else:
                query_dct[key] = str_to_number(value)

        return query_dct

    def __init__(self, query) -> None:
        self.query_param = self.parse_query(query)

    def __str__(self) -> str:
        return urlencode(self.query_param, doseq=True)

    def __repr__(self) -> str:
        return 'URLQueryParam({})'.format(', '.join([f'{k}={v}' for k, v in self.items()]))

    def keys(self) -> Iterable[str]:
        """ URLSearchParam.keys in a pythonic way ;-) """
        return self.query_param.keys()

    def values(self) -> Generator[Union[str, int, float], None, None]:
        """ URLSearchParam.forEach in a pythonic way ;-) """
        for value in self.query_param.values():
            if isinstance(value, list):
                for single_value in value:
                    yield single_value
            else:
                yield value

    def items(self) -> Iterable[tuple[str, Union[str, list]]]:
        """ URLSearchParam.entries in a pythonic way ;-) """
        return self.query_param.items()

    def set(self, key, value=None):
        """ URLSearchParam.set"""
        if value is None:
            return

        self.query_param[key] = value

    def get(self, key) -> Optional[Any]:
        """ URLSearchParam.get. If the value is a list, first element of the
            list will be returned. If the key does not exist, return None
        """
        if key not in self.query_param:
            return

        value = self.query_param[key]
        return value if not isinstance(value, list) else value[0]

    def get_all(self, key) -> Optional[list]:
        """ URLSearchParam.getAll. If the value is not a list, the value will
            be returned in a list. If the key does not exist, return empty list.
        """
        if key not in self.query_param:
            return []

        all_value = self.query_param[key]
        return all_value if isinstance(all_value, list) else [all_value]

    def has(self, key) -> bool:
        """ URLSearchParam.has"""
        return key in self.query_param

    def delete(self, key) -> None:
        """ URLSearchParam.delete """
        if key not in self.query_param:
            return

        del self.query_param[key]

    def append(self, key, value=None) -> None:
        if value is None:
            return

        if key not in self.query_param:
            self.query_param[key] = value
            return

        if isinstance(self.query_param[key], list):
            self.query_param[key].append(value)
        else:
            self.query_param[key] = [self.query_param[key], value]

    def extend(self, key, values=None) -> None:
        if values is None:
            return

        if key not in self.query_param:
            self.query_param[key] = list(values)
            return

        if isinstance(self.query_param[key], list):
            self.query_param[key].extend(values)
        else:
            self.query_param[key] = [self.query_param[key]] + list(values)

    def sort(self) -> None:
        """ URLSearchParam.sort"""
        return dict(sorted(self.query_param.items()))


class URL:
    """ A class that mimic the behavior of javascript's built-in Web API
        URL class in a pythonic way.
    """

    @staticmethod
    def parse_url(
        url: str
    ) -> tuple[Optional[AnyStr], Optional[AnyStr], Optional[AnyStr], Optional[AnyStr], Optional[AnyStr]]:
        """ Parse the attributes of url."""
        parsed = urlsplit(url)
        return parsed[:]

    def __init__(self, url: str) -> None:
        (
            self.scheme,
            self.netloc,
            self.path,
            self._query,
            self.fragment
        ) = self.parse_url(url)
        self.query_param = URLQueryParam(self._query)

    def __str__(self) -> str:
        return urlunsplit(
            (
                self.scheme,
                self.netloc,
                self.path,
                self.query,
                self.fragment,
            )
        )

    def __repr__(self) -> str:
        return 'URL(scheme={}, netloc={}, path={}, query={}, fragment={})'.format(
            self.scheme, self.netloc, self.path, self.query, self.fragment
        )

    def copy(self) -> 'URL':
        """ Return a copy of the URL object"""
        return URL(str(self))

    def to_string(self) -> str:
        """ Return a string version of URL object, reflect the change of query if the query_param has changed."""
        return str(self)

    @property
    def query(self):
        """ Query property will be changed as the query_param is changed."""
        return str(self.query_param)
