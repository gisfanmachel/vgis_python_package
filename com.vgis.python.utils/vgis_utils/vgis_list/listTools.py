#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/6/27 14:20
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : listTools.py
# @Descr   : 
# @Software: PyCharm
from operator import itemgetter
import itertools
import numpy as np


class ListHelper:
    def __int__(self):
        pass

    # ------------------------------------
    # list数组的操作
    # ------------------------------------
    @staticmethod
    # list数组去重
    def remove_same_item(ids):
        news_ids = []
        for id in ids:
            if id not in news_ids:
                news_ids.append(id)
        return news_ids

    @staticmethod
    # 去掉list数组中重复项
    def remove_same_element_of_list(ele_list):
        new_ele_list = []
        for ele in ele_list:
            if ele not in new_ele_list:
                new_ele_list.append(ele)
        return new_ele_list

    @staticmethod
    # 去掉list数组中空白项
    def remove_blank_elment_of_list(ele_list):
        new_ele_list = []
        for ele in ele_list:
            if str(str(ele).strip()) != "":
                new_ele_list.append(ele)
        return new_ele_list

    @staticmethod
    # 查找元素在list数组中的索引号
    def get_index_in_list_of_elment(element, ele_list):
        # index = ele_list.index(element)
        return_index = -1
        for index in range(len(ele_list)):
            if ele_list[index] == element:
                return_index = index
                break
        return return_index

    @staticmethod
    # 获取元素在list数组中出现的次数
    def get_value_count_in_list(value, value_list):
        count = 0
        for tempvalue in value_list:
            if value == tempvalue:
                count = count + 1
        return count

    @staticmethod
    # 将所有list数组合并成一个list数组
    def convert_all_list_into_one_list(all_data_record_list):
        result_data_list = []
        for each_data_record_list in all_data_record_list:
            for data_field_value_obj in each_data_record_list:
                result_data_list.append(data_field_value_obj)
        return result_data_list

    # 将list数组里的数字用逗号拼接成字符串
    @staticmethod
    def get_number_str_by_list(num_list):
        number_str = ""
        for num in num_list:
            number_str = number_str + str(num) + ","
        number_str = number_str.rstrip(",")
        return number_str

    # 将list数组转换为指定字符连接的字符串
    @staticmethod
    def get_connect_str_by_list(connector_char, list_obj):
        return connector_char.join(str(x) for x in list_obj)


    # 在list的dict中找到字段的重复项，并返回索引号
    # 比如找到列表里字段重复的name
    # [{"name": "张三", "age": 20},{"name": "李四", "age": 25},{"name":"张三", "age": 20},{"name": "王五", "age": 30},{"name": "张三", "age": 35}]
    # 返回[2,4]
    def get_indexs_of_item_duplicates(self, field_name, data_list):
        items = [item[field_name] for item in data_list]
        duplicates = {item: index for index, item in enumerate(items) if items.count(item) > 1}
        indexs = []
        for value in duplicates.values():
            indexs.append(value)
        return indexs

    # 得到混合类型二维数据的指定数值列的之和
    def get_number_cloum_sum_in_list(self, data_list, column_index):
        # 创建一个混合类型的二维数组
        # # 创建一个混合类型的二维数组
        # array = np.array([[1, "2.5", [3]],
        #                   [4, "5.5", [6]],
        #                   [7, "8.5", [9]]], dtype=object)
        array = np.array(data_list, dtype=object)
        # 获取指定列的和
        need_column_sum = array[:, column_index].sum()
        print(need_column_sum)
        return need_column_sum

    # 将混合类型二维数组的指定数组列合并
    # # 假设有一个二维数组
    # array = [
    #     [[1, 8], 2, 3],
    #     [[4], 5, 6],
    #     [[7], 8, 9]
    # ]
    # 返回 [1,8,4,7]
    def combine_array_cloumns_in_list(self, data_list, column_index):

        # 使用列表推导式获取第一列
        first_column = [sublist[column_index] for sublist in data_list]
        # 使用itertools.chain合并第一列中的元素
        merged_elements = list(itertools.chain(*first_column))
        return merged_elements

    # 将字典列表中指定列的字符串连接
    # 如        # # 假设有一个二维数组（列表的列表）
    #         # matrix = [
    #         #     ['a union ', 1, 'c'],
    #         #     ['d union ', 2, 'f'],
    #         #     ['g union ', 3, 'i']
    #         # ]
    # 返回 'a union d union  g union'
    def contact_string_colums_in_list(self, data_list, column_index):

        # 使用列表推导式获取第一列的字符，然后使用join连接它们
        column_chars = ''.join([row[column_index] for row in data_list])
        return column_chars

    # 去除字典列表中的包含指定列的指定字段值的列表
    #         # # 示例使用
    #         # all_list = [
    #         #     {'name': 'Alice', 'age': 25},
    #         #     {'name': 'Bob', 'age': 30},
    #         #     {'name': 'Charlie', 'age': 35},
    #         #     {'name': 'David', 'age': 40}
    #         # ]
    #         # keyvalue_list = ['Bob', 'Charlie']
    # 返回[
    #  {'name': 'Alice', 'age': 25},
    #  {'name': 'David', 'age': 40}
    #   ]
    def remove_dict_in_list_by_key_value_list(self, all_list, key, keyvalue_list):

        return [d for d in all_list if d[key] not in keyvalue_list]

    # ---------------------------------------
    # dict字典的操作
    # ---------------------------------------

    @staticmethod
    # 根据字段名称获取dict对象里的字段索引
    def get_field_index_in_dict(dict_obj, field_name):
        key_index = 0
        field_index = None
        for key in dict_obj:
            if key == field_name:
                field_index = key_index
                break
            key_index += 1
        return field_index

    @staticmethod
    # 根据字段索引获取dict对象里的字段名称
    def get_field_name_in_dict(dict_obj, field_index):
        field_name = None
        key_index = 0
        for key in dict_obj:
            if key_index == field_index:
                field_name = key
                break
            key_index += 1
        return field_name

    @staticmethod
    # 获取dict里包含的字段列
    def get_key_name_str(data_dict):
        columns = []
        for key, value in data_dict.items():
            columns.append(key)
        return columns

    @staticmethod
    # 删除dict对象里不要的key
    def remove_keys_in_obj(obj, remove_key_list):
        for remove_key in remove_key_list:
            if remove_key in obj:
                del obj[remove_key]

    @staticmethod
    # 对dict里的字典内容进行排序
    def sort_dict_by_filed(item_list, sort_field):
        return sorted(item_list, key=itemgetter(sort_field))

    @staticmethod
    # 判断dict字典是否有搜索对象
    def is_has_item_in_dict(search_item_value, item_list):
        is_find = False
        for item_name in item_list:
            if item_name == search_item_value:
                is_find = True
                break
        return is_find
