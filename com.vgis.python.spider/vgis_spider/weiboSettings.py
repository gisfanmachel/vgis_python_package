#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    : 2021/1/18 10:31
# @Author  : chenxw
# @Email   : gisfanmache.@gmail.com
# @File    :
# @Descr   :
# @Software: PyCharm

class Setting:
    AUTH_STR = "67697366616e5f61694073696e612e636f6d262626726f6f74313233282a265e25"
    AUTH_SPLIT_STR = "&&&"

    # 初始化
    def __init__(self):
        pass

    def get_AUTH_STR(self):
        return self.AUTH_STR

    def set_AUTH_STR(self, auth_str):
        self.AUTH_STR = auth_str

    def get_AUTH_SPLIT_STR(self):
        return self.AUTH_SPLIT_STR

    def set_AUTH_SPLIT_STR(self, split_str):
        self.AUTH_SPLIT_STR = split_str
