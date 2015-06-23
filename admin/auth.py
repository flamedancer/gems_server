# -*- coding: utf-8 -*-

from bottle import route, request
from bottle import jinja2_view as view


@route('/admin/signin', method='GET')
@view('signin.html')
def login():
    return {}


@route('/admin/home', method='GET')
@route('/admin/', method='GET')
@view('frame.html')
def home():
    return {}
