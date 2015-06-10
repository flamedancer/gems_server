#-*- coding: utf-8 -*-

from bottle import post, get, request
from models.user_base import UserBase 
from common.preaction import prelogic

@post('/login')
@prelogic
def login():
    uid = str(request.forms.get('uid', ''))
    print uid
    Ubase = UserBase.get(uid)
    if not Ubase:
        print "create new uid", uid
       
            
        Ubase = UserBase.create(uid)
        Ubase.put()
    Uproperty = Ubase.user_property
    #Uproperty.add_thing('money', 100)
        

    return Uproperty.__dict__ 
