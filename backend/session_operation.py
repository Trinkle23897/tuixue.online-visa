""" Definition of 3 classes:
    1. Session: Object used to store the session string retrieved from crawler server.
    2. SessionCache: Container that cache the session by visa_type and places, along with
        method for manipulating the session.

    Refactored out from ../global/crawler/lite_visa.py
"""
import os
import json
import util
import random
import string
import logging
from queue import Queue
from collections import defaultdict
from datetime import datetime, timedelta
from typing import DefaultDict, List, Optional, Sequence, Tuple, Union

import global_var as G


class Session:
    """ Store the session from CGI/AIS systems.
        AIS system session has a variable `schedule_id` coming along, in order to
        align the attributes of session objects from two systems, the field with be
        None for session instances of CGI.
    """

    def __init__(
        self,
        session: Union[str, Sequence[str]],
        sys: str = 'cgi'
    ) -> None:
        if sys not in ('cgi', 'ais'):
            raise ValueError(f'argument `sys` can only be \'cgi\' or \'ais\', get {sys}')
        if sys == 'cgi' and not isinstance(session, str):
            raise TypeError(f'CGI system should receive a str for session arg, but get {session}')
        if sys == 'ais' and not isinstance(session, (tuple, list)):
            raise TypeError(f'AIS system should receive a tuple for session arg, but get {session}')

        self._session = session if sys == 'cgi' else tuple(session)  # keep the (sess, sched_id) of ais in a tuple
        self.sys = sys
        self.logger = logging.getLogger(G.GlobalVar.var_dct['log_name'])

        self.logger.debug('Generate new session: %s', self.__repr__())

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(session={self._session}, sys={self.sys})'

    def to_json(self) -> dict:
        """ Return serializable object from Session object."""
        return {'session': self._session, 'sys': self.sys}

    @property
    def session(self) -> str:
        """ Return session string, regardless of target system."""
        if self.sys == 'ais':
            return self._session[0]
        elif self.sys == 'cgi':
            return self._session

    @property
    def schedule_id(self) -> Optional[str]:
        """ Return schedule id string for AIS system session, else None"""
        if self.sys == 'ais':
            return self._session[1]
        else:
            return None


def random_session(sys: str) -> Session:
    sess = 'placeholder_{}'.format(''.join(random.choices(string.ascii_lowercase, k=16)))
    if sys == 'ais':
        random_sched_id = ''.join(random.choices(string.digits, k=6))
        sess = (sess, random_sched_id)
    return Session(session=sess, sys=sys)


class SessionCache:
    """ A container that store all the sessions by visa_type and places, along
        with thread safe methods to manipulate it.
    """
    @staticmethod
    def inititae_session_cache(
        sys: str,
        session: DefaultDict[str, DefaultDict[str, List[Session]]],
        session_idx: DefaultDict[str, DefaultDict[str, int]],
    ) -> Tuple[DefaultDict[str, DefaultDict[str, List[Session]]], DefaultDict[str, DefaultDict[str, int]]]:
        """ When there is no session cache file or reading a sessoin cache file
            in __init__ is failing, this method will be called to generate a new
            session cache data structure with random sessions filling in as pla-
            ceholders.
        """
        with G.LOCK:
            for visa_type, sess_pool_size in G.SESS_POOL_SIZE[sys].items():
                for loc in G.SYS_LOCATION[sys]:
                    session[visa_type][loc] = session[visa_type][loc][:sess_pool_size]
                    while len(session[visa_type][loc]) < sess_pool_size:
                        session[visa_type][loc].append(random_session(sys))
                    session_idx[visa_type][loc] = 0
        return session, session_idx

    def __init__(self) -> None:
        self.session = defaultdict(lambda: defaultdict(list))
        self.session_idx = defaultdict(lambda: defaultdict(int))
        now = datetime.now()
        self.session_avail = defaultdict(lambda: defaultdict(lambda: now))
        self.logger = logging.getLogger(G.GlobalVar.var_dct['log_name'])

        # read cached session pool (if any)
        sys = G.value('target_system', None)
        session_file = G.value('session_file', 'session.json')
        if sys is None:
            self.logger.error('Not target system given')
            raise ValueError('The target system is not set!')

        if os.path.exists(session_file):
            with open(session_file) as f:
                try:
                    old_session = json.load(f)
                    if not isinstance(old_session, dict):
                        raise TypeError()
                except json.decoder.JSONDecodeError:
                    self.logger.debug('session.json is empty or borken written')
                except TypeError:
                    self.logger.debug('session.json doesn\'t store a dictionary.')
                else:
                    for visa_type, loc_sess_lst in old_session.items():
                        for loc, sess_lst in loc_sess_lst.items():
                            self.session[visa_type][loc] = [Session(**session) for session in sess_lst]
                            self.session_idx[visa_type][loc] = 0  # set currently used index to 0
        self.session, self.session_idx = self.inititae_session_cache(sys, self.session, self.session_idx)
        self.save()

    def save(self):
        """ Write the current session into disk."""
        session_file = G.value('session_file', 'session.json')
        with G.LOCK:

            session_json = defaultdict(lambda: defaultdict(list))
            for visa_type, loc_sess_dct in self.session.items():
                for loc, sess_lst in loc_sess_dct.items():
                    session_json[visa_type][loc] = [session.to_json() for session in sess_lst]

            with open(session_file, 'w') as f:
                json.dump(dict(session_json), f, indent=4, ensure_ascii=False)

            self.logger.debug('Write session cache into disk: %s', session_file)

    def get_session(self, visa_type: str, location: str) -> Session:
        """ Return the cached session object by visa_type and location."""
        if visa_type not in G.VISA_TYPES or location not in [*G.CGI_LOCATION, *G.AIS_LOCATION]:
            return
        if datetime.now() < self.session_avail[visa_type][location]:
            return

        with G.LOCK:  # is locking here necessary?
            sess_lst = self.session[visa_type][location]
            sess_idx = self.session_idx[visa_type][location]
            session = sess_lst[sess_idx % len(sess_lst)]
            self.logger.debug('get session %s', session)
            self.session_idx[visa_type][location] += 1

        return session

    def replace_session(
        self,
        visa_type: str,
        location: str,
        session: Session,
        new_session: Session,
    ) -> None:
        """ Replace session immediately with a new session object provided.
            Every time the sesssion is update, write to the file.
        """
        if visa_type not in G.VISA_TYPES or location not in [*G.CGI_LOCATION, *G.AIS_LOCATION]:
            return

        with G.LOCK:  # is locking here necessary?
            sess_lst = self.session[visa_type][location]

            try:
                sess_idx = [sess.session for sess in sess_lst].index(session.session)
            except ValueError:
                self.logger.debug('Error: given session is not in the session list.')
                return
            else:
                self.session[visa_type][location][sess_idx] = new_session
                self.logger.debug('Replace session | OLD: %s | NEW: %s', session, new_session)

        self.save()

    def produce_new_session_request(
        self,
        visa_type: str,
        location: str,
        session: Session,
        task_queue: Queue = G.SESSION_UPDATE_QUEUE
    ) -> None:
        """ Put the session to be replaced in the task queue for visa fetched to update."""
        self.logger.debug(
            'Produce session update event for %s-%s | Current queue size: %d',
            visa_type,
            location,
            task_queue.qsize()
        )
        task_queue.put((visa_type, location, session))

    def contain_session(self, visa_type: str, location: str, session: Session) -> bool:
        """ For a given session, return whether or not the session is in the cache"""
        if datetime.now() < self.session_avail[visa_type][location]:
            return False
        sess_str_lst = [sess.session for sess in self.session[visa_type][location]]
        return session.session in sess_str_lst

    def mark_unavailable(
        self, visa_type: str, location: str, cd: timedelta = timedelta(hours=G.CD_HOURS)
    ) -> None:
        self.logger.warning(f"mark {visa_type} {location} unavailable for {cd.seconds}s")
        with G.LOCK:
            self.session_avail[visa_type][location] = datetime.now() + cd


if __name__ == "__main__":
    # Manual testing

    from pprint import pprint

    test_log = 'test_session_log'
    G.assign('log_name', test_log)
    util.init_logger(test_log, './logs', debug=True)
    for sys in ('cgi', 'ais'):
        G.assign('target_system', sys)
        G.assign('session_file', f'test_{sys}_session.json')
        sc = SessionCache()

        if sys == 'cgi':
            sess = sc.get_session('F', '金边')
            print(sess)
            new_sess = Session(
                session='new_sess_{}'.format(''.join(random.choices(string.ascii_lowercase, k=16))),
                sys='cgi'
            )
            sc.replace_session('F', '金边', sess, new_sess)
            pprint(sc.session['F']['金边'])
        elif sys == 'ais':
            sess = sc.get_session('F', 'en-gb')
            print(sess)
            new_sess = Session(
                session=(
                    'new_sess_{}'.format(''.join(random.choices(string.ascii_lowercase, k=16))),
                    'new_sched_id_{}'.format(''.join(random.choices(string.digits, k=6)))
                ),
                sys='ais'
            )
            sc.replace_session('F', 'en-gb', sess, new_sess)
            pprint(sc.session['F']['en-gb'])
