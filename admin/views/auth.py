# -*- coding: utf-8 -*-

from bottle import route, request, response, redirect
from bottle import jinja2_view as view
from admin.models.employee import Employee
from admin.decorators import validate
from admin.permissions import ALL_PERMISSIONS


@route('/admin/login', method=['GET', 'POST'])
@view('login.html')
def login():
    username = request.forms.get('inputUsername')
    password = request.forms.get('inputPassword')
    if username and password:
        em = Employee.get(username)
        if not em:
            return {'msg': u'账号不存在!'}
        elif not em.check_password(password):
            return {'msg': u'密码错误!'}
        #response.employee = em
        response.set_cookie('username', username)
        response.set_cookie('password', password)
        redirect('/admin/home')
    return {}

@route('/admin/logout', method='GET')
def logout():
    response.delete_cookie('username')
    response.delete_cookie('password')
    redirect('/admin/login')


@route('/admin/home', method='GET')
@route('/admin/', method='GET')
@view('frame.html')
@validate
def home():
    return {}

@route('/admin/detail/<employeeName>', method='GET')
@route('/admin/detail', method='GET')
@view('detail.html')
@validate
def detail(employeeName=''):
    if not employeeName:
        em = request.employee
    else:
        em = Employe.get(employeeName)
        if not Em:
            return {}
    return {
        'employeeUsername': em.username,
        'employeeRealname': em.realname,
        'employeeRole': em.role,
        'employeePermissions': em.permissions,
        'all_permissions': ALL_PERMISSIONS,
    }
