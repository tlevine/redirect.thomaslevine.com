#!/usr/bin/env python2
import random
import datetime
from time import sleep
import json

import requests
import nose.tools as n

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

    def test_basic_put(self):
        "A basic put should work."
        params = {
            'from': 'example.com',
            'to': 'www.example.com',
        }
        r1 = requests.put(self.url, params)
        n.assert_equal(r1.status_code, 204)
        n.assert_equal(r1.text, '')

        r2 = requests.get(self.url)
        n.assert_equal(r1.status_code, 200)
        n.assert_dict_contains_subset(params, json.loads(r1.text))

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

    def test_creation_date(self):
        "If I create a record and then read it, it should have a creation date."

        # Create
        params = {
            'from': 'example.com',
            'to': 'www.example.com',
        }
        requests.put(self.url, params)

        # Read
        r = requests.get(self.url)
        pseudo_observed_data['created'] = datetime.datetime.strptime(
            pseudo_observed_data['created'][:10],
            '%Y-%m-%d'
        ).date()
        pseudo_expected_data = {
            "from": "thomaslevine.com",
            "to": "www.thomaslevine.com",
            "created": datetime.date(2012, 08, 03),
        }
        n.assert_dict_equal(pseudo_observed_data, pseudo_expected_data)

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

        requests.put(self.url, params)
        data1 = json.loads(requests.get(self.url).text)
        sleep(5)
        requests.put(self.url, params)
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

        requests.put(self.url, params)
        data1 = json.loads(requests.get(self.url).text)
        sleep(5)
        requests.post(self.url, params)
        data2 = json.loads(requests.get(self.url).text)

        n.assert_not_equal(data1, data2)
        data1['status_code'] = 303
        n.assert_equal(data1, data2)

    def test_delete(self):
        'I should be able to create a redirect and then delete it.'

    def test_nonexistant(self):
        'I should receive an error if the redirect doesn\'t exist.'
        r = request.get(self.url)
        n.assert_equal(r.status_code, 404)

        observed = json.loads(r.text)
        expected = { "error": "That redirect doesn't exist. But feel free to create it." }
        n.assert_dict_equal(observed, expected)

    def test_put_missing_fields(self):
        "An invalid put should say what fields are missing."
        r = requests.put(self.url, {'to': 'example.com'})
        n.assert_equal(r.status_code, 400)

        data = json.loads(r.text)
        n.assert_in('error', data)
        n.assert_in('"from"', data)
        n.assert_not_in('"to"', data)
 

nose.main()