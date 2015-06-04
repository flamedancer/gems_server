#-*- coding: utf-8 -*-

from bottle import post, get, request
from models.user_base import UserBase 


@post('/login')
def login():
    uid = str(request.forms.get('uid', ''))
    print uid
    ubase = UserBase.get(uid)
    if not ubase:
        print "create new"
            
        ubase = UserBase.create(uid)
    return ubase.__dict__ 
