""" Definition of 2 classes:
    1. Session: Object used to store the session string retrieved from crawler server.
    2. SessionCache: Container that cache the session by visa_type and places, along with
        method for manipulating the session.

    Refactored out from ../global/crawler/lite_visa.py
"""
import os
import json
import random
import string
import logging
from queue import Queue
from typing import Optional
from collections import defaultdict

import global_var as G


class Session:
    """ Store the session from CGI/AIS systems.
        AIS system session has a variable `schedule_id` coming along, in order to
        align the attributes of session objects from two systems, the field with be
        None for session instances of CGI.
    """

    def __init__(self, session: str, schedule_id: Optional[str] = None, sys: str = 'cgi'):
        self.session = session
        self.schedule_id = schedule_id
        self.sys = sys
        self.logger = logging.getLogger(G.GlobalVar.var_dct['log_name'])

        if self.sys == 'cgi' and self.schedule_id is not None:
            raise TypeError(f'CGI system shouldn\'t have schedule_id but get {self.schedule_id}!')
        self.logger.debug('Generate new session: %s | %s | session object id: %s', self.session, self.sys, id(self))

    def to_json(self):
        """ Return serializable object from Session object."""
        return {'session': self.session, 'schedule_id': self.schedule_id, 'sys': self.sys}

    @property
    def is_ais(self):
        """ Flag for AIS session."""
        return self.sys == 'ais'

    @property
    def is_cgi(self):
        """ Flag for CGI session.
            (Can be totally unnecessary, just can't help it...
        """
        return self.sys == 'cgi'


class SessionCache:
    """ A container that store all the sessions by visa_type and places, along
        with thread safe methods to manipulate it.
    """
    def __init__(self):
        self.session = defaultdict(lambda: defaultdict(list))
        self.session_idx = defaultdict(lambda: defaultdict(list))
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
                    self.logger.debug('session.json is empty.')
                except TypeError:
                    self.logger.debug('session.json doesn\'t store a dictionary.')
                else:
                    for visa_type, loc_sess_lst in old_session.items():
                        for loc, sess_lst in loc_sess_lst.items():
                            self.session[visa_type][loc] = [Session(**session) for session in sess_lst]
                            self.session_idx[visa_type][loc] = 0  # set currently used index to 0

        else:  # Initiate the pool size
            with G.LOCK:
                for visa_type, sess_pool_size in G.SESS_POOL_SIZE[sys].items():
                    for loc in G.SYS_LOCATION[sys]:
                        self.session[visa_type][loc] = [
                            Session(
                                session='placeholder_{}'.format(
                                    ''.join([random.choice(string.ascii_lowercase) for _ in range(16)])
                                ),
                                schedule_id=''.join(
                                    [random.choice(string.digits) for _ in range(6)]
                                ) if sys == 'ais' else None,
                                sys=sys,
                            ) for _ in range(sess_pool_size)
                        ]
                        self.session_idx[visa_type][loc] = 0
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

    def get_session(self, visa_type: str, location: str):
        """ Return the cached session object by visa_type and location."""
        if visa_type not in G.VISA_TYPES or location not in [*G.CGI_LOCATION, *G.AIS_LOCATION]:
            return

        with G.LOCK:  # is locking here necessary?
            sess_lst = self.session[visa_type][location]
            sess_idx = self.session_idx[visa_type][location]
            session = sess_lst[sess_idx % len(sess_lst)]
            self.logger.debug('get session %s', session.session)
            self.session_idx[visa_type][location] += 1

        return session

    def replace_session(
        self,
        visa_type: str,
        location: str,
        session: Session,
        new_session: Session,
    ):
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
                self.logger.debug('Replace session | OLD: %s | NEW: %s', session.session, new_session.session)

        self.save()

    def produce_new_session_request(
        self,
        visa_type: str,
        location: str,
        session: Session,
        task_queue: Queue = G.SESSION_UPDATE_QUEUE
    ):
        """ Put the session to be replaced in the task queue for visa fetched to update."""
        self.logger.debug(
            'Produce session update event for %s-%s | Current queue size: %d',
            visa_type,
            location,
            task_queue.qsize()
        )
        task_queue.put((visa_type, location, session))
