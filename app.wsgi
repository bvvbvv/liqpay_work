#!/usr/local/bin/pay_app/bin/python3
####!/usr/bin/python3
import sys
import os

sys.path.insert(0,"/var/www/pay.sns.net.ua/public_html")
#sys.path.insert(0, os.path.dirname(__file__))
'''
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    return [b"<h1>Hello from Python via mod_wsgi!</h1>"]
'''
print("#### 111")
from app import app as application
print("#### 222")
