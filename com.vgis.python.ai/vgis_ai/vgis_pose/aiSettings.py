#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2021/9/24 14:10
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : aiSettings.py
# @Descr   : AI识别配置文件
# @Software: PyCharm


class Setting:
    PEOPLE_PROGRAM_PATH = "E:\\AI\\openpose\\program\\bin"

    # 初始化
    def __init__(self):
        pass

    def get_PEOPLE_PROGRAM_PATH(self):
        return self.PEOPLE_PROGRAM_PATH

    def set_PEOPLE_PROGRAM_PATH(self, people_program_path):
        self.PEOPLE_PROGRAM_PATH = people_program_path


