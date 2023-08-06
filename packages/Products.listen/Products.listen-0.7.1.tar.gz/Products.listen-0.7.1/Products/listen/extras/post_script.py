#!/usr/bin/env python
"""
script to post to listen from the command line
"""

# global variable
URL = 'http://localhost:8080/plone/send_listen_mail'

import sys
import urllib
import urllib2

data = sys.stdin.read()
quoted_data = urllib.quote(data)
quoted_data = 'Mail=' + quoted_data

urllib2.urlopen(URL, data=quoted_data).read()
