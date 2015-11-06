#-*- coding: utf -*-

import os
import glob

from bottle import request, route
from common.preaction import prelogic

__all__ = [os.path.basename(
    f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py") if not f.startswith('__')]

from . import *

@route('/api/<category>/<method>', method='post')
@prelogic
def api(category='', method=''):
    if not category or not method:
        return ''
    model = globals().get(category)
    if not model:
        return ''
    func = getattr(model, 'api_' + method, None) 
    
    if not func:
        return ''
    task.check_task('_'.join([category, method]), request.api_data) 
    return func(**request.api_data)



