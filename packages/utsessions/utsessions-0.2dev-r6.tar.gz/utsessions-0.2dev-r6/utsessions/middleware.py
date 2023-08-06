"""Middleware pieces for ut_session"""
from utsessions.sessions import SessionCollector

class UTSessionMiddleware(object):

    def __init__(self):
        """Amorcing the datas"""
        self._user_sessions = {}

    def process_request(self, request):
        """Attacking the view with the middleware"""
        return self.check_sessions(request)

    def check_sessions(self, request):
        """Check for unique sessions"""
        if request.user.is_authenticated():
            user_sessions = self.get_sessions(request.user.username)
            user_sessions.register(request)

            if user_sessions.opened > 1:
                user_sessions.set_unique()
        else:
            return None

    def get_sessions(self, key):
        """Return user sessions from his username as key"""
        self._user_sessions.setdefault(key, SessionCollector())
        return self._user_sessions.get(key)
