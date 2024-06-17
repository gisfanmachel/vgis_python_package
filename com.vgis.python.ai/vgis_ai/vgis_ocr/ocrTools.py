#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/3/23 11:02
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : ocrTools.py
# @Descr   : 
# @Software: PyCharm
import base64
import json
import os
import urllib
import requests

# 高精度OCR
def ocr_file_high_precision_version(API_KEY, SECRET_KEY, file_path):
    (file_pre_path, temp_filename) = os.path.split(file_path)
    (shot_name, file_ext) = os.path.splitext(temp_filename)
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token=" + get_access_token(API_KEY,
                                                                                                     SECRET_KEY)
    # pdf能识别出签名，但不准，同时字符中间的空格会去掉,结果有46行
    if file_ext.lower() == ".pdf":
        payload = "pdf_file=" + get_file_content_as_base64(file_path, True)
    # 图片识别不出签名，但字符中间的空格能识别，结果有45行
    else:
        payload = "image=" + get_file_content_as_base64(file_path, True)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    json_dict = json.loads(response.text)
    return json_dict


# 高精度ORC并返回像素位置
def ocr_file_high_precision_versio_position(API_KEY, SECRET_KEY, file_path):
    (file_pre_path, temp_filename) = os.path.split(file_path)
    (shot_name, file_ext) = os.path.splitext(temp_filename)
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate?access_token=" + get_access_token(API_KEY, SECRET_KEY)
    # pdf能识别出签名，但不准，同时字符中间的空格会去掉,结果有46行
    if file_ext.lower() == ".pdf":
        payload = "pdf_file=" + get_file_content_as_base64(file_path, True)
    # 图片识别不出签名，但字符中间的空格能识别，结果有45行
    else:
        payload = "image=" + get_file_content_as_base64(file_path, True)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    json_dict = json.loads(response.text)
    return json_dict


def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content


def get_access_token(API_KEY, SECRET_KEY):
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))


# 获取识别字段值，通过前后字段名来卡，这样可以确保字段值识别的多行情况不漏掉
def get_recog_field_value_by_start_end_field_name(result_json, start_field_name, end_field_name):
    start_field_index, start_field_location = get_words_index_by_words_value(result_json, start_field_name)
    end_field_index, end_field_location = get_words_index_by_words_value(result_json, end_field_name)
    if start_field_index is not None and end_field_index is None:
        end_field_index = start_field_index + 2
    if start_field_index is None and end_field_index is not None:
        start_field_index = end_field_index - 2
    return_field_value = None
    for index in range(len(result_json["words_result"])):
        each_info = result_json["words_result"][index]
        each_words = each_info["words"]
        # 字段值可能存在多行情况，如附加险，有真换行，也有假换行
        if index > start_field_index and index < end_field_index:
            if return_field_value is not None:
                return_field_value = str(return_field_value) + " " + str(each_words)
            else:
                return_field_value = str(each_words)
    return return_field_value


# 获取识别字段值，通过前后字段名来卡，这样可以确保字段值识别的多行情况不漏掉
def get_recog_field_value_by_start_end_field_name_multi_row(result_json, start_field_name,
                                                            end_field_name, join_str):
    start_field_index, start_field_location = get_words_index_by_words_value(result_json, start_field_name)
    end_field_index, end_field_location = get_words_index_by_words_value(result_json, end_field_name)
    if start_field_index is not None and end_field_index is None:
        end_field_index = start_field_index + 2
    if start_field_index is None and end_field_index is not None:
        start_field_index = end_field_index - 2
    return_field_value = None
    for index in range(len(result_json["words_result"])):
        each_info = result_json["words_result"][index]
        each_words = each_info["words"]
        # 字段值可能存在多行情况，如附加险，有真换行，也有假换行
        if index > start_field_index and index < end_field_index:
            if return_field_value is not None:
                return_field_value = str(return_field_value) + join_str + str(each_words)
            else:
                return_field_value = str(each_words)
    return return_field_value


# 获取识别字段值，通过前后字段名来卡，这样可以确保字段值识别的多行情况不漏掉
def get_recog_field_value_by_part_start_end_field_name_multi_row(result_json, start_field_name,
                                                                 end_field_name, join_str):
    start_field_index = get_words_index_by_part_words_value(result_json, start_field_name)
    end_field_index = get_words_index_by_part_words_value(result_json, end_field_name)
    if start_field_index is not None and end_field_index is None:
        end_field_index = start_field_index + 2
    if start_field_index is None and end_field_index is not None:
        start_field_index = end_field_index - 2
    return_field_value = None
    for index in range(len(result_json["words_result"])):
        each_info = result_json["words_result"][index]
        each_words = each_info["words"]
        # 字段值可能存在多行情况，如附加险，有真换行，也有假换行
        if index > start_field_index and index < end_field_index:
            if return_field_value is not None:
                return_field_value = str(return_field_value) + join_str + str(each_words)
            else:
                return_field_value = str(each_words)
    return return_field_value


# 获取识别字段值，通过最后字段名来卡
def get_recog_field_value_by_end_field_name(result_json, end_field_name):
    end_field_index, end_field_location = get_words_index_by_words_value(result_json, end_field_name)
    return_field_value = None
    for index in range(len(result_json["words_result"])):
        each_info = result_json["words_result"][index]
        each_words = each_info["words"]
        # 字段值可能存在多行情况，如附加险
        if index > end_field_index:
            if return_field_value is not None:
                return_field_value = str(return_field_value) + " " + str(each_words)
            else:
                return_field_value = str(each_words)
    return return_field_value


# 获取识别字段值，通过前后部分字段名来卡，这样可以确保字段值识别的多行情况不漏掉
def get_recog_field_value_by_part_start_end_field_name(result_json, start_field_name, end_field_name):
    start_field_index = get_words_index_by_part_words_value(result_json, start_field_name)
    end_field_index = get_words_index_by_part_words_value(result_json, end_field_name)
    if start_field_index is not None and end_field_index is None:
        end_field_index = start_field_index + 2
    if start_field_index is None and end_field_index is not None:
        start_field_index = end_field_index - 2
    return_field_value = None
    for index in range(len(result_json["words_result"])):
        each_info = result_json["words_result"][index]
        each_words = each_info["words"]
        # 字段值可能存在多行情况，如附加险
        if index > start_field_index and index < end_field_index:
            if return_field_value is not None:
                return_field_value = str(return_field_value) + " " + str(each_words)
            else:
                return_field_value = str(each_words)
    return return_field_value


# 获取预报单的识别字段值，在自己的字段名里
def get_recog_field_value_in_sub_insurance_by_single_field_name(result_json, single_field_name):
    return_field_value = None
    for index in range(len(result_json["words_result"])):
        each_info = result_json["words_result"][index]
        each_words = each_info["words"]
        # 字段值可能存在多行情况，如附加险
        if strip_str(single_field_name) in strip_str(each_words):
            return_field_value = each_words
    return return_field_value


# 去掉字符串中的前后中间空格
def strip_str(str):
    return str.strip().replace(" ", "")


# 根据表头第一列的位置，计算表内容第一列位置对应的索引
def get_first_tbody_cell_value_index(result_json, first_head_value_postion, first_head_value_index):
    head_left_position = first_head_value_postion["left"]
    return_index = None
    for index in range(len(result_json["words_result"])):
        each_info = result_json["words_result"][index]
        each_words = each_info["words"]
        if "location" in each_info:
            each_location = each_info["location"]
            left_position = each_location["left"]
            if index > first_head_value_index and abs(left_position - head_left_position) < 2:
                return_index = index
                break
    return return_index


# 通过字段名获取字段索引在json中的索引
# 如果字段名有重复，这里是第一次出现的索引
def get_words_index_by_words_value(result_json, words_value):
    return_words_index = None
    return_words_location = None
    each_location = None
    for index in range(len(result_json["words_result"])):
        each_info = result_json["words_result"][index]
        each_words = each_info["words"]
        if "location" in each_info:
            each_location = each_info["location"]
        if strip_str(words_value) == strip_str(each_words):
            return_words_index = index
            return_words_location = each_location
            break
    return return_words_index, return_words_location


# 获取字段值根据字段索引在json中的
def get_words_value_by_words_index(result_json, words_index):
    return_words_value = None
    return_words_location = None
    each_location = None
    for index in range(len(result_json["words_result"])):
        each_info = result_json["words_result"][index]
        each_words = each_info["words"]
        if "location" in each_info:
            each_location = each_info["location"]
        if words_index == index:
            return_words_value = each_words
            return_words_location = each_location
            break
    return return_words_value, return_words_location


# 通过部分字段名获取字段索引在json中的
def get_words_index_by_part_words_value(result_json, words_value):
    return_words_index = None
    for index in range(len(result_json["words_result"])):
        each_info = result_json["words_result"][index]
        each_words = each_info["words"]
        if strip_str(words_value) in strip_str(each_words):
            return_words_index = index
            break
    return return_words_index

if __name__ == '__main__':
    file_path = "E:\\work-维璟\\2 项目实施\\2.1行业应用部\\54保险OCR识别\原油附件压缩包\\附件2收到版.pdf"
    ocr_file_high_precision_version(file_path)
