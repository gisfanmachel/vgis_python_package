#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/6/27 15:24
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : __init__.py.py
# @Descr   : 
# @Software: PyCharm
from vgis_database.pgTools import PgHelper

__all__ = 'PgHelper'

# 原来的引用方式
# from vgis_database.pgTools import PgHelper
# 现在的引用方式,这样做的目的是将pgTools.py编译成pyd
# from vgis_database import PgHelper
