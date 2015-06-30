#-*- coding: utf-8 -*-

from bottle import post, get, request
from models.user_base import UserBase 
from common.preaction import prelogic

@post('/login')
@prelogic
def login():
    print "#####test dir request.forms::", dir(request.forms)
    uid = str(request.forms.get('uid', ''))
    # test list
    list_data = request.forms.get('list_data')
    print "#####test list_data:: by get", list_data 
    list_data = request.forms.getlist('list_data')
    print "#####test list_data:: by getlist", list_data 

    list_data = request.forms.getall('list_data')
    print "#####test list_data:: by getlist", list_data 

    # test dir
    dir_data = request.forms.get('dir_data')
    print "#####test dir_data:: by get", dir_data 
    dir_data = request.forms.getall('dir_data')
    print "#####test dir_data:: by getall", dir_data 

    # test normal
    uid_data = request.forms.get('uid')
    print "#####test uid_data:: by get", uid_data 
    uid_data = request.forms.getall('uid')
    print "#####test uid_data:: by get", uid_data 


    print "#####test allvalues:: values", request.forms.values() 
    print "#####test allvalues:: items", request.forms.items() 
    Ubase = UserBase.get(uid)
    if not Ubase:
        print "create new uid", uid
       
            
        Ubase = UserBase.create(uid)
        Ubase.put()
    Uproperty = Ubase.user_property
    #Uproperty.add_thing('money', 100)
        

    return Uproperty.__dict__ 

    Ubase = UserBase.get(uid)
    if not Ubase:
        print "create new uid", uid
       
            
        Ubase = UserBase.create(uid)
        Ubase.put()
    Uproperty = Ubase.user_property
    #Uproperty.add_thing('money', 100)
        

    return Uproperty.__dict__ 
