#!/usr/bin/env python2
import datetime
import json
from tempfile import mktemp
import os
import shutil

import nose
import nose.tools as n

import app

class TestValidation:
    "Prevent injection attacks."

    @n.raises(ValueError)
    def test_identifier(self):
        "The request identifier should not contain spaces."
        app._validate_request_id('/srv/index.html')

    @n.raises(ValueError)
    def test_response_code_number(self):
        "The response code must be one of 301 or 303."
        app._validate_response_code('302')

    @n.raises(ValueError)
    def test_domain_name_semicolon(self):
        "The domain name should contain a semicolon."
        app._validate_domain_name('http://example.com;')

    @n.raises(ValueError)
    def test_domain_name_squiggle(self):
        "The domain name should contain a squiggle."
        app._validate_domain_name('http://example.com{')

    @n.raises(ValueError)
    def test_domain_name_squaggle(self):
        "The domain name should contain a squaggle."
        app._validate_domain_name('http://example.com}')

def test_add_http():
    '_add_http should add http:// if it isn\'t already there.'
    e = 'http://example.com/foo+bar'
    o1 = app._add_http('http://example.com/foo+bar')
    o2 = app._add_http('example.com/foo+bar')
    n.assert_equal(o1, e)
    n.assert_equal(o2, e)

def test_remove_http():
    '_remove_http should remove http:// if it is there.'
    e = 'example.com/foo+bar'
    o1 = app._remove_http('http://example.com/foo+bar')
    o2 = app._remove_http('example.com/foo+bar')
    n.assert_equal(o1, e)
    n.assert_equal(o2, e)

class TestFilesystem:
    'Information should be stored on the filesystem.'
    def teardown(self):
        try:
            shutil.rmtree(self.root)
        except OSError:
            pass

    def load(self, fixture_name):
        self.root = mktemp()
        fixture_dir = os.path.join('.', 'fixtures-nginx', fixture_name)
        shutil.copytree(fixture_dir, self.root)

    def test_current_froms1(self):
        self.load('several-redirects')
        observed = app._current_froms(self.root)
        expected = {
            'lorena.co.nz',
            'dumptruck.io',
            'www.thomaslevine.org',
            'urchin.sh',
        }
        n.assert_set_equal(observed, expected)

    def test_current_froms2(self):
        self.load('no-redirects')
        observed = app._current_froms(self.root)
        expected = set()
        n.assert_set_equal(observed, expected)

    # os.path.getctime('../unittests.py')

    def test_parse_nginx_conf(self):
        self.load('basic')
        filename = os.path.join(self.root, 'etc', 'nginx', 'conf.d', '1-www.thomaslevine.org-89ouoneu')
        conf = open(filename).read()

        print conf
        observed = app._parse_nginx_redirect(conf)
        expected = {
            'from': 'www.thomaslevine.org',
            'status_code': 303,
            'to': 'http://www.thomaslevine.com',
            'email': 'occurrence@example.com',
        }
        n.assert_dict_equal(observed, expected)

nose.main()
