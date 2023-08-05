#!/usr/bin/python

"""very simple example CGI script that displays all env variables"""

import templess
import os

import cgitb
cgitb.enable()

ct = templess.cgitemplate('templates/cgitest.html')
ct.render({
    'envvars': [{'key': k, 'value': v} for (k, v) in os.environ.items()],
})

