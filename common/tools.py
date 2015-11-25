# -*- coding: utf-8 -*-

from models import GameModel


def log(thing, num, way):
    print "******add thing num way", thing, num, way 


def add_user_things(user, thing, num, way):
    umodified = user.user_modified
    change_info = None

    if thing in ['lv', 'vip_lv', 'stamina', 'diamond',
         'coin', 'city_jeton', 'pk_jeton', 'heroSoul', 'nature_0',
         'nature_1', 'nature_2', 'nature_3', 'nature_4',
         'nature_5', 'nature_remain']:
        new_num = user.user_property.add_thing(thing, num)
        umodified.set_modify_info(thing, new_num)
        change_info = new_num
    elif thing == 'exp':
        modified_info = user.user_property.add_exp(num)
        umodified.update_modify(modified_info)
        change_info = user.user_property.exp
    elif thing.endswith('_card'):
        new_card_info = user.user_cards.add_card(thing, num)
        umodified.set_modify_info('cards', {thing: new_card_info})
        change_info = new_card_info
    elif thing.endswith('_item'):
        new_item_info = user.user_items.add_item(thing, num)
        umodified.set_modify_info('items', {thing: new_item_info})
        change_info = new_item_info
    elif thing == 'invade_jeton':
        uinvade = user.user_invade
        uinvade.add_invade_jeton(num)
    log(thing, num, way)
    return change_info 


def del_user_things(user, thing, num, way):
    umodified = user.user_modified
    change_info = None
    if thing in ['lv', 'vip_lv', 'exp', 'stamina', 'diamond',
         'coin', 'city_jeton', 'pk_jeton', 'heroSoul', 'nature_0',
         'nature_1', 'nature_2', 'nature_3', 'nature_4',
         'nature_5', 'nature_remain']:
        new_num = user.user_property.del_thing(thing, num)
        umodified.set_modify_info(thing, new_num)
        change_info = new_num
        return new_num
    elif thing.endswith('_card'):
        new_card_info = user.user_cards.del_card(thing, num)
        umodified.set_modify_info('cards', {thing: new_card_info})
        change_info = new_card_info
    elif thing.endswith('_item'):
        new_item_info = user.user_items.del_item(thing, num)
        umodified.set_modify_info('items', {thing: new_item_info})
        change_info = new_item_info
    elif thing == 'invade_jeton':
        uinvade = user.user_invade
        uinvade.add_invade_jeton(-num)
    return change_info
    print "******del thing num way", thing, num, way 


def update_user_info(user, thing, new_info, way):
    umodified = user.user_modified
    change_info = None
    if thing in ['name',]:
        new_name = user.user_base.change_name(new_info)
        umodified.set_modify_info(thing, new_name)
        return new_name
    elif thing in ['lv', 'vip_lv', 'exp', 'stamina', 'diamond',
         'coin', 'city_jeton', 'pk_jeton', 'heroSoul', 'nature_0',
         'nature_1', 'nature_2', 'nature_3', 'nature_4',
         'nature_5', 'nature_remain']:
        new_num = new_info
        uproperty = user.user_property 
        setattr(uproperty, thing, new_num)
        uproperty.put()
        umodified.set_modify_info(thing, new_num)
        change_info = new_num
        return new_num
        
        
    print "******update user info way", thing, new_info, way 


def add_user_awards(user, award, way):
    for thing, info in award.items():
        # 'card' : [['1_card', 1]...
        if thing == 'card':
            for cid, num in info:
                add_user_things(user, cid, num, way)
        if thing == 'item':
            for itemid, num in info:
                add_user_things(user, itemid, num, way)
        else:
            add_user_things(user, thing, info, way)
        

