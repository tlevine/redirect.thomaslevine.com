#!/usr/bin/env python2
import random
import requests

from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises

import app

API_DOMAIN=u'http://redirect.thomaslevine.com'
def api_url(size=32, chars=string.letters + string.digits):
    '''
    Return a redirect endpoint with a random identifier.
    The randomness code is based on
    http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
    '''
    randomthing=''.join(random.choice(chars) for x in range(size))
    return API_DOMAIN + '/v1/redirects/' + randomthing

class TestAPI:
    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        # Make a temporary redirect
        self.url = api_url()
 
    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        # Remove the redirect.
        requests.delete(api_url)

    def test_post_missing_fields(self):
        "An invalid post should say what fields are missing."
        r = requests.post(API_URL, {'to': 'example.com'})
        assert_equal(r.status_code, 400)

        data = json.loads(r.content)
        assert_in('error', data)
        assert_in('"from"', data)
        assert_not_in('"to"', data)
 
    def test_return_true(self):
        a = A()
        assert_equal(a.return_true(), True)
        assert_not_equal(a.return_true(), False)
 
    def test_raise_exc(self):
        a = A()
 
        assert_raises(KeyError, a.raise_exc, "A value")
 
    @raises(KeyError)
    def test_raise_exc_with_decorator(self):
        a = A()
        a.raise_exc("A message")

nose.main()
