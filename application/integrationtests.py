#!/usr/bin/env python2
import sys
import random
import datetime
import string
from time import sleep
from copy import copy
import json
import uuid

import requests
import nose
import nose.tools as n

from app import PORT
API_DOMAIN='http://localhost:%d' % PORT

def api_url(size=32, chars=string.letters + string.digits):
    '''
    Return a redirect endpoint with a random identifier.
    The randomness code is based on
    http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
    '''
    randomthing=''.join(random.choice(chars) for x in range(size))
    return API_DOMAIN + '/v1/' + randomthing

class TestNoId:
    "Requests to /v1 should report that a redirect name is needed."
    url = API_DOMAIN + '/v1/'

    def _no_id(self, method):
        r = method(self.url)
        observed_data = json.loads(r.text)
        expected_data = {
            'error': 'You must specify a redirect name after /v1/'
        }

        n.assert_equal(r.status_code, 400)
        n.assert_equal(observed_data, expected_data)

    def test_put(self):
        self._no_id(requests.put)

    def test_post(self):
        self._no_id(requests.post)

    def test_get(self):
        self._no_id(requests.get)

    def test_delete(self):
        self._no_id(requests.delete)

class Base:
    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        # Make a temporary redirect
        self.url = api_url()
        requests.delete(self.url)

        # Temporary from value
        self.uuid = unicode(uuid.uuid1()) 

        # A few versions of the addresses
        self.simple_params = {
            'from': self.uuid + 'example.com',
            'to': 'www.example.com',
        }
        self.http_params = {
            'from': 'http://' + self.uuid + 'example.com',
            'to': 'http://www.example.com',
        }
 
    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        # Remove the redirect.
        requests.delete(self.url)

class TestAPI(Base):
    def test_content_type(self):
        "The content type should be JSON."
        r = requests.get(self.url)
        n.assert_equal(r.headers['Content-Type'].decode('utf-8'), u'application/json')

    def test_basic_put(self):
        "A basic put should work."
        r1 = requests.put(self.url, self.simple_params)
        n.assert_equal(r1.status_code, 204)
        n.assert_equal(r1.content, '')

        r2 = requests.get(self.url)
        n.assert_equal(r2.status_code, 200)
        n.assert_dict_contains_subset(self.http_params, json.loads(r2.text))

    def test_advanced_put(self):
        "A put with email and status_code should work."
        extra = {
            'status_code': 303,
            'email': 'occurrence@example.com',
        }
        self.simple_params.update(extra)
        self.http_params.update(extra)

        r1 = requests.put(self.url, self.simple_params)
        n.assert_equal(r1.status_code, 204)
        n.assert_equal(r1.content, '')

        r2 = requests.get(self.url)
        n.assert_equal(r2.status_code, 200)

        n.assert_dict_equal(json.loads(r2.text), self.http_params)

#   def test_creation_date(self):
#       "If I create a record and then read it, it should have a creation date."

#       # Create
#       requests.put(self.url, self.simple_params)

#       # Read
#       r = requests.get(self.url)
#       pseudo_observed_data['created'] = datetime.datetime.strptime(
#           pseudo_observed_data['created'][:10],
#           '%Y-%m-%d'
#       ).date()
#       pseudo_expected_data = {
#           "from": "thomaslevine.com",
#           "to": "www.thomaslevine.com",
#           "created": datetime.date(2012, 8, 3),
#       }
#       n.assert_dict_equal(pseudo_observed_data, pseudo_expected_data)

    def test_put_put(self):
        'If I make different puts, the response should change.'
        params1 = self.simple_params
        params2 = copy(self.simple_params)
        params2['status_code'] = 301

        requests.put(self.url, params1)
        data1 = json.loads(requests.get(self.url).text)
        sleep(1)
        requests.put(self.url, params2)
        data2 = json.loads(requests.get(self.url).text)

        n.assert_equal(data1['status_code'], 303)
        n.assert_equal(data1['status_code'], 303)
        del(data1['status_code'])
        del(data2['status_code'])
        n.assert_equal(data1, data2)

    def test_put_post(self):
        'If I create and then update, the response should change.'
        params_update = {
            'status_code': 301,
        }

        requests.put(self.url, self.simple_params)
        data1 = json.loads(requests.get(self.url).text)
        n.assert_equal(data1['status_code'], 303)
        sleep(1)

        requests.post(self.url, params_update)
        data2 = json.loads(requests.get(self.url).text)
        n.assert_equal(data2['status_code'], 301)

        del(data1['status_code'])
        del(data2['status_code'])
        n.assert_equal(data1, data2)

    def test_delete(self):
        'I should be able to create a redirect and then delete it.'
        requests.put(self.url, self.simple_params)
        r = requests.delete(self.url)
        n.assert_equal(r.status_code, 204)
        n.assert_equal(r.content, '')

    def test_delete_nonexistant(self):
        'I should receive an error if the redirect doesn\'t exist.'
        r = requests.delete(self.url)
        n.assert_equal(r.status_code, 404)
        observed = json.loads(r.text)
        expected = { "error": "That redirect doesn't exist. Use PUT to create it." }
        n.assert_dict_equal(observed, expected)

    def test_post_nonexistant(self):
        'I should receive an error if the redirect doesn\'t exist.'
        r = requests.post(self.url, self.simple_params)
        n.assert_equal(r.status_code, 404)

        observed = json.loads(r.text)
        expected = { "error": "That redirect doesn't exist. Use PUT to create it." }
        n.assert_dict_equal(observed, expected)

    def test_get_nonexistant(self):
        'I should receive an error if the redirect doesn\'t exist.'
        r = requests.get(self.url)
        n.assert_equal(r.status_code, 404)

        observed = json.loads(r.text)
        expected = { "error": "That redirect doesn't exist. Use PUT to create it." }
        n.assert_dict_equal(observed, expected)

    def test_put_missing_fields(self):
        "An invalid put should say what fields are missing."
        r = requests.put(self.url, {'to': 'example.com'})
        n.assert_equal(r.status_code, 400)

        data = json.loads(r.text)
        n.assert_in('error', data)
        n.assert_in('"from"', data['error'])
        n.assert_not_in('"to"', data['error'])

class TestAuthorization:
    'If I try to make a redirect with a from that already exists, I should get an error.'
    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        # Make a temporary redirect
        self.url_old = api_url()
        self.url = api_url()

        self.from_address = unicode(uuid.uuid1()) + 'TEST'

        params = {
            'from': self.from_address,
            'to': 'www.example.com',
            'status_code': 301,
        }
        r = requests.put(self.url_old, params)
        sleep(1)
 
    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        # Remove the redirect.
        requests.delete(self.url_old)
        requests.delete(self.url)

 
    def test_post(self):
        "If you post the update"

        # Create my redirect
        params1 = {
            'from': unicode(uuid.uuid1()),
            'to': 'www.thomaslevine.com',
            'status_code': 303,
        }

        requests.put(self.url, params1)
        sleep(1)

        # Change it.
        params2 = {
            'from': self.from_address,
        }
        r = requests.post(self.url, params2)
        self._check_sameness_error(r)
 
    def test_put(self):
        "If you put the update"
        params = {
            'from': self.from_address,
            'to': 'www.thomaslevine.com',
            'status_code': 303,
        }

        r = requests.put(self.url, params)
        self._check_sameness_error(r)

    def _check_sameness_error(self, r):
        data = json.loads(r.text)
        n.assert_equal(r.status_code, 403)
        n.assert_in('error', data)
        n.assert_regexp_matches(data['error'], r"There's already a different redirect from [0-9A-Za-z-]+TEST. If you think there shouldn't be, contact Tom.")

def test_splash_page():
    "There should be a splash page at /"
    r = requests.get(API_DOMAIN, allow_redirects=False)
    n.assert_equal(r.headers['Location'], 'https://github.com/tlevine/redirect.thomaslevine.com')
    n.assert_equal(r.status_code, 303)

if __name__ == '__main__':
    nose.main()
