from .myutil import myuuid
from threading import Timer
import time
from configuration import mysettings
session = {}
sessionTimer = {}


def timer():
    clearList = []
    for t in sessionTimer:
        if t < time.time() - mysettings.settings['sessionCycleSeconds']:
            clearList.append(t)
    for t in clearList:
        if session.get(sessionTimer[t], None):
            del session[sessionTimer[t]]
        del sessionTimer[t]


Timer(mysettings.settings['sessionCycleSeconds'], timer).start()


class MySession:
    def __init__(self, handler):
        self.handler = handler

    def __getitem__(self, key):
        # 6f2610266c159b4a2b6d9c649a7319ec
        cookieid = self.handler.get_cookie('mycookie')
        if cookieid:
            info = session.get(cookieid, None)
            if info:
                result = info.get(key, None)
                return result
            else:
                return None
        else:
            return None

    def __setitem__(self, key, value):
        cookieid = self.handler.get_cookie('mycookie')

        if cookieid:
            info = session.get(cookieid, None)
            if info:
                info[key] = value
            else:
                r = {}
                r[key] = value
                session[cookieid] = r
        else:
            r = {}
            r[key] = value
            cookieid = myuuid()
            session[cookieid] = r
            sessionTimer[time.time()] = cookieid
            self.handler.set_cookie('mycookie', cookieid,
                                    expires_days=mysettings.settings['sessionCycleDays'])

    def __delitem__(self, key):
        cookieid = self.handler.get_cookie('mycookie')
        if cookieid:
            info = session.get(cookieid, None)
            if info:
                result = info.get(key, None)
                if result:
                    del info[key]
