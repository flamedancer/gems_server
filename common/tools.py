# -*- coding: utf-8 -*-

from models import GameModel

def log(thing, num, way):
    print "******add thing num way", thing, num, way 
    pass

def add_user_things(user, thing, num, way):
    umodified = user.user_modified

    if thing in ['lv', 'vip_lv', 'exp', 'stamina', 'diamond',          'money', 'city_jeton', 'pk_jeton', 'heroSoul', 'nature_0',
         'nature_1', 'nature_2', 'nature_3', 'nature_4',
         'nature_5', 'nature_remain']:
        new_num = user.user_property.add_thing(thing, num)
        umodified.set_modify_info(thing, new_num)
        return new_num
    elif thing.endswith('_card'):
        new_card_info = user.user_cards.add_card(thing, num)
        umodified.set_modify_info('card', {thing: new_card_info})
    log(thing, num, way)


def del_user_things(user, thing, num, way):
    umodified = user.user_modified
    if thing in ['lv', 'vip_lv', 'exp', 'stamina', 'diamond',          'money', 'city_jeton', 'pk_jeton', 'heroSoul', 'nature_0',
         'nature_1', 'nature_2', 'nature_3', 'nature_4',
         'nature_5', 'nature_remain']:
        new_num = user.user_property.del_thing(thing, num)
        umodified.set_modify_info(thing, new_num)
        return new_num
    elif thing.endswith('_card'):
        new_card_info = user.user_cards.del_card(thing, num)
        umodified.set_modify_info('card', new_card_info)
    
