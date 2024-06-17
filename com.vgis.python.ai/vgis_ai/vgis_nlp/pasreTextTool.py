#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    : 2021/1/18 10:24
# @Author  : chenxw
# @Email   : gisfanmache.@gmail.com
# @File    : pasreTextTool.py
# @Descr   : 从文本信息里识别出有用资料
# @Software: PyCharm

from aip import AipNlp


class TextParser:
    # 初始化
    def __init__(self):
        pass

    def parse_address_in_text(self, APP_ID, API_KEY, SECRET_KEY, pasre_text):
        # setting = Setting()
        # auth_str = setting.get_AIP_AUTH_STR()
        # decode_str = binascii.a2b_hex(auth_str).decode("utf-8")
        # key_list = decode_str.split(setting.get_AUTH_SPLIT_STR())
        client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
        result = client.address(pasre_text)
        obj = {}
        if "error_code" not in result:
            obj["is_success"] = True
            obj["province"] = result.get("province")
            obj["city"] = result.get("city")
            obj["county"] = result.get("county")
            obj["town"] = result.get("town")
        else:
            obj["is_success"] = False
            obj["error_code"] = result.get("error_code")
            obj["error_msg"] = result.get("error_msg")
        return obj
