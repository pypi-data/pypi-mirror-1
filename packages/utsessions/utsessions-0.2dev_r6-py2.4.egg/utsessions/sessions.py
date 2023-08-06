"""Session collector for managing sessions instances"""
from datetime import datetime

from django.conf import settings
from django.contrib.auth import logout

SESSION_LIMIT_SECONDS = getattr(settings, 'SESSION_LIMIT_SECONDS', 0)
SESSION_TOKEN_LIMIT_SECONDS = getattr(settings, 'SESSION_TOKEN_LIMIT_SECONDS', 300)

class SessionCollector(object):
    """Collector of sessions for user"""
    def __init__(self):
        self._sessions = {}

    def register(self, request):
        """Register session by key with creation time"""
        if not request.session.session_key in self._sessions.keys():
            self._sessions[request.session.session_key] = (datetime.now(), request)

    @property
    def opened(self):
        """Return the number of sessions after a flush"""
        self.flush()
        return len(self._sessions)

    def flush(self, session_limit=SESSION_LIMIT_SECONDS):
        """Flush the cache of opened sessions and
        close expired session"""
        now = datetime.now()

        for session_key, values in self._sessions.items():
            creation_time, request = values
            delta = now - creation_time
            if session_limit and delta.seconds >= session_limit:
                logout(request)
            if not request.session.exists(session_key):
                del self._sessions[session_key]

    def set_unique(self):
        """Choose the current session, and close the others"""
        current_session_key = self.get_current_session_key()

        for session_key, values in self._sessions.items():
            if session_key != current_session_key:
                creation_time, request = values
                logout(request)
                del self._sessions[session_key]

    def get_current_session_key(self, session_token_limit=SESSION_TOKEN_LIMIT_SECONDS):
        """Return the current session key, selected by his creation time
        and his limit before destruction, we suppose that we always
        have 2 items in sessions"""
        sessions = self._sessions.items()[:2]

        if sessions[0][1][0] > sessions[1][1][0]:
            most_recent_session = sessions[0]
            most_oldest_session = sessions[1]
        else:
            most_recent_session = sessions[1]
            most_oldest_session = sessions[0]

        delta_oldest = datetime.now() - most_oldest_session[1][0]
        if session_token_limit and delta_oldest.seconds < session_token_limit:
            return most_oldest_session[0]
        return most_recent_session[0]

