#-*- coding: utf-8 -*-

import os
import datetime
from bottle import route, request, view
from bottle import jinja2_view as view
from admin.decorators import validate

resource_path = 'static/resource/resource.zip'

@route('/resource_version')
def resource_version():
    if not os.path.isfile(resource_path):  
        return 0
    else:
        return int(os.path.getctime(resource_path))


@route('/admin/upload_resource', method=['GET', 'POST'])
@view('upload_resource.html')
@validate
def upload_resource():
    uploadfile=request.files.get('data')  #获取上传的文件
    new_upload = False
    if uploadfile:
        uploadfile.save(resource_path, overwrite=True)  #overwrite参数是指覆盖同名文件
        new_upload = True
        
    now_version = resource_version()
    last_upload_time = datetime.datetime.fromtimestamp(now_version) 
    return {'last_upload_time': last_upload_time, 'is_new_upload': new_upload}
