"""Test for utsessions"""
import unittest
from datetime import datetime
from datetime import timedelta

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from utsessions.sessions import SessionCollector

class SessionCollectorTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('TestUser', 'test@test.com',
                                             'testtest')
        self.client.login(username='TestUser', password='testtest')

    def tearDown(self):
        self.client.logout()
        self.user.delete()

    def test_register(self):
        sc = SessionCollector()

        self.assertEquals(len(sc._sessions), 0)
        sc.register(self.client)
        self.assertEquals(len(sc._sessions), 1)
        sc.register(self.client)
        self.assertEquals(len(sc._sessions), 1)

        new_c = Client()
        new_c.login(username='TestUser', password='testtest')
        sc.register(new_c)
        self.assertEquals(len(sc._sessions), 2)

    def test_opened(self):
        sc = SessionCollector()

        self.assertEquals(sc.opened, 0)
        sc.register(self.client)
        self.assertEquals(sc.opened, 1)
        sc.register(self.client)
        self.assertEquals(sc.opened, 1)

        new_c = Client()
        new_c.login(username='TestUser', password='testtest')
        sc.register(new_c)
        self.assertEquals(len(sc._sessions), 2)

    def test_flush(self):
        sc = SessionCollector()

        self.assertEquals(len(sc._sessions), 0)
        sc._sessions['toto'] = (datetime.now(), self.client)
        self.assertEquals(len(sc._sessions), 1)
        sc.flush(session_limit=0)
        self.assertEquals(len(sc._sessions), 0)

        sc._sessions['toto'] = (datetime.now(), self.client)
        sc._sessions[self.client.session.session_key] = (datetime.now(), self.client)
        self.assertEquals(len(sc._sessions), 2)
        sc.flush(session_limit=0)
        self.assertEquals(len(sc._sessions), 1)

        sc._sessions['toto'] = (datetime.now(), self.client)
        sc._sessions[self.client.session.session_key] = (datetime.now() - timedelta(seconds=1000), self.client)
        self.assertEquals(len(sc._sessions), 2)
        sc.flush(session_limit=300)
        self.assertEquals(len(sc._sessions), 0)

        sc._sessions['toto'] = (datetime.now(), self.client)
        self.client.login(username='TestUser', password='testtest')
        sc._sessions[self.client.session.session_key] = (datetime.now() - timedelta(seconds=100), self.client)
        self.assertEquals(len(sc._sessions), 2)
        sc.flush(session_limit=300)
        self.assertEquals(len(sc._sessions), 1)

        sc._sessions['toto'] = (datetime.now(), self.client)
        self.client.login(username='TestUser', password='testtest')
        sc.register(self.client)
        new_c = Client()
        new_c.login(username='TestUser', password='testtest')
        sc.register(new_c)
        sc.flush(session_limit=300)
        self.assertEquals(len(sc._sessions), 2)

    def test_get_current_session_key(self):
        sc = SessionCollector()
        sc._sessions['toto'] = (datetime.now(), self.client)
        sc._sessions['tata'] = (datetime.now() - timedelta(seconds=100), self.client)
        self.assertEquals(sc.get_current_session_key(session_token_limit=300), 'tata')
        sc.flush()
        sc._sessions['toto'] = (datetime.now(), self.client)
        sc._sessions['titi'] = (datetime.now() + timedelta(seconds=100), self.client)
        self.assertEquals(sc.get_current_session_key(session_token_limit=300), 'toto')
        sc.flush()
        sc._sessions['toto'] = (datetime.now() - timedelta(seconds=600), self.client)
        sc._sessions['tutu'] = (datetime.now(), self.client)
        self.assertEquals(sc.get_current_session_key(session_token_limit=300), 'tutu')
        sc.flush()
        sc._sessions['toto'] = (datetime.now(), self.client)
        sc._sessions['tete'] = (datetime.now() + timedelta(seconds=100), self.client)
        self.assertEquals(sc.get_current_session_key(session_token_limit=0), 'tete')

    def test_set_unique(self):
        sc = SessionCollector()
        sc._sessions['toto'] = (datetime.now(), self.client)
        sc._sessions['tata'] = (datetime.now() - timedelta(seconds=100), self.client)
        sc._sessions['titi'] = (datetime.now() + timedelta(seconds=100), self.client)
        sc.set_unique()
        self.assertEqual(len(sc._sessions), 1)

