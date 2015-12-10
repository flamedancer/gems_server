# -*- coding:utf-8 -*-
"""  任务系统
"""

from bottle import request
from common import tools
from common.exceptions import *
from libs.dbs import app


def default_complete_num(task_id):
    """
    第一次新任务时, 默认的完成度
    ID  系统    任务内容    备注        
    1.1 主角系统    玩家等级达到10级    一直存在        A
    1.2 主角系统    红色元素元素掌握度达到10    玩家到达一定等级开启        B0(暂无)
    2.1 城市系统    成功解锁2座城市 一直存在        C
    2.2 城市系统    成功征服1座城市 一直存在        D
    2.3 城市系统    拥有1座3级城池  一座城市征服后开启  暂无    E
    3.1 征服系统    顺利通过纳达拉城的第5战 一直存在        F00
    3.2 征服系统    顺利通过科洛西尔的第5战 科洛西尔开城后开启      F01
    3.3 征服系统    顺利通过尤克特拉希尔的第5战 尤克特拉希尔后开启      F02
    3.4 征服系统    顺利通过特兰西瓦尼亚的第5战 特兰西瓦尼亚后开启      F03
    3.5 征服系统    顺利通过云雾峰的第5战   云雾峰后开启        F04
    3.6 征服系统    顺利通过萨拉曼德的第5战 萨拉曼德后开启      F05
    4.1 竞技场  获得1场竞技场战斗的胜利 竞技场开启后开启        G
    4.2 竞技场  在竞技场中获得3胜奖励   竞技场开启后开启        H
    5.1 天梯    获得1场天梯战斗的胜利   天梯开启后开启      I
    5.2 天梯    在天梯赛中达到10段  天梯开启后开启      J
    6.1 城战    获得1次城战进攻胜利 城战开启后开启      K
    6.2 城战    获得1次城战防守胜利 城战开启后开启      L
    6.3 城战    一次城战中奖杯最高达到20个  城战开启后开启      M
    7.1 图鉴    卡牌收集数量达到10  一直存在    暂无    N
    """
    user = request.user
        
    if task_id.startswith('A'):
        return user.user_property.lv 
    elif task_id.startswith('C'):
        return user.user_cities.get_opened_city_num()
    elif task_id.startswith('D'):
        return user.user_cities.get_conquered_city_num()
    elif task_id.startswith('F'):
        ucities = user.user_cities
        city_id = str(int(task_id[1:]))
        return int(ucities.cur_conquer_stage(city_id)) - 1
    elif task_id.startswith('G'):
        return user.user_arena.win
    elif task_id.startswith('H'):
        return user.user_arena.win
    elif task_id.startswith('I'):
        return user.user_pvp.total_win
    elif task_id.startswith('J'):
        return user.user_pvp.grade
    elif task_id.startswith('K'):
        return user.user_invade.total_invade_win
    elif task_id.startswith('L'):
        return user.user_invade.total_defense_win
    elif task_id.startswith('M'):
        return user.user_invade.cup
        

api_task_map = {
    'city_open_city': ['C'],
    'dungeon_end': ['D', 'F'],
    'arena_end_fight': ['G', 'H'],
    'pvp_info': ['I', 'J'],
    'invade_end_invade': ['K', 'M'],
    'invade_end_defense': ['L'],
}


def set_value(utask, task_id, value):
    utask.set_now_value(task_id, value) 
    main_task_conf = utask._task_config['main_task']
    print "debug_task set value", task_id, value
    # pvp段位 15  比 10 弱(虽然15>10）
    if not task_id.startswith('J'):
        if main_task_conf[task_id]['value'][utask.main_task[task_id]['step']] <= value:
            utask.set_completed(task_id) 
            print "debug_task com", task_id
    else:
        if main_task_conf[task_id]['value'][utask.main_task[task_id]['step']] >= value:
            utask.set_completed(task_id) 


def check_task_and_guideflag(api_path, api_data):
    user = request.user 
    utask = user.user_task 
    umodified = user.user_modified
    modified_info = umodified.modified
    main_task_conf = utask._task_config['main_task']
    ucities = user.user_cities


    # 是否新的任务进度
    def check_value(task_type, task_id):
        # A系列判定 玩家等级
        if task_type == 'A':
            new_value = modified_info['lv']
        # C系列 开城数
        elif task_type == 'C':
            new_value = ucities.get_opened_city_num()
        # D系列 征服城数
        elif task_type == 'D':
            if api_data['dungeon_type'] != 'conquer':
                return
            new_value = ucities.get_conquered_city_num()
        # F系列 征服某关卡
        elif task_type == 'F':
            if api_data['dungeon_type'] != 'conquer':
                return
            city_id = api_data['city_id']
            if int(city_id) != int(task_id[1:]):
                return
            new_value = int(ucities.cur_conquer_stage(city_id)) - 1
        # G系列 竞技场胜场数
        elif task_type == 'G':
            if not api_data['win']:
                return
            new_value = utask.get_now_value(task_id) + 1
        # H系列 竞技场连胜数 
        elif task_type == 'H':
            if not api_data['win']:
                return
            new_value = max(utask.get_now_value(task_id), user.user_arena.win)
        # I系列 pvp胜数 
        elif task_type == 'I':
            new_value = user.user_pvp.total_win
        # J系列 pvp段 
        elif task_type == 'J':
            new_value = user.user_pvp.grade
        # K系列 城战侵略成功数 
        elif task_type == 'K':
            if not api_data['win']:
                return
            new_value = user.user_invade.total_invade_win
        # L系列 城战反击成功数 
        elif task_type == 'L':
            if not api_data['win']:
                return
            new_value = user.user_invade.total_defense_win
        # M系列 城战奖杯数 
        elif task_type == 'M':
            if not api_data['win']:
                return
            new_value = max(utask.get_now_value(task_id), user.user_invade.cup)
        set_value(utask, task_id, new_value)
 
    # 若升级：1 是否有新任务 2 是否完成升级任务
    print "debug_task modifiedinfo", modified_info
    
    guide_flags = user._userInit_config.get('guide_flags', {})
    if 'lv' in modified_info:
        lv = user.user_property.lv
        # 是否有新任务
        for task_id, info in main_task_conf.items():
            if 'open_lv' in info and info['open_lv'] == lv:
                utask.add_main_task(task_id)
                set_value(utask, task_id, default_complete_num(task_id))
        # 检查A系列
        for task_id in utask.main_task:
            if task_id.startswith('A'):
                check_value('A', task_id)

        # 系统引导flag   等级有关
        for guide_type in ['arena', 'pvp', 'invade']:
            if lv == guide_flags.get(guide_type):
                umodified.set_guide_flags(guide_type, 2)
        

    # # 若开城: 1新的城市征服任务
    # if api_path == 'city_open_city':
    #     city_id = api_data['city_id']
    #     task_str = "F{:0>2}".format(city_id) 
    #     if task_str in main_task_conf:
    #         utask.add_main_task(task_str)
   
    print "debug_task", api_path
    # 判断有没完成新的任务
    if api_path in api_task_map:
        for task_type in api_task_map[api_path]:
            for task_id in utask.main_task:
                if task_id.startswith(task_type):
                    check_value(task_type, task_id)

    # 系统引导flag 过关有关
    # 过完某关flag
    if api_path == 'dungeon_end':
        guide_conquer_type = ['charactor', 'gacha', 'cards', 'task']
        win = api_data['win']
        if win and api_data['dungeon_type'] == 'conquer':
            city_id = api_data['city_id']
            floor = str(int(ucities.cur_conquer_stage(city_id)) - 1)
            conquered_city_num = user.user_cities.get_conquered_city_num()
            # 挑战 征服完一个城
            if conquered_city_num == 1 and umodified.has_guide_flags('challenge'):
                umodified.set_guide_flags('challenge', 1)
            if city_id == '0':
                city_floor = '-'.join([city_id, floor])
                for guide_type in guide_conquer_type:
                    if guide_flags.get(guide_type) == city_floor and umodified.has_guide_flags(guide_type):
                        umodified.set_guide_flags(guide_type, 2)
            # 获得新的军旗 (征服除城'0' 以外城市 )
            if (conquered_city_num - 1 if ucities.has_conquer_city('0') else 0) == 1:
                if umodified.has_guide_flags('team_index_normal'):
                    umodified.set_guide_flags('team_index_normal', 1)
                if umodified.has_guide_flags('team_index_special'):
                    umodified.set_guide_flags('team_index_special', 1)
    

def api_info():
    """ api/task/info
    显示任务列表

    Retures:
        tasks(list->dict):
            task_id(str): 任务代号
            title(str): 任务标题
            desc(str): 描述
            show_type(int): 未完成时显示格式 
                            0显示进度和前往 
                            1显示前往和未完成 
                            2只显示进度
    
            current(int): 完成数
            total(int): 总任务数 
            award(dict): 任务奖励
            completed(bool): 是否可领取
        
    """
    utask = request.user.user_task
    main_task_conf = utask._task_config['main_task']
    def info(task_id):
        task_conf = main_task_conf[task_id]
        return_info = {
            'task_id': task_id,
            'title': task_conf['title'] % int(utask.main_task[task_id]['step']),
            'desc': task_conf['desc'],
            'show_type': task_conf['show_type'],
            'current': utask.main_task[task_id]['now_value'] if\
                 utask.main_task[task_id]['now_value'] is not None else\
                 default_complete_num(task_id),
            'total': task_conf['value'][utask.main_task[task_id]['step']],
            'award': task_conf['award'][utask.main_task[task_id]['step']],
            'completed': utask.main_task[task_id]['completed'],
        } 
        return return_info
    completed_tasks = []
    no_completed_tasks = []
    print "debug", utask.main_task
    for task_id in sorted(utask.main_task.keys()):
        if utask.main_task[task_id]['completed']:
            completed_tasks.append(info(task_id))
        else:
            no_completed_tasks.append(info(task_id))
    # 取消标记
    utask.turn_new_task(False)
        
    return {'tasks': completed_tasks + no_completed_tasks
    }


def api_get_award(task_id):
    """ api/task/get_award
    领取任务奖励
    Args:
        task_id(str): 任务代号
    """
    utask= request.user.user_task
    main_task_conf = utask._task_config['main_task']
    print "debug guochen", utask.has_task(task_id), task_id in main_task_conf
    if not utask.has_task(task_id) or task_id not in main_task_conf:
        return {}
    print "debug gucohen", utask.main_task[task_id]['completed']
    if not utask.main_task[task_id]['completed']:
        return {}
    now_step = utask.main_task[task_id]['step']
    award = main_task_conf[task_id]['award'][now_step]
    next_step = str(int(now_step) + 1)
    if next_step in main_task_conf[task_id]['value']:
        utask.set_completed(task_id, completed=False)
        utask.set_step(task_id, next_step)
        set_value(utask, task_id, utask.main_task[task_id]['now_value'])
    else:
        utask.del_main_task(task_id)
    tools.add_user_awards(utask, award, 'task')
    return api_info()
    
