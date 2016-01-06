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


@route('/admin/upload_resource', method='GET')
@view('upload_resource.html')
@validate
def upload_resource():
    now_version = resource_version()
    last_upload_time = datetime.datetime.fromtimestamp(now_version) 
    return {'last_upload_time': last_upload_time}


@route('/admin/save_resource', method='POST')
@view('upload_reource.html')
@validate
def upload_resource():
    uploadfile=request.files.get('data')  #获取上传的文件
    uploadfile.save(resource, overwrite=True)  #overwrite参数是指覆盖同名文件
    return u"上传成功,文件名为：%s，文件类型为：%s"% (uploadfile.filename,uploadfile.content_type)


