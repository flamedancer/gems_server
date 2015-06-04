from bottle import route, run
from logics.login import login

@route('/hello')
def hello1():
    return "Hello World!"


run(host='127.0.0.1', port=8081, debug=True)
