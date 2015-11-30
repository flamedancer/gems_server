# -*- coding: utf-8 -*-
""" 竞技场逻辑
"""
import time
from bottle import request
from common.exceptions import *
from common import tools 
from common.arena_user import ArenaUser
from common.utils import get_key_by_weight_dict


def api_check_arena():
    """ api/arena/check_arena
    检查竞技状态
    提供当前竞技信息(已选到第几张卡等)
    Returns:
        step(int): 当前竞技场状态 0未开启 1选第一张卡 2选第二张卡...  5准备开始竞技 6完成竞技等待领取奖励 
        selected_cards(list): 已选的卡,长度为4,未选的位为空字符串      
        team_index(str): 选择的军旗
        cards_pool(list): 备选的卡
        win(int): 已胜场数
        lose(int): 已负场数

        例:{
            'step': 3,
            'selected_cards': ['1_card', '3_card', '', ''],
            'cards_pool': [ ['1_card', '10_card', '11_card'], 
                            ['3_card', '30_card', '33_card'],
                            ['5_card', '50_card', '6_card'],
                            ['8_card', '9_card', '7_card'],
                          ],
            'win': 0,
            'lose': 0,
        }
    """
    uarena = request.user.user_arena
    # 是否结束竞技, 胜10或负2
    uarena.check_over()
    # 不在出现打折卡包界面
    if uarena.step > 6:
        uarena.reset_arena()
    return uarena.pack_info()


def get_arena_cards(user, step):
    arena_cards = []
    cardpool_conf = user._arenapool_config[str(step)]
    if len(cardpool_conf) < 3:
        raise LogicError('Cardpool cards num less than 3') 
    cid_rate_conf = {key: value['weight'] for key, value in cardpool_conf.items()}
    for cnt in range(0, 3):
        card_key = get_key_by_weight_dict(cid_rate_conf)
        get_card = cardpool_conf[card_key]['id']
        arena_cards.append(get_card)
        cid_rate_conf.pop(card_key)
    return arena_cards
        

def api_new_arena():
    """ api/arena/new_arena
    开启新的竞技场
    Returns:
        cards_pool(list): 此次竞技候选卡
    """
    uarena = request.user.user_arena
    if uarena.is_in_arena():
        raise LogicError('Aready in arena') 
    
    common_config = uarena._common_config
    # 扣竞技场道具 若无 扣金币
    uitems = uarena.user_items
    if uitems.get_item_num('arenaticket_item'):
        tools.del_user_things(uarena, 'arenaticket_item', 1, 'new_arena')
    else:
        need_coin = common_config['open_arena_coin'] 
        tools.del_user_things(uarena, 'coin', need_coin, 'new_arena')
    
    team_length = common_config['team_length']
    cards_pool = []
    for step in range(1, team_length + 1):
        cards_pool.append(get_arena_cards(uarena, step))
    uarena.set_cards_pool(cards_pool) 
    uarena.set_step(1)
    return {'cards_pool': cards_pool}


def api_select_card(step, card_id):
    """ api/arena/select_card
    玩家选卡
    Args:
        step(int): 选卡步骤数  1选第一张卡 2选第二张卡...
        card_id(str): 此次选择的卡片id
    """
    uarena = request.user.user_arena
    team_length = uarena._common_config['team_length']
    if step not in range(1, 1 + team_length):
        raise ParamsError('Step num error')
    index = step - 1
    cards_pool = uarena.cards_pool
    if card_id not in cards_pool[index]:
        raise ParamsError('Has no this card in pool')
    uarena.select_card(index, card_id)
    uarena.set_step(step + 1)
    return {}


def api_start_fight(team_index='', new_team=None):
    """ api/arena/start_fight
    开打
    Args:
        team_index(str): 选择的编队号
        new_team(list): 战斗编队
    Returns:
        enemy(dict):
            uid: 敌人uid
            name: 敌人名字
            lv: 敌人等级
            nature_*: 敌人各元素掌握度
            team: 敌人卡片队伍
        card_lv(int): 双方卡片等级
        card_favor(int): 双方卡片好感度
        
    """
    uarena = request.user.user_arena
    if not uarena.can_fight():
        raise LogicError('Cannot fight')
    api_set_team(new_team, team_index)
    common_config = uarena._common_config
    # 扣除体力
    need_stamina = common_config['arena_fight_stamina']
    tools.del_user_things(uarena, 'stamina', need_stamina, 'start_arena')

    uarena.inc_total()
    except_uids = uarena.has_fight_uids + [uarena.uid]
    arena_user = ArenaUser.get_instance()
    enemy_info = arena_user.get_random_user(except_uids=except_uids)
    arena_user.add_user(uarena.uid, uarena.selected_cards)
    # 记录战前信息
    umodified = uarena.user_modified
    umodified.temp['dungeon'] = {
        'type': 'arena',
        'time': int(time.time()),
    }
    umodified.put()
    return {'enemy': enemy_info,
            'card_lv': common_config['arena_card_lv'],
            'card_favor': common_config['arena_card_favor'],
    }


def api_end_fight(win):
    """ api/arena/end_fight
    战斗胜利
    Argv:
        win(bool): 是否胜利
    """ 
    uarena = request.user.user_arena
    if win:
        umodified = uarena.user_modified
        if 'dungeon' not in umodified.temp:
            raise LogicError('Should start fight first')
        start_info = umodified.temp['dungeon']
        if start_info.get('type') != 'arena':
            raise LogicError('End the wrong fight')
        now = int(time.time())
        if now - start_info['time'] <= 1:
            raise LogicError("rush a dungeon to quick")
        uarena.inc_win()
    uarena.check_over()
    return {}


def api_cancel_arena():
    """  api/arena/cancel_arena
    取消这次竞技
    """
    uarena = request.user.user_arena
    if not uarena.can_fight():
        raise LogicError('Cannot cancel')
    uarena.set_step(6)
    return {}


def api_get_award():
    """ api/arena/get_award
    领取竞技奖励
    Returns:
        awards: 获得奖励
        cards_price(int): 卡包价格，若达到获得折扣卡包由此字段
    """
    uarena = request.user.user_arena
    if uarena.step != 6:
        return {}
    award = uarena._arenaaward_config[str(uarena.win)]
    tools.add_user_awards(uarena, award, 'arena')
    common_config = uarena._common_config
    returns = {} 
    returns['awards'] = award
    if uarena.win >= common_config['arena_discount_win']:
        all_price = 0
        price_conf = uarena._cardup_config['price']
        card_conf = uarena._card_config
        for cid in uarena.selected_cards:
            # 拥有卡不出售 
            own_cards = uarena.user_cards.cards
            if cid not in own_cards or own_cards[cid]['num'] != 0:
                continue    
            quality = str(card_conf[cid]['quality'])
            all_price += price_conf[quality]
        if all_price:
            discount_rate = uarena._common_config['arena_discount_rate']
            returns['cards_price'] = int(all_price * discount_rate)
            uarena.set_step(7)
        else:
            uarena.reset_arena()
    else:
        uarena.reset_arena()
    return returns


def api_set_team(new_team, team_index=''):
    """ api/arena/set_team
    更改竞技编队队形
    Args:
        new_team(list): 新的卡片编队 
        team_index(str): 选择的编队号
    """
    uarena = request.user.user_arena
    if sorted(new_team) != sorted(uarena.selected_cards):
        raise ParamsError('Card not in old team')
    uarena.selected_cards = new_team
    uarena.set_team_index(team_index)
    return {}


def api_buy_discount_cards():
    """ api/arena/buy_discount_cards
    购买竞技场卡包
    """
    uarena = request.user.user_arena
    if uarena.step != 7:
        return {} 
    all_price = 0
    sell_cards = []
    price_conf = uarena._cardup_config['price']
    card_conf = uarena._card_config
    discount_rate = uarena._common_config['arena_discount_rate']
    for cid in uarena.selected_cards:
        own_cards = uarena.user_cards.cards
        if cid not in own_cards or own_cards[cid]['num'] != 0:
            continue    
        quality = str(card_conf[cid]['quality'])
        all_price += price_conf[quality]
        sell_cards.append(cid)
    all_price = int(all_price * discount_rate)
    tools.del_user_things(uarena, 'diamond', all_price, 'arena_buy_discount_cards')
    for cid in sell_cards:
        tools.add_user_things(uarena, cid, 1, 'arena_buy_discount_cards') 
    return {}

