from bottle import route, run
from logics.login import login
from admin.config_view import config_view

@route('/hello')
def hello1():
    return "Hello World!"


run(host='127.0.0.1', port=8081, debug=True)
