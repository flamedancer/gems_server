#-*- coding: utf -*-

import os
import glob
import time
import datetime
import random

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
    # 城市进贡
    prod_city_award(request.user)
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


def prod_city_award(ubase):
    """ 产出城市进贡 """
    td = datetime.datetime.today()
    ucities = ubase.user_cities
    last_datetime = datetime.datetime.fromtimestamp(ubase.last_login_time)
    # 每小时产出一次
    if str(last_datetime)[:13] == str(td)[:13]:
        return
    # 有未领取的进贡不产生新的进贡
    if ucities.city_award:
        return
    award = {}
    city_config = ubase._city_config
    # 每个征服了的城市都有进贡几率
    for city_id in ucities.cities:
        if not ucities.has_conquer_city(city_id):
            continue
        # 每一级都增加1%的进贡率 
        if random.random() > (0.01 * ucities.cities[city_id]['lv']):
            continue
        # 贡品类型
        award_type = city_config[city_id]['reward_type']
        # 城市声望越高，贡品的数量越多
        award_num = city_config[city_id]['reward_num'][ucities.cities[city_id]['reputation_lv']]
        award.setdefault(award_type, 0)
        award[award_type] += award_num
    ucities.set_city_award(award)
         

