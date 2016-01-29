# -*- coding: utf-8 -*-

from bottle import route, request, response, redirect
from bottle import jinja2_view as view
from admin.models.employee import Employee
from admin.decorators import validate
from admin.permissions import ALL_PERMISSIONS
from admin.permissions import ALL_ROLES


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

@route('/admin/register', method=['GET', 'POST'])
@view('register.html')
def register():
    register_info = {
        'all_roles': ALL_ROLES,
        'all_permissions': ALL_PERMISSIONS,
    }
    username = request.forms.get('inputUsername')
    if not username:
         return register_info
    register_info.update({
        'inputUsername': '',
        'inputRealname': '',
        'inputRole': '',
        'inputPassword': '',
        'inputPasswordCheck': '',
        'inputPermissions': [],
    })
    for key, value in register_info.items():
        if isinstance(value, list):
            register_info[key] = request.forms.getlist(key) or register_info[key]
        else:
            register_info[key] = request.forms.get(key).decode('utf-8') or register_info[key]
    if register_info['inputPassword'] != register_info['inputPasswordCheck']:
        register_info['msg'] = u'两次输入密码不一样!'
        return register_info
    elif Employee.get(username):
        register_info['msg'] = u'账号已存在!'
        return register_info
    em = Employee()
    em.username = username
    em.realname = register_info['inputRealname']
    em.role = register_info['inputRole']
    em.permissions = register_info['inputPermissions'] 
    em.set_password(register_info['inputPassword'])
    em.put()
    response.set_cookie('username', username)
    response.set_cookie('password', register_info['inputPassword'])
    redirect('/admin/home')

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
        em = Employee.get(employeeName)
        if not em:
            return {}
    return {
        'employeeUsername': em.username,
        'employeeRealname': em.realname,
        'employeeRole': em.role,
        'employeeInreview': em.in_review,
        'employeePermissions': em.permissions,
        'employeeNewPermissions': em.new_permissions,
        'all_permissions': ALL_PERMISSIONS,
    }


@route('/admin/manage', method='GET')
@view('manage.html')
@validate
def manage():
    if not request.employee.is_super():
        return {}
    employee_list = Employee.find({})
    return {"moderator_list": employee_list}

@route('/admin/manage/delete_employee', method='GET')
@validate
def delete_employee():
    if not request.employee.is_super():
        return {}
    employeeName = request.query.get('username')
    em = Employee.get(employeeName)
    if em:
        em.delete()
    redirect('/admin/manage')

@route('/admin/manage/in_review', method='GET')
@validate
def review_employee():
    if not request.employee.is_super():
        return {}
    employeeName = request.query.get('username')
    in_review = request.query.get('in_review')
    em = Employee.get(employeeName)
    if em:
        em.in_review = True if in_review=='true' else False
        em.put()
    redirect('/admin/manage')

@route('/admin/manage/change_password/<username>', method='POST')
@view('detail.html')
@validate
def change_password(username=''):
    if username != request.employee.username and not request.employee.is_super():
        return {}
    em = Employee.get(username)
    if not em:
        return {}
    inputpassword = request.forms.get('newPassword')
    inputpasswordcheck = request.forms.get('newPasswordCheck')
    if inputpassword != inputpasswordcheck:
        return u'两次密码输入不一样!'
    em.set_password(inputpassword)
    redirect('/admin/detail/' + username)

@route('/admin/manage/apply_permissions/<username>', method='POST')
@validate
def apply_permissions(username=''):
    em = Employee.get(username)
    if not em:
        return {}
    new_permissions = request.forms.getlist('new_permissions')
    if request.employee.is_super():
        em.permissions = new_permissions
        em.new_permissions = []
        em.put()
    elif request.employee.username == username:
        em.new_permissions = new_permissions
        em.put()
    else:
        return {}
    redirect('/admin/detail/' + username)

@route('/admin/manage/set_new_permissions/<username>', method='POST')
@validate

def set_new_permissions(username=''):
    em = Employee.get(username)
    if not em or not request.employee.is_super():
        return {}
    new_permissions = request.forms.getlist('confirm_new_permissions')
    new_permissions.extend(em.permissions)
    em.permissions = list(set(new_permissions))
    em.new_permissions = []
    em.put()
    redirect('/admin/detail/' + username)
