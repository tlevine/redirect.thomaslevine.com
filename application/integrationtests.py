#!/usr/bin/env python2
import sys
import random
import datetime
import string
from time import sleep
import json

import requests
import nose
import nose.tools as n

#if len(sys.argv) == 1:
#    API_DOMAIN=u'http://redirect.thomaslevine.com'
#else:
#    API_DOMAIN=sys.argv[1]

API_DOMAIN='http://localhost:9001'

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
        _no_id(self, requests.put)

    def test_post(self):
        _no_id(self, requests.post)

    def test_get(self):
        _no_id(self, requests.get)

    def test_delete(self):
        _no_id(self, requests.delete)

class Base:
    simple_params = {
        'from': 'example.com',
        'to': 'www.example.com',
    }
    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        # Make a temporary redirect
        self.url = api_url()
 
    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        # Remove the redirect.
        requests.delete(self.url)

class TestAPI(Base):
    def test_content_type(self):
        "The content type should be JSON."
        r = requests.get(self.url)
        n.assert_equal(r.headers['content-type'], 'application/json; charset=utf-8')

    def test_basic_put(self):
        "A basic put should work."
        r1 = requests.put(self.url, self.simple_params)
        n.assert_equal(r1.status_code, 204)
        n.assert_equal(r1.text, '')

        r2 = requests.get(self.url)
        n.assert_equal(r1.status_code, 200)
        n.assert_dict_contains_subset(self.simple_params, json.loads(r1.text))

    def test_advanced_put(self):
        "A put with email and status_code should work."
        params = {
            'from': 'example.com',
            'to': 'www.example.com',
            'status_code': 303,
            'email': 'occurrence@example.com',
        }
        r1 = requests.put(self.url, params)
        n.assert_equal(r1.status_code, 204)
        n.assert_equal(r1.text, '')

        r2 = requests.get(self.url)
        n.assert_equal(r1.status_code, 200)
        n.assert_dict_contains_subset(params, json.loads(r1.text))

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
        params1 = {
            'from': 'example.com',
            'to': 'www.example.com',
            'status_code': 301,
        }
        params2 = {
            'from': 'example.com',
            'to': 'www.example.com',
            'status_code': 303,
        }

        requests.put(self.url, params1)
        data1 = json.loads(requests.get(self.url).text)
        sleep(1)
        requests.put(self.url, params2)
        data2 = json.loads(requests.get(self.url).text)

        n.assert_not_equal(data1, data2)
        data1['status_code'] = 303
        n.assert_equal(data1, data2)

    def test_put_post(self):
        'If I create and then update, the response should change.'
        params1 = {
            'from': 'example.com',
            'to': 'www.example.com',
            'status_code': 301,
        }
        params2 = {
            'status_code': 303,
        }

        requests.put(self.url, params1)
        data1 = json.loads(requests.get(self.url).text)
        sleep(1)
        requests.post(self.url, params2)
        data2 = json.loads(requests.get(self.url).text)

        n.assert_not_equal(data1, data2)
        data1['status_code'] = 303
        n.assert_equal(data1, data2)

    def test_delete(self):
        'I should be able to create a redirect and then delete it.'
        requests.put(self.url, self.simple_params)
        r = requests.delete(self.url)
        n.assert_equal(r.status_code, 204)
        n.assert_equal(r.text, '')

    def test_delete_nonexistant(self):
        'I should receive an error if the redirect doesn\'t exist.'
        requests.put(self.url, self.simple_params)
        r = requests.delete(self.url, self.simple_params)
        n.assert_equal(r.status_code, 404)
        n.assert_equal(r.text, '')

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
        n.assert_in('"from"', data)
        n.assert_not_in('"to"', data)

class TestAuthorization:
    'If I try to make a redirect with a from that already exists, I should get an error.'
    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        # Make a temporary redirect
        self.url_old = api_url()
        self.url = api_url()

        params = {
            'from': 'example.com',
            'to': 'www.example.com',
            'status_code': 301,
        }
        requests.put(self.url_old, params)
        sleep(1)
 
    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        # Remove the redirect.
        requests.delete(self.url_old)
        requests.delete(self.url)

    def _check_sameness_error(self, r):
        data = json.loads(requests.get(r.url).text)

        n.assert_equal(r.status_code, 401)
        n.assert_in('error', data)
        n.assert_equal(data['error'], "There's already a different redirect from example.com. If you think there shouldn't be, contact Tom.")
 
    def test_post(self):
        "If you post the update"

        # Create my redirect
        params1 = {
            'from': 'thomaslevine.com',
            'to': 'www.thomaslevine.com',
            'status_code': 303,
        }
        requests.put(self.url, params1)

        # Change it.
        params2 = {
            'from': 'example.com',
        }
        r = requests.post(self.url, params2)
        _check_sameness_error(r)
 
    def test_put(self):
        "If you put the update"
        params = {
            'from': 'example.com',
            'to': 'www.thomaslevine.com',
            'status_code': 303,
        }

        r = requests.put(self.url, params)
        _check_sameness_error(r)

def test_splash_page():
    "There should be a splash page at /"
    html = requests.get(API_DOMAIN + '/v1/').text
    assert_in('https://github.com/tlevine/redirect.thomaslevine.com', html)

if __name__ == '__main__':
    nose.main()
