"""Manage videos from the Canal+ website."""

class Show(object):

    def __init__(self, pid, nickname, fullname):
        self.pid = pid
        self.nickname = nickname
        self.fullname = fullname


SHOW_BY_NICK = {}
SHOW_BY_PID = {}

for show in [Show(1830, 'zapping', u'Le Zapping'),
             Show(1784, 'guignoles', u'Les Gignoles'),
             Show(1787, 'magzin', u'Groland Magzin')]:
    SHOW_BY_NICK[show.nickname] = show
    SHOW_BY_PID[show.pid] = show
