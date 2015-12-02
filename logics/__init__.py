#-*- coding: utf -*-

import os
import glob
import time

from bottle import request, route
from common.preaction import prelogic
from common.tools import add_user_things

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
    # 自然回复体力
    recover_stamina()
    result = func(**request.api_data) 
    task.check_task_and_guideflag('_'.join([category, method]), request.api_data) 
    return result 



def recover_stamina():
    """ 恢复体力 并 更新下次回复体力时间
    """
    user = request.user
    now = time.time()
    if now < user.last_recover_stamina_time:
        return
    gap_min = user._common_config["stamina_recover_gap_min"]
    gap_cnt = int((now - user.last_recover_stamina_time) / (gap_min * 60)) + 1
    user.last_recover_stamina_time += gap_min * 60 * gap_cnt

    # 体力不能超过上限
    uproperty = user.user_property
    max_stamina = user._userlv_config[str(user.user_property.lv)]["stamina"]
    if uproperty.stamina >= max_stamina:
        return
    add_stamina = min(max_stamina - uproperty.stamina, gap_cnt)

    add_user_things(uproperty, "stamina", add_stamina, "recover_stamin_by_self")
