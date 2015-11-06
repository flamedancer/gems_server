# -*- coding: utf-8 -*-

import settings
from bottle import route, run, app, Bottle, debug, default_app, BaseRequest
from logics import api
from admin.views import *

# 提交的文件最大长度
BaseRequest.MEMFILE_MAX = 1024 * 1024
@route('/hello')
def hello1():
    return "Hello World!"


if __name__ == '__main__':
    run(host='192.168.1.43', reloader=False, port=8081, debug=settings.DEBUG)
else:
    debug(mode=settings.DEBUG)
    application = default_app()
