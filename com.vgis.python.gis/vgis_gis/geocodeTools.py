"""
===================================
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Author: chenxw
@Email : gisfanmachel@gmail.com
@File: geocodeTools.py
@Date: Create in 2021/1/28 9:50
@Description: 地址匹配(百度，高德，四维等）
http://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-geocoding
（wgs84ll即GPS经纬度），2（gcj02ll即国测局经纬度坐标），3（bd09ll即百度经纬度坐标），4（bd09mc即百度米制坐标）
@ Software: PyCharm
===================================
"""
import json
from time import sleep

import requests


class AddressMatcher:
    # 初始化
    def __init__(self, baidu_key_list, gaode_key_list, siwei_key_list):
        self.baidu_key_list = baidu_key_list
        self.gaode_key_list = gaode_key_list
        self.siwei_key_list = siwei_key_list
        self.baidu_key_index = 0
        self.baidu_key = self.baidu_key_list[self.baidu_key_index]
        self.baidu_key_status = "配额正常"

    # 正向匹配，从地址名/POI名到坐标
    # TODO:高德，四维的接口加入
    def geocoder_forward(self, query_address):
        # 先用百度做匹配
        result_obj = self.get_geocoder_forward_result_by_baidu(query_address)
        # 配额用完，切换下一个账号许可，再执行一次
        if self.baidu_key_status == "配额用完":
            result_obj = self.get_geocoder_forward_result_by_baidu(query_address)
        # 针对百度没有匹配上的再用高德匹配
        # if result_obj.get("经度") is None:
        #     result_obj = self.get_geocoder_forward_result_by_gaode(query_address)
        # # 针对百度和高德都没有匹配上的再用四维匹配
        # if result_obj.get("经度") is None:
        #     result_obj = self.get_geocoder_forward_result_by_siwei(query_address)
        return result_obj

    # 通过百度进行正向地址匹配
    def get_geocoder_forward_result_by_baidu(self, query_address):
        sleep(1)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
        }
        url = 'http://api.map.baidu.com/geocoding/v3/?address={}&output=json&ak={}&ret_coordtype=wgs84ll'.format(
            query_address, self.baidu_key)
        res = requests.get(url, headers=headers)
        res.encoding = 'utf-8-sig'
        data = json.loads(res.text)
        result_obj = {}
        if data.get("status") == 0:
            self.baidu_key_status = "配额正常"
            result_obj['经度'] = data['result'].get('location').get('lng')
            result_obj['纬度'] = data['result'].get('location').get('lat')
        # 没有查询结果
        elif data.get("status") == 1:
            self.baidu_key_status = "配额正常"
            result_obj['经度'] = None
            result_obj['纬度'] = None
        # 超出配额限制
        elif data.get("status") == 301 or data.get("status") == 302:
            result_obj['经度'] = None
            result_obj['纬度'] = None
            print("------------------------------{}配额用完".format(self.baidu_key))
            self.baidu_key_index += 1
            self.baidu_key = self.baidu_key_list[self.baidu_key_index]
            self.baidu_key_status = "配额用完"
            print("-------------------------------切换到新许可{}".format(self.baidu_key))
        return result_obj

    # 通过高德进行正向地址匹配
    def get_geocoder_forward_result_by_gaode(self):
        result_obj = {}
        # result_obj['经度'] = data['result'].get('location').get('lng')
        # result_obj['纬度'] = data['result'].get('location').get('lat')
        return result_obj

    # 通过四维进行正向地址匹配
    def get_geocoder_forward_result_by_siwei(self):
        result_obj = {}
        # result_obj['经度'] = data['result'].get('location').get('lng')
        # result_obj['纬度'] = data['result'].get('location').get('lat')
        return result_obj

    # 逆向匹配，从坐标到地址
    def geocoder_reverse(self):
        pass

    # 通过百度逆向地址匹配
    def get_geocoder_reverse_result_by_baidu(self, query_lat, query_lon):
        result_obj = {}
        url = "http://api.map.baidu.com/reverse_geocoding/v3/?ak={}&output=json&coordtype=wgs84ll&location=".format(
            self.baidu_key) + str(
            query_lat) + "," + str(query_lon)
        payload = {}
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        obj_json = json.loads(response.text)
        result_obj["省"] = obj_json.get("result").get("addressComponent").get("province")
        result_obj["地市"] = obj_json.get("result").get("addressComponent").get("city")
        result_obj["区县"] = obj_json.get("result").get("addressComponent").get("district")
        return result_obj
