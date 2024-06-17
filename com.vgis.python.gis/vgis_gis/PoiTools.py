"""
===================================
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Author: chenxw
@Email : gisfanmachel@gmail.com
@File: poiTools.py
@Date: Create in 2021/1/28 9:59
@Description: POI数据查询
http://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-placeapi
@ Software: PyCharm
===================================
"""

import json
import math
from time import sleep

import requests

from vgis_utils.vgis_list.listTools import ListHelper


class POIOperater:

    def __init__(self, baidu_key_list, baidu_city_code_txt):
        self.baidu_key_list = baidu_key_list
        self.baidu_city_code_txt = baidu_city_code_txt
        self.baidu_key_index = 0
        self.baidu_key = self.baidu_key_list[self.baidu_key_index]
        self.baidu_key_status = "配额正常"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36",
        }

    # 连接百度接口，判断状态,如果许可配额用完，切换到另外一个配合
    def make_baidu_connect_and_return_data(self, query_word, region_name, page_num):
        sleep(1)
        url = 'http://api.map.baidu.com/place/v2/search?query=%s&region=%s&output=json&ak=%s&page_size=20&page_num=%s&coord_type=wgs84ll' % (
            query_word, region_name, self.baidu_key, page_num)
        res = requests.get(url, headers=self.headers)
        res.encoding = 'utf-8-sig'
        data = json.loads(res.text)
        if data.get("status") == 0:
            self.baidu_key_status = "配额正常"
            return data
        # 超出配额限制
        elif data.get("status") == 301 or data.get("status") == 302:
            print("------------------------------{}配额用完".format(self.baidu_key))
            self.baidu_key_index += 1
            if self.baidu_key_index <= len(self.baidu_key_list) - 1:
                self.baidu_key = self.baidu_key_list[self.baidu_key_index]
                self.baidu_key_status = "配额用完"
                print("-------------------------------切换到新许可{}".format(self.baidu_key))
                url = 'http://api.map.baidu.com/place/v2/search?query=%s&region=%s&output=json&ak=%s&page_size=20&page_num=%s&coord_type=wgs84ll' % (
                    query_word, region_name, self.baidu_key, page_num)
                res = requests.get(url, headers=self.headers)
                res.encoding = 'utf-8-sig'
                data = json.loads(res.text)
                if data.get("status") == 0:
                    self.baidu_key_status = "切换的配额正常"
                    return data
                elif data.get("status") == 301 or data.get("status") == 302:
                    # 这个时候，会漏掉本次查询的
                    self.baidu_key_status = "切换的配额用完"
                    return None
            else:
                print("-------------------------------所有的配额都用完，请第二天再使用")
                return None

    # 触发调用百度接口，获取结果对象
    def toogle_query_baidu_poi(self, query_word, region_name, page_num):
        return self.make_baidu_connect_and_return_data(query_word, region_name, page_num)

    # 触发调用百度接口，获取结果类型
    def get_query_baidu_data_type(self, query_word, region_name, page_num):
        data = self.make_baidu_connect_and_return_data(query_word, region_name, page_num)
        return data['result_type']

    # 得到city_type下面的name,有可能是省，也可能是地市
    def get_result_name_list_of_city_type(self, query_word, region_name, page_num):
        result_name_list = []
        data = self.make_baidu_connect_and_return_data(query_word, region_name, page_num)
        for t in range(0, len(data['results'])):
            result_region_name = data['results'][t].get('name')
            result_name_list.append(result_region_name)
        return result_name_list

    # 获取百度查询需要的地市名称，根据百度接口返回结果调整
    # 不支持任意值的区域名称
    def get_area_region_of_baidu_need(self, query_word, region_name):
        need_region_list = []
        if region_name == "全国":
            need_region_list = self.get_all_city_of_country()
        else:
            if self.get_query_baidu_data_type(query_word, region_name, 0) == "poi_type":
                # 针对只有一页的poi_type
                if self.get_query_baidu_data_type(query_word, region_name, 1) is None:
                    need_region_list.append(region_name)
                else:
                    # 针对两页多的poi_type
                    if self.get_query_baidu_data_type(query_word, region_name, 1) == "poi_type":
                        need_region_list.append(region_name)
                    # 第一页是poi_type,第二页是city_type, 如区域为四川，关键词是煤炭厂
                    elif self.get_query_baidu_data_type(query_word, region_name, 1) == "city_type":
                        result_name_list = self.get_result_name_list_of_city_type(query_word, region_name, 1)
                        for result_name in result_name_list:
                            need_region_list.append(result_name)
            elif self.get_query_baidu_data_type(query_word, region_name, 0) == "city_type":
                # 煤炭厂 嘉峪关市
                if self.get_query_baidu_data_type(query_word, region_name, 1) == "poi_type":
                    pass
                else:
                    result_name_list2 = self.get_result_name_list_of_city_type(query_word, region_name, 1)
                    for result_name2 in result_name_list2:
                        need_region_list.append(result_name2)
        return need_region_list

    # 从百度地图官网上下载的百度地图city_code文件中获取全国的城市列表
    # 后期百度地图的city_code更新后，同步更新这个txt文件接口
    # 下载地址：http://lbsyun.baidu.com/index.php?title=open/%E5%BC%80%E5%8F%91%E8%B5%84%E6%BA%90
    def get_all_city_of_country(self):
        city_list = []
        with open(self.baidu_city_code_txt, 'r', encoding='UTF-8') as file:
            city_code_file = file.read()
            current_row = 0
            line_list = city_code_file.split("\n")
            for line in line_list:
                current_row += 1
                if current_row == 1:
                    continue
                else:
                    city_list.append(line.split(",")[1])
        return city_list

    # 单次调用百度地图接口获取结果数据
    def get_poi_data_from_baidu(self, query_word, region_name):
        print("对{}内的{}进行采集".format(region_name, query_word))
        query_result = []
        data = self.toogle_query_baidu_poi(query_word, region_name, 0)
        # 即使是正常地市名，也会查询出city_code，如煤炭厂，嘉峪关市，第一页是city_code,第二页是poi_type，但没有数值
        # 上述情况有可能是嘉峪关市没有煤炭厂的原因
        if data is not None and data['result_type'] == "poi_type":
            total = data['total']
            pageSize = math.ceil(total / 20)
            if (pageSize):
                for i in range(0, pageSize):
                    print("采集第{}/{}页数据".format(str(i + 1), str(pageSize)))
                    data = self.toogle_query_baidu_poi(query_word, region_name, i)
                    if data is not None:
                        for t in range(0, len(data['results'])):
                            obj = {}
                            try:
                                obj['名称'] = data['results'][t].get('name')
                            except:
                                obj['名称'] = ""
                                pass
                            try:
                                address = data['results'][t].get('province') + ',' + data['results'][t].get(
                                    'city') + ',' + \
                                          data['results'][t].get('area') + ',' + data['results'][t].get('address')
                                obj['地址'] = address
                            except:
                                obj['地址'] = ""
                                pass
                            try:
                                obj['省份'] = data['results'][t].get('province')
                            except:
                                obj['省份'] = ""
                                pass
                            try:
                                obj['地市'] = data['results'][t].get('city')
                            except:
                                obj['地市'] = ""
                                pass
                            try:
                                obj['区县'] = data['results'][t].get('area')
                            except:
                                obj['区县'] = ""
                                pass
                            try:
                                obj['电话'] = data['results'][t].get('telephone')
                            except:
                                obj['电话'] = ""
                                pass
                            try:
                                obj['经度'] = data['results'][t].get('location').get('lng')
                            except:
                                obj['经度'] = ""
                                pass
                            try:
                                obj['纬度'] = data['results'][t].get('location').get('lat')
                            except:
                                obj['纬度'] = ""
                                pass
                            query_result.append(obj)
        return query_result

    # 批量调用百度POI接口获取所有结果
    # TODO:获取高德，四维的POI
    def get_all_poi_data_batch_by_baidu(self, query_word, query_region):
        all_result_list = []
        need_region_list = self.get_area_region_of_baidu_need(query_word, query_region)
        for need_region in need_region_list:
            try:
                if self.get_poi_data_from_baidu(query_word, need_region) is not None and len(
                        self.get_poi_data_from_baidu(query_word, need_region)) > 0:
                    all_result_list.append(self.get_poi_data_from_baidu(query_word, need_region))
            except:
                pass
            continue
        all_result_list_converse = ListHelper.convert_all_list_into_one_list(all_result_list)
        return all_result_list_converse
