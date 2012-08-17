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
        app._validate_redirect_id('/srv/index.html')

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

    @n.raises(ValueError)
    def test_domain_name_space(self):
        "The domain name should not contain a space."
        app._validate_domain_name('Bagger 288')

    @n.raises(ValueError)
    def test_domain_name_empty(self):
        "The domain name should not be the empty string."
        app._validate_domain_name('')

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

class TestReadFilesystem:
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
        observed = app._current_froms(self.root, 'h92hsuostuhaou')
        expected = {
            'lorena.co.nz',
            'www.thomaslevine.org',
            'urchin.sh',
        }
        n.assert_set_equal(observed, expected)

    def test_current_froms2(self):
        self.load('no-redirects')
        observed = app._current_froms(self.root, 'foobar')
        expected = set()
        n.assert_set_equal(observed, expected)

    # os.path.getctime('../unittests.py')

    def test_parse_nginx_conf(self):
        self.load('basic')
        filename = os.path.join(self.root, 'etc', 'nginx', 'conf.d', '1-www.thomaslevine.org-89ouoneu')
        conf = open(filename).read()
        observed = app._parse_nginx_redirect(conf)
        expected = {
            'from': 'www.thomaslevine.org',
            'status_code': 303,
            'to': 'http://www.thomaslevine.com',
            'email': 'occurrence@example.com',
        }
        n.assert_dict_equal(observed, expected)

class TestWriteNginxConfig:
    "The Nginx config should be written in a few particular ways."
    def test_add_http(self):
        '"http://" should be added to "to" if it\'s missing'
        params = {
            'from': 'foo',
            'status_code': 303,
            'to': 'bar',
            'email': '',
        }
        conf = app.nginx_conf(params)
        n.assert_in('http://bar$request_uri;', conf)

    def test_remove_http(self):
        '"http://" should be removed from "from" if it\'s in there'
        params = {
            'from': 'http://foo',
            'status_code': 303,
            'to': 'bar',
            'email': '',
        }
        conf = app.nginx_conf(params)
        n.assert_not_in('http://foo', conf)
        n.assert_in('foo', conf)

    def test_remove_https(self):
        '"https://" should be removed from "from" if it\'s in there'
        params = {
            'from': 'https://foo',
            'status_code': 303,
            'to': 'bar',
            'email': '',
        }
        conf = app.nginx_conf(params)
        n.assert_not_in('https://foo', conf)
        n.assert_in('foo', conf)

    def test_empty_email(self):
        'An empty email should still create a line'
        params = {
            'from': 'https://foo',
            'status_code': 303,
            'to': 'bar',
            'email': '',
        }
        conf = app.nginx_conf(params)
        n.assert_in('# email', conf)

    def test_full_email(self):
        'An email addresses should be followed by a semicolon.'
        params = {
            'from': 'https://foo',
            'status_code': 303,
            'to': 'bar',
            'email': 'baz@example.com',
        }
        conf = app.nginx_conf(params)
        n.assert_in('baz@example.com;', conf)

class TestRedirectMustExist:
    'This should return an HTTP error if the redirect doesn\'t exist.'
    def test_specified_file_does_not_exist(self):
        def fail_to_open(foo):
            open('/a/b/c/d', 'r')
 
        observed = app.redirect_must_exist(fail_to_open)('elephant')
        expected = { "error": "That redirect doesn't exist. Use PUT to create it." }
        n.assert_dict_equal(observed, expected)

    def test_other_file_does_not_exist(self):
        filename = os.path.join(app.NGINX_SITES, '1-foobar')
        open(filename, 'w').write('baz')
        def fail_to_open(foo):
            open('/a/b/c/d/e/f', 'r')
 
        with n.assert_raises(IOError):
            app.redirect_must_exist(fail_to_open)('foobar')

        # Clean up
        os.remove(filename)

    def test_specified_file_does_exist(self):
        open(os.path.join(app.NGINX_SITES, '1-chainsaw'), 'w').write('baz')
        def succeed_to_open(foo):
            open(os.path.join(app.NGINX_SITES, '1-chainsaw'), 'r')
            return {'yay': 'it works'}
 
        observed = app.redirect_must_exist(succeed_to_open)('chainsaw')
        expected = {'yay': 'it works'}
        n.assert_dict_equal(observed, expected)

result = nose.run()
shutil.rmtree(app.NGINX_SITES)
os.makedirs(app.NGINX_SITES)
exit(result)
