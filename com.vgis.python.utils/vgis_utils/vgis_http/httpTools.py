#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/6/27 14:12
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : httpTools.py
# @Descr   : 
# @Software: PyCharm
class HttpHelper:
    # 初始化
    def __init__(self):
        pass


    @staticmethod
    # 获取http请求参数
    def get_params_request(request):
        params = ""
        dict_obj = None
        # POST请求
        if request.data is not None and len(request.data) != 0:
            dict_obj = request.data
        # GET请求
        elif request.query_params is not None and len(request.query_params) != 0:
            dict_obj = request.query_params
        if dict_obj is not None:
            for (k, v) in dict_obj.items():
                params = params + "{}={}".format(k, v) + "&"
        params = params.rstrip("&")

        return params

    @staticmethod
    # 获取ip地址
    def get_ip_request(request):
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META.get("HTTP_X_FORWARDED_FOR")
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip