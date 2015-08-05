# -*- coding: utf-8 -*-
import os

import settings
from bottle import request, route
from logics import *
from bottle import jinja2_view as view
from admin.decorators import validate




@route('/admin/server_doc', method='GET')
@view('server_doc.html')
@validate
def server_doc():
    stuffs = sorted(os.listdir('logics'))
    global_vars = globals()
    docs = {}
    for stuff in stuffs:
        if stuff.endswith('.py') and stuff != '__init__.py':
            model_name = stuff.rsplit('.', 1)[0] 
            print "logic model for:", model_name
            model = global_vars[model_name] 
            docs[model_name] = this_docs = {}
            this_docs['title'] = getattr(model, '__doc__', '').decode('utf-8')
            this_docs['functions'] = get_api_doc(model)
    print docs
    return {'doc': docs}

def get_api_doc(model):
    api_docs = {}
    api_strs = [attr for attr in dir(model) if attr.startswith('api_')]
    for attr in api_strs:
        api_docs[attr] = getattr(model, attr).__doc__.decode('utf-8')
    return api_docs
    
    

if __name__ == '__main__':
    server_doc()
