#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    : 2021/1/7 23:44
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : htmlParse.py
# @Desc    ：针对迭代器的一些操作
# @Software: PyCharm

from collections import Iterable


class IteratorHelper:
    # 初始化
    def __init__(self, iterator):
        self.iterator = iterator

    def get_iterator_count(self):
        flag = isinstance(self.iterator, Iterable)
        sum = 0
        if flag:
            for i in self.iterator:
                # print(i)
                if i is not None and str(i).strip() != "" and str(i).strip() != "\n":
                    sum = sum + 1
        return sum

    def is_has_value(self, check_array):
        flag = isinstance(self.iterator, Iterable)
        is_has = False
        if flag:
            for i in self.iterator:
                if i.text in check_array:
                    is_has = True
        return is_has
