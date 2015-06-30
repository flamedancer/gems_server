# -*- coding: utf-8 -*-

import settings
from bottle import route, run, app, Bottle
from logics import *
from admin.views import *

@route('/hello')
def hello1():
    return "Hello World!"

app = Bottle()

run(host='192.168.1.36', reloader=False, port=8081, debug=settings.DEBUG)
