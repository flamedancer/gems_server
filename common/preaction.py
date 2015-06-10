# -*- coding: utf-8 -*-

import sys, os
import datetime
import traceback
from libs.dbs import app 
from common.exceptions import *
from bottle import request
from models.user_base import UserBase


def prelogic(func):
    def wrap_func(*args):
        timestamp_validation()
        signature_validation()
        pier_clear()
        try:
            result = func(*args)
        except Error as e:
            result['error_code'] = e.error_code
            result['error_msg'] = e.error_msg
        except Exception as e:
            print_err()
            print e.msg
            
        result['user_info'] = modified_user_data()
        save_pier()
        return result
    return wrap_func


def timestamp_validation():
    pass


def signature_validation():
    uid = str(request.forms.get('uid', ''))
    print "signatur_uid", uid
    user = UserBase.create(uid)
    request.user = user


def pier_clear():
    app.pier.clear()


def save_pier():
    app.pier.save()


def modified_user_data():
    Umodified = request.user.user_modified
    print type(Umodified)
    modified_data = Umodified.modified
    if modified_data:
        Umodified.modified = {}
        Umodified.put()
    return modified_data


def print_err():
    sys.stderr.write('=='*30+os.linesep)
    sys.stderr.write('err time: '+str(datetime.datetime.now())+os.linesep)
    sys.stderr.write('--'*30+os.linesep)
    traceback.print_exc(file=sys.stderr)
    sys.stderr.write('=='*30+os.linesep)
