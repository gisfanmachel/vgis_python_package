#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    : 2021/1/8 9:52
# @Author  : chenxw
# @Email   : gisfanmache.@gmail.com
# @File    : commonTools.py
# @Descr   : 通用工具类
# @Software: PyCharm
import platform
import subprocess


class CommonHelper:
    # 初始化
    def __init__(self):
        pass

    @staticmethod
    # 获取换行符
    def get_line_feed():
        if platform.system() == 'Windows':
            return "\n"
        else:
            return "\n"

    @staticmethod
    # 得到文件路径的斜杆写法
    # 也可以直接用os.sep
    def get_dash_in_system():
        if platform.system() == 'Windows':
            return "\\"
        else:
            return "/"


    @staticmethod
    # 执行cmd命令
    def run_command( cmd_str):
        out = subprocess.Popen(cmd_str, shell=True)



    @staticmethod
    # 转换布尔值为中文
    def convert_to_boolean_evalue(boolean_cvalue):
        boolean_evalue = True
        if boolean_cvalue == "否" or boolean_cvalue == False:
            boolean_evalue = False
        return boolean_evalue

    @staticmethod
    # 转换布尔值为英文
    def convert_to_boolean_cvalue(boolean_evalue):
        boolean_cvalue = "是"
        if boolean_evalue == False or boolean_evalue == "否":
            boolean_cvalue = "否"
        return boolean_cvalue





