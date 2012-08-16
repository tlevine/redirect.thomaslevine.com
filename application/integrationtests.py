#!/usr/bin/env python2
import random
import datetime
from time import sleep
import json

import requests
from nose.tools import assert_equal, assert_dict_equal, assert_in, assert_not_in

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

    def test_basic_post(self):
        "A basic post should work and return what it did."
        params = {
            'from': 'example.com',
            'to': 'www.example.com',
        }
        r = requests.post(API_URL, params)
        assert_equal(r.status_code, 201)

        pseudo_observed_data = json.loads(r.text)
        pseudo_observed_data['created'] = datetime.datetime.strptime(
            pseudo_observed_data['created'][:10],
            '%Y-%m-%d'
        ).date()
        pseudo_expected_data = {
            "from": "thomaslevine.com",
            "to": "www.thomaslevine.com",
            "email": "occurrence@example.com",
            "created": datetime.date(2012, 08, 03),
        }
        assert_dict_equal(pseudo_observed_data, pseudo_expected_data)

    def test_post_then_get(self):
        'A basic post should return something, and then getting again a few seconds later should return the same something.'
 
        params = {
            'from': 'example.com',
            'to': 'www.example.com',
        }

        # Create the thingy.
        post = requests.post(API_URL, params)
        post_data = json.loads(post.text)

        sleep(5)

        # Query the thingy.
        get = requests.post(API_URL, params)
        get_data = json.loads(post.text)

        assert_dict_equal(post_data, get_data)

    def test_post_twice(self):
        'If I post twice, the first should be 201 and the second should be 200'
        params = {
            'from': 'example.com',
            'to': 'www.example.com',
        }

        creation = requests.post(API_URL, params)
        sleep(5)
        modification = requests.post(API_URL, params)
        assert_equal(creation.status_code, 201)
        assert_equal(modification.status_code, 200)

    def test_put_post(self):

    def test_delete(self):
        'I should be able to create a redirect and then delete it.'

    def test_post_missing_fields(self):
        "An invalid post should say what fields are missing."
        r = requests.post(API_URL, {'to': 'example.com'})
        assert_equal(r.status_code, 400)

        data = json.loads(r.text)
        assert_in('error', data)
        assert_in('"from"', data)
        assert_not_in('"to"', data)
 

nose.main()
