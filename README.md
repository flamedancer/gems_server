# gems_server
no mean

安装  (sudo) pip install pymongo
      (sudo) pip install redis
      (sudo) pip install msgpack-python
      (sudo) pip install Jinja2
      (sudo) pip install xlrd

      (sudo) pip install uwsgi

修改 pymongo bug  ：  在  /python2.7/site-packages/pymongo/common.py  第392行加入一行：
     'max_pool_size': validate_positive_integer_or_none,



pvp 支持:
      (sudo) pip install geventwebsocket
