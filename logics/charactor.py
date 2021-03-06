#-*- coding: utf-8 -*-
""" 主角系统
"""

from bottle import request
from common import tools
from common import utils
from common.names import Names
from common.exceptions import *


def api_get_names():
    """api/charactor/get_names
    获取随机名字
    Args:
        names(list->str): 随机名字组
    """
    names = [utils.random_name() for i in range(0,7)]
    return {'names':names}


def check_name(name):
    """
    检查名字是否合法
    """
    if len(name.strip()) <= 0:
        raise LogicError('名字不能为空哦亲')
    if utils.is_sense_word(name):
        raise LogicError('名字含有敏感词汇哦亲')
    if Names.get(name):
        #rk_user调用 UserName.set_name, UserName的 pk 是 name, 若重复，报错
        raise LogicError('名字已被别人使用哦亲')


def api_init_charactor(name, picture):
    """api/charactor/init_charactor
    初始化玩家姓名，形象
    Args:
        name(str): 主角名字 
        picture(int): 选择的皮肤id
    """
    ubase = request.user
    tools.update_user_info(ubase, 'name', name, 'init_charactor')
    check_name(name)
    Names.set_name(ubase.uid, name)
    tools.update_user_info(ubase, 'picture', name, 'init_charactor')
    return {}
    
    

def api_rename(new_name):
    """ api/charactor/rename
    重命名
    
    Args:
        new_name(str): 新的主角名字
    """
    ubase = request.user
    check_name(name)
    tools.update_user_info(ubase, 'name', new_name, 'api_rename')
    return {}


def api_allot_nature(nature_type, allot_num=1):
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
        allot_num(str): 给该元素分配点数，缺省为1 
    """
    ubase = request.user
    need_remain_num = allot_num 
    tools.del_user_things(ubase, 'nature_remain', need_remain_num, 'allot_nature') 
    tools.add_user_things(ubase, "nature_" + nature_type, allot_num, 'allot_nature') 
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
    # 消耗元素重置道具
    tools.del_user_things(ubase, 'elementrefresh_item', 1, 'reallot_nature')
    uproperty = ubase.user_property
    nature_types = ["0", "1", "2", "3", "4", "5", "remain"]
    has_nature_num = sum([getattr(uproperty, "nature_" + nature_type, 0) for nature_type in nature_types])
    consume_nature_num = sum(natures.values())
    remain_nature = has_nature_num - consume_nature_num
    if remain_nature < 0:
        raise LogicError("Not enough natures!") 
    for nature_type, num in natures.items():
        if nature_type not in nature_types[:-1]:
            raise LogicError("Unkonew nature type!")
        tools.update_user_info(uproperty, "nature_" + nature_type, num, "reallot_nature") 
    tools.update_user_info(uproperty, "nature_remain", remain_nature, "reallot_nature") 
    return {}


def api_set_newbie_step(step):
    """ api/charactor/set_newbie_step
    设置玩家已过新手引导步数
    Args:
        step(int): 新手引导步数id
    """

    ubase = request.user
    ubase.newbie_step = step
    if step >= ubase._common_config.get('newbie_step', 0):
        ubase.is_newbie = False
    return {}
        

def api_turn_guide_flags(flag):
    """ api/charactor/turn_guide_flags
    完成指定系统引导
    Args:
        flag(str): 系统引导名 
            arena  竞技场
            pvp    天梯
            invade 城战
            charactor 主角系统
            gacha   抽卡
            cards   图鉴系统
            task    任务
            challenge 挑战模式
            team_index_normal 获得新的军旗并进入除竞技场与城战防守外任意军旗界面-1默认转态
            team_index_special        玩家第一次获得新的军旗并进入竞技场军旗界面
    """
    umodified = request.user.user_modified
    umodified.del_guide_flags(flag)
    return {}

