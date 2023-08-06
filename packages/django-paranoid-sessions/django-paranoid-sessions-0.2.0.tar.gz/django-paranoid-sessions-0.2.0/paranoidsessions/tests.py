
import time

from django.test import TestCase
from django.conf.urls.defaults import *
from django.http import HttpResponse
from django.conf import settings

import paranoidsessions

def test_view(request):
    if "timestamp" not in request.session:
        request.session["timestamp"] = time.time()
    return HttpResponse("OK")

urlpatterns = patterns('',
  (r'^$', test_view),
  (r'^safeview$', test_view),
)

def request_filter(request):
    if "safe" in request.path:
        return False
    return True


def with_settings(**new_settings):
    """Decorator to temporarily change django settings during a test."""
    def with_settings_dec(func):
        def newfunc(*args,**kwds):
            old_settings = {}
            for (key,value) in new_settings.iteritems():
                old_settings[key] = getattr(settings,key)
                setattr(settings,key,value)
            try:
                return func(*args,**kwds)
            finally:
                for (key,value) in old_settings.iteritems():
                    setattr(settings,key,value)
        return newfunc
    return with_settings_dec


class TestParanoidSessions(TestCase):
    """Testcases for paranoidsessions module."""

    urls = "paranoidsessions.tests"

    def setUp(self):
        self.orig_clear_session = settings.PSESSION_CLEAR_SESSION_FUNCTION
        settings.PSESSION_CLEAR_SESSION_FUNCTION = lambda r: r.session.flush()

    def tearDown(self):
        settings.PSESSION_CLEAR_SESSION_FUNCTION = self.orig_clear_session

    @with_settings(PSESSION_SECURE_COOKIE_NAME="secureid")
    def test_secure_key_handling(self):
        #  No secure key given as it's not a secure request
        r = self.client.get("/")
        session1 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertFalse("secureid" in self.client.cookies)
        #  Secure key generated and sent in secure cookie
        r = self.client.get("/",**{"wsgi.url_scheme":"https"})
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        key1 = self.client.cookies["secureid"].value
        self.assertEquals(session1,session2)
        self.assertTrue(self.client.cookies["secureid"]["secure"])
        #  Additional request accepted, key not sent again
        r = self.client.get("/",**{"wsgi.url_scheme":"https"})
        session3 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertEquals(session1,session3)
        self.assertFalse("secureid" in r.cookies)
        #  Insecure requests are accepted with an invalid secure key
        self.client.cookies["secureid"] = "invalid"
        r = self.client.get("/")
        session4 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertEquals(session1,session4)
        self.assertFalse("secureid" in r.cookies)
        #  And with no secure key at all
        del self.client.cookies["secureid"]
        r = self.client.get("/")
        session4 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertEquals(session1,session4)
        self.assertFalse("secureid" in r.cookies)
        #  But secure requests are rejected with an invalid key
        self.client.cookies["secureid"] = "invalid"
        r = self.client.get("/",**{"wsgi.url_scheme":"https"})
        session5 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        key2 = self.client.cookies["secureid"].value
        self.assertNotEquals(session1,session5)
        self.assertNotEquals(key1,key2)
        #  Rejected session still works OK
        r = self.client.get("/",**{"wsgi.url_scheme":"https"})
        session6 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertEquals(session5,session6)
        #  But is rejected again when secureid is not provided
        del self.client.cookies["secureid"]
        r = self.client.get("/",**{"wsgi.url_scheme":"https"})
        session7 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertNotEquals(session5,session7)
        #  Check that initiating a session over https works as expected
        del self.client.cookies[settings.SESSION_COOKIE_NAME]
        r = self.client.get("/",**{"wsgi.url_scheme":"https"})
        session8 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertNotEquals(session8,session7)
        r = self.client.get("/",**{"wsgi.url_scheme":"https"})
        session9 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertEquals(session8,session9)
        

    @with_settings(PSESSION_NONCE_TIMEOUT=0)
    def test_nonce_generation(self):
        r = self.client.get("/")
        session1 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        nonce1 = self.client.cookies[settings.PSESSION_COOKIE_NAME].value
        r = self.client.get("/")
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        nonce2 = self.client.cookies[settings.PSESSION_COOKIE_NAME].value
        self.assertEqual(session1,session2)
        self.assertNotEqual(nonce1,nonce2)

    @with_settings(PSESSION_NONCE_TIMEOUT=0.2)
    def test_nonce_timeout(self):
        r = self.client.get("/")
        nonce1 = self.client.cookies[settings.PSESSION_COOKIE_NAME].value
        r = self.client.get("/")
        nonce2 = self.client.cookies[settings.PSESSION_COOKIE_NAME].value
        self.assertEqual(nonce1,nonce2)
        time.sleep(0.2)
        r = self.client.get("/")
        nonce2 = self.client.cookies[settings.PSESSION_COOKIE_NAME].value
        self.assertNotEqual(nonce1,nonce2)

    @with_settings(PSESSION_NONCE_TIMEOUT=0)
    def test_invalid_nonce(self):
        r = self.client.get("/")
        session1 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        timestamp1 = self.client.session["timestamp"]
        r = self.client.get("/")
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        timestamp2 = self.client.session["timestamp"]
        self.assertEqual(session1,session2)
        self.assertEqual(timestamp1,timestamp2)
        self.client.cookies[settings.PSESSION_COOKIE_NAME].value = "invalid"
        r = self.client.get("/")
        session3 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        timestamp3 = self.client.session["timestamp"]
        self.assertNotEqual(session1,session3)
        self.assertNotEqual(timestamp1,timestamp3)

    @with_settings(PSESSION_NONCE_WINDOW=2,PSESSION_NONCE_TIMEOUT=0)
    def test_nonce_window(self):
        r = self.client.get("/")
        nonce1 = self.client.cookies[settings.PSESSION_COOKIE_NAME].value
        session1 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        r = self.client.get("/")
        nonce2 = self.client.cookies[settings.PSESSION_COOKIE_NAME].value
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertEqual(session1,session2)
        #  Use the old nonce, it should still work
        self.client.cookies[settings.PSESSION_COOKIE_NAME].value = nonce1
        r = self.client.get("/")
        session3 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertEqual(session1,session3)
        #  Use the old nonce again, it should still work
        self.client.cookies[settings.PSESSION_COOKIE_NAME].value = nonce1
        r = self.client.get("/")
        session3 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertEqual(session1,session3)
        #  But using it a third time should fail
        self.client.cookies[settings.PSESSION_COOKIE_NAME].value = nonce1
        r = self.client.get("/")
        session4 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertNotEqual(session1,session4)

    @with_settings(PSESSION_NONCE_WINDOW=3,PSESSION_NONCE_TIMEOUT=0,PSESSION_NONCE_WINDOW_TIMEOUT=0.2)
    def test_nonce_window_timeout(self):
        r = self.client.get("/")
        nonce1 = self.client.cookies[settings.PSESSION_COOKIE_NAME].value
        session1 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        r = self.client.get("/")
        nonce2 = self.client.cookies[settings.PSESSION_COOKIE_NAME].value
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertEqual(session1,session2)
        #  Use the old nonce, it should still work
        self.client.cookies[settings.PSESSION_COOKIE_NAME].value = nonce1
        r = self.client.get("/")
        session3 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertEqual(session1,session3)
        #  Wait for timeout, then it should fail
        time.sleep(0.2)
        self.client.cookies[settings.PSESSION_COOKIE_NAME].value = nonce1
        r = self.client.get("/")
        session4 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertNotEqual(session1,session4)

    @with_settings(PSESSION_KEY_TIMEOUT=0.2)
    def test_key_timeout(self):
        r = self.client.get("/")
        session1 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        timestamp1 = self.client.session["timestamp"]
        r = self.client.get("/")
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        timestamp2 = self.client.session["timestamp"]
        self.assertEqual(session1,session2)
        self.assertEqual(timestamp1,timestamp2)
        time.sleep(0.2)
        r = self.client.get("/")
        session3 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        timestamp3 = self.client.session["timestamp"]
        self.assertNotEqual(session1,session3)
        self.assertEqual(timestamp1,timestamp3)

    @with_settings(PSESSION_CHECK_HEADERS=["REMOTE_ADDR","HTTP_USER_AGENT"])
    def test_check_headers(self):
        #  Test a missing header suddenly appearing
        r = self.client.get("/")
        session1 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        r = self.client.get("/",HTTP_USER_AGENT="attacker")
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertNotEqual(session1,session2)
        #  Test a header changing its value
        r = self.client.get("/",HTTP_USER_AGENT="goodguy")
        session1 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        r = self.client.get("/",HTTP_USER_AGENT="badguy")
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertNotEqual(session1,session2)
        #  Test a header disappearing
        r = self.client.get("/",HTTP_USER_AGENT="goodguy")
        session1 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        r = self.client.get("/")
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertNotEqual(session1,session2)
        #  Test a change and a disappear
        r = self.client.get("/",HTTP_USER_AGENT="goodguy",REMOTE_ADDR="xxx")
        session1 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        r = self.client.get("/",REMOTE_ADDR="yyy")
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertNotEqual(session1,session2)
        #  Test everything staying the same
        r = self.client.get("/",HTTP_USER_AGENT="goodguy",REMOTE_ADDR="xxx")
        session1 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        r = self.client.get("/",HTTP_USER_AGENT="goodguy",REMOTE_ADDR="xxx")
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertEqual(session1,session2)
        r = self.client.get("/",HTTP_USER_AGENT="goodguy",REMOTE_ADDR="xxx")
        session3 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        self.assertEqual(session1,session3)

    @with_settings(PSESSION_REQUEST_FILTER_FUNCTION=request_filter,PSESSION_CHECK_HEADERS=["HTTP_USER_AGENT"])
    def test_request_filter(self):
        r = self.client.get("/")
        session1 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        nonce1 = self.client.cookies[settings.PSESSION_COOKIE_NAME].value
        r = self.client.get("/safeview",HTTP_USER_AGENT="attacker")
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        nonce2 = self.client.cookies[settings.PSESSION_COOKIE_NAME].value
        self.assertEqual(session1,session2)
        self.assertEqual(nonce1,nonce2)
        r = self.client.get("/",HTTP_USER_AGENT="attacker")
        session2 = self.client.cookies[settings.SESSION_COOKIE_NAME].value
        nonce2 = self.client.cookies[settings.PSESSION_COOKIE_NAME].value
        self.assertNotEqual(session1,session2)
        self.assertNotEqual(nonce1,nonce2)

