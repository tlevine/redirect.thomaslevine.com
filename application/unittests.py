#!/usr/bin/env python2
import datetime
import json

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
    def test_response_code(self):
        "The response code must be one of 301 or 303 and an integer."
        app._validate_response_code(302)
        app._validate_response_code('303')

nose.main()
