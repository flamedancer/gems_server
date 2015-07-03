# -*- coding: utf-8 -*-

from models import GameModel

def log(thing, num, way):
    print "add thing num way", thing, num, way 
    pass

def add_user_things(user, thing, num, way):
    Umodified = user.user_modified

    if thing in ['lv', 'vip_lv', 'exp', 'stamina', 'diamond',          'money',
        'city_jeton', 'pk_jeton', 'heroSoul', 'master_0',
         'master_1', 'master_2', 'master_3', 'master_4',
         'master_5', 'master_remain']:
        new_num = user.user_property.add_thing(thing, num)
        Umodified.modified[thing] = new_num
    elif thing.endswith('_card'):
        new_card_info = user.user_cards.add_card(thing, num)
        Umodified.modified['card'] = {thing: new_card_info}
    Umodified.put()
    log(thing, num, way)
    
