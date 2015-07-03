# -*- coding: utf-8 -*-

import datetime
from bottle import request, redirect
from admin.models.employee import Employee
from admin.permissions import ALL_PERMISSIONS


def validate(func):
    def warp_func(*args, **kwargs):
        username = request.get_cookie('username')
        password = request.get_cookie('password')
        print "$$$", username, password
        if not (username and password):
            redirect('/admin/login')
        else:
            em = Employee.get(username)
            if not em or not em.check_password(password):
                redirect('/admin/login')
        request.employee = em
        # 更新雇员信息
        login_ip = request.remote_addr
        login_time = str(datetime.datetime.now())[:19]  
        em.last_ip = login_ip
        em.last_login_time = login_time
        em.put()
        result = func(*args, **kwargs)
        if isinstance(result, dict):
            em_permissions = em.permissions
            result.update(
                {
                    'selfRealname': em.realname,
                    'selfIsSuper': em.is_super(),
                    'selfInreview': em.in_review,
                    'selfPermissionsConf': {} if em.in_review else ([perm for perm in
                     ALL_PERMISSIONS if perm['permission']
                     in em_permissions] if not em.is_super() else ALL_PERMISSIONS),
                    'supermsg_num': get_supermsg_num(),
                    'selfApplyPermissmionConf': [perm for perm in ALL_PERMISSIONS if perm['permission'] in em.new_permissions],
                },
                    
            )
        return result
    return warp_func
          
def get_supermsg_num():
    msgnum = 0
    all_employee_info = Employee.find({})
    print all_employee_info 
    for info in all_employee_info:
        if info.in_review or info.new_permissions:
            msgnum += 1
    return msgnum
