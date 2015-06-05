#-*- coding: utf-8 -*-

import ast
import json

from bottle import route, request, static_file
from bottle import jinja2_view as view
import xlrd

@route('/static/<filepath:path>')
def server_static(filepath):
    print filepath
    return static_file(filepath, root='./static/')
    return ''
    
    


@route('/admin/config_view', method=['GET', 'POST'])
@view('admin/templates/config_view.html')
def config_view():
    print dir(request)
    view = '' 
    excel_file = request.files.get('xls')
    if excel_file:
        print excel_file.__dict__
        view = make_config(excel_file.file)
       
    return {'config_value': view}


def make_config(excel_file):
    excel = xlrd.open_workbook(file_contents = excel_file.read())
    sheet = excel.sheet_by_name('cardata')
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
        
        count = 0
        walk_dict = make_dict 
        try:
            for key in keys_list:
                if key in walk_dict:
                    walk_dict = walk_dict[key]
                    continue
                walk_dict[key] = {}
                if key != keys_list[-1]:
                    continue
                if type_cell == 'bool':
                    walk_dict[key] = bool(values)
                elif type_cell == 'list':
                    walk_dict[key] = ast.literal_eval('[' + values + ']')
                elif type_cell == 'str':
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
            erro_msg = u"ERROR RAISE in line {} : {}，{}， {}".format(row_num, unicode(key), unicode(values), unicode(type_cell)) 
            print erro_msg
            raise Exception(erro_msg)
    return json.dumps(make_dict)

