# -*- coding: utf-8 -*-

from bottle import request, redirect
from admin.models.employee import Employee
from admin.permissions import ALL_PERMISSIONS


def validate(func):
    def warp_func(*args):
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
        result = func(*args)
        if isinstance(result, dict):
            em_permissions = em.permissions
            result.update(
                {
                    'employeeRealname': em.realname,
                    'employeeRole': em.role,
                    'employeePermissionsConf': [perm for perm in
                     ALL_PERMISSIONS if perm['permission']
                     in em_permissions],
                },
                    
            )
        return result
    return warp_func
          
