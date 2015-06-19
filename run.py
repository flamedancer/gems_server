from bottle import route, run, app, Bottle
from logics import *
from admin import *

@route('/hello')
def hello1():
    return "Hello World!"

app = Bottle()

run(host='192.168.1.43', reloader=False, port=8081, debug=True)
