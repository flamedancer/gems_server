#-*- coding: utf-8 -*-

import os
import glob
from bottle import TEMPLATE_PATH

TEMPLATE_PATH.append('admin/templates/')

__all__ = [os.path.basename(
    f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py") if not f.startswith('__')]

