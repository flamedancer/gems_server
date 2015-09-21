#-*- coding: utf-8 -*-

import ast
import json
import time

from common.game_config import CONFIG_TITLES 
from common.game_config import NOTE 
from common.game_config import get_config_str 
from common.game_config import get_config_dir 
from common.game_config import set_config_update_time 
from libs.model import ConfigModel 

from bottle import route, request, static_file
from bottle import jinja2_view as view
import xlrd
from admin.decorators import validate
from libs.model import RedisKeyValue

@route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='./static/')
    

@route('/resource_version')
def resource_version():
    system_conf = get_config_dir('system_config')
    return system_conf.get('resource_version', 0)  


@route('/admin/game_config', method=['GET', 'POST'])
@view('game_config.html')
@validate
def config_view():
    this_config_name = request.query.get('config_name')
    view = {} 
    excel_file = request.files.get('xls')
    if excel_file:
        view = make_config(excel_file.file, this_config_name)
    elif this_config_name:
        view = get_config_str(this_config_name)
       
    return {'config_titles': CONFIG_TITLES, 'config_value': view, 'config_name': this_config_name, 'config_note': NOTE.get(this_config_name, '')}


@route('/admin/save_config', method='POST')
@validate
def save_config():
    this_config_name = request.forms.get('config_name')
    this_config_value = request.forms.get('config_value')
    # 校验是否为json数据
    this_config_value = json.loads(this_config_value)  
    config_obj = ConfigModel.get(this_config_name)
    # config_list里是否有这个配置
    if not config_obj:
        has_get = False
        for config_info in CONFIG_TITLES:
            for name_conf in config_info['content']:
                if name_conf[0] == this_config_name:
                    config_obj = ConfigModel.create(this_config_name)
                    has_get = True
                    break
            if has_get:
                break
        else:
            raise Exception('This Config  Not Exist')
    config_obj.data = this_config_value
    config_obj.put()
    set_config_update_time(this_config_name)
    return ''
        
    

def make_config(excel_file, this_config_name):
    excel = xlrd.open_workbook(file_contents = excel_file.read())
    sheet = excel.sheet_by_name('config')
    return excel_explain(sheet)
    


def excel_explain(sheet):
    make_dict = {}
    first_column = sheet.col_values(0)
    first_row = sheet.row_values(0)
    for row_num in range(1, len(first_column)):
        keys = sheet.cell(row_num, 0).value
        values = sheet.cell(row_num, 1).value
        type_cell = sheet.cell(row_num, 2).value
        keys_list = keys.split('>')
        
        walk_dict = make_dict 
        try:
            for key in keys_list:
                if key in walk_dict:
                    walk_dict = walk_dict[key]
                    continue
                walk_dict[key] = {}
                if key != keys_list[-1]:
                    walk_dict = walk_dict[key]
                    continue
                if type_cell == 'bool':
                    walk_dict[key] = bool(values)
                elif type_cell == 'list':
                    walk_dict[key] = ast.literal_eval('[' + values + ']')
                elif type_cell == 'str':
                    if isinstance(values, (int, float)):
                        walk_dict[key] = str(values)
                    else:
                        walk_dict[key] = values
                elif type_cell == 'int':
                    walk_dict[key] = int(values)
                elif type_cell == 'float':
                    walk_dict[key] = float(values)
                else:
                    raise Exception('ERRO TYPE')
                walk_dict = walk_dict[key]
        except Exception, e:
            print e.message
            erro_msg = u"ERROR RAISE in line {}: {}, {}, {}".format(row_num, unicode(key), unicode(values), unicode(type_cell)) 
            print erro_msg
            raise Exception(erro_msg)
    return json.dumps(make_dict)

