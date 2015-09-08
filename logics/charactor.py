#-*- coding: utf-8 -*-
""" 主角系统
"""

from bottle import request
from common.tools import *
from common.exceptions import *

def api_rename(new_name):
    """ api/charactor/rename
    重命名
    
    Args:
        new_name(str): 新的玩家名字
    """
    ubase = request.user
    update_user_info(ubase, 'name', new_name, 'api_rename')
    return {}


def api_allot_nature(nature_type):
    """ api/charactor/allot_nature
    元素掌握度加点, 每次加一点
            蓝 "0"
            红 "1"
            绿 "2"
            褐 "3"
            黄 "4"
            紫 "5"

    Args:
        nature_type(str): 元素类型代号
    """
    ubase = request.user
    need_remain_num = 1
    tools.del_user_things(ubase, 'nature_remain', need_remain_num, 'allot_nature') 
    tools.add_user_things(ubase, "nature_" + nature_type, 1, 'allot_nature') 
    return {}


def api_reallot_nature(natures):
    """ api/charactor/reallot_nature

    Args:
        natures(dir): 元素类别-新重置的数量
         例如：
            "natures": {
                "0": 1,
                "1": 4,
                "3": 2,
                ....
          }
    """
    ubase = request.user
    uproperty = ubase.user_property
    nature_types = ["0", "1", "2", "3", "4", "5", "remain"]
    has_nature_num = sum([getattr(uproperty, "nature_" + nature_type, 0) for nature_type in nature_types])
    consume_nature_num = sum(natures.keys())
    remain_nature = has_nature_num - consume_nature_num
    if reamin_nature < 0:
        raise LogicError("Not enough natures!") 
    for nature_type, num in natures.items():
        if nature_type not in nature_types[:-1]:
            raise LogicError("Unkonew nature type!")
        tools.update_user_info(uproperty, "nature_" + nature_type, num, "reallot_nature") 
    tools.update_user_info(uproperty, "nature_remain", remain_nature, "reallot_nature") 
    return {}

