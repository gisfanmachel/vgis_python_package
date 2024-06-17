#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2021/11/13 23:21
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : aiSettings.py
# @Descr   : 人像分割
# @Software: PyCharm


# encoding:utf-8

import base64
import time

import cv2
import numpy as np
import requests
from PIL import Image, ImageFont, ImageDraw

from vgis_utils.vgis_file.fileTools import FileHelper
from vgis_utils.vgis_image.imageTools import ImageHelper

# 百度Access Token
baidu_auth = "24.df463e180818ddfd50ad2d002f6f6c90.2592000.1641713356.282335-25323811"

'''
人像分割,基于百度接口（人体分析--人像分割）
API文档：https://cloud.baidu.com/doc/BODY/s/Fk3cpyxua
'''


# 个人账号调用总数1W，企业账号调用总数5W
# 多注册几个账号进行轮换使用
def reg_body_outline_by_baidu(baidu_ak, baidu_sk, in_file_path, out_file_path):
    global baidu_auth
    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_seg"
    # 二进制方式打开图片文件
    f = open(in_file_path, 'rb')
    img = base64.b64encode(f.read())
    imgfile = Image.open(in_file_path)
    # 获取图片原始大小
    pic_width = imgfile.width
    pic_height = imgfile.height
    params = {"vgis_image": img}
    response = get_body_seg_reponse(request_url, params)
    if response is None:
        print("百度人像分割接口调试失败，请检查")
    if "error_msg" in response.json() and response.json()['error_msg'] == "Access token invalid or no longer valid":
        baidu_auth = get_baidu_auth(baidu_ak, baidu_sk)
        response = get_body_seg_reponse(request_url, params)
    if "error_code" not in response.json():
        # 获取百度人像分割返回结果
        img_data = response.json()['labelmap']  # res为通过接口获取的返回json
        # print(img_data)
        labelmap = base64.b64decode(img_data)
        nparr = np.frombuffer(labelmap, np.uint8)
        labelimg = cv2.imdecode(nparr, 1)
        labelimg = cv2.resize(labelimg, (pic_width, pic_height), interpolation=cv2.INTER_NEAREST)
        im_new = np.where(labelimg == 1, 255, labelimg)
        # cv2.imwrite(out_file_path, im_new)
        file_suffix = FileHelper.get_file_name_suffix(out_file_path)
        cv2.imencode(file_suffix, im_new)[1].tofile(out_file_path)


# 调用百度人像分割接口得到响应
def get_body_seg_reponse(request_url, params):
    # 30天生效
    access_token = baidu_auth
    request_url = request_url + "?access_token=" + access_token
    # 验证认证码是否在有效期内，如果失效，重新请求
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    # TODO
    if response is None:
        return "fail to get license2"
    else:
        return response


# 获取百度接口调用授权码
def get_baidu_auth(API_Key, Secret_Key):
    access_token = ""
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(
        API_Key, Secret_Key)
    response = requests.get(host)
    if response:
        access_token = response.json()['access_token']
    return access_token


# 得到指定Y坐标的人像的左边和右边的边界点，TODO需要解决横线与轮廓相交产生2个以上点的情况
def getBodyLeftandRightPoint(base_y, file_path):
    # FileHelper = FileOperator()
    img = np.array(Image.open(file_path).convert('L'))
    rows, cols = img.shape
    body_left = -1
    body_right = -1
    for j in range(cols):
        if (img[base_y, j] == 255):
            if body_left == -1:
                body_left = j
        if (body_left > -1 and img[base_y, j] == 0):
            if body_right == -1:
                body_right = j - 1
        if body_right > -1:
            break
    people_image = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
    radius = 6
    color = (255, 0, 0)
    color2 = (0, 255, 0)
    line = 3
    cv2.circle(people_image, (body_left, base_y), radius, color, line)
    cv2.circle(people_image, (body_right, base_y), radius, color, line)
    out_file_path = 'E:\\tiqu\\2021-08-08 112517_调整大小_tiqu_point.png'
    file_suffix = FileHelper.get_file_name_suffix(out_file_path)
    cv2.imencode(file_suffix, people_image)[1].tofile(out_file_path)
    # cv2.imencode('.jpg', people_image)[1].tofile(image_path)


# 获取人像分割的图片
# 百度人像分割接口：不超过4M，最短边至少50px，最长边最大4096px
def getBodyOutlinePic(baidu_ak, baidu_sk, file_dir):
    all_pic_list = ImageHelper.get_image_list(file_dir)
    for each_pic in all_pic_list:
        in_file_path = each_pic
        file_size_mb = 0
        file_name = FileHelper.get_file_name(in_file_path)
        print("开始处理图片：{}".format(file_name))
        with open(in_file_path, "rb") as f:
            size = len(f.read())
            file_size_mb = size / 1e6
        if file_size_mb <= 4:
            print("图片大小：{}MB".format(file_size_mb))
            out_file_path = FileHelper.get_new_file_path_add_suffix(in_file_path, "tiqu")
            try:
                start = time.perf_counter()
                reg_body_outline_by_baidu(baidu_ak, baidu_sk, in_file_path, out_file_path)
                end = time.perf_counter()
                t = end - start
                print("图片提取共耗时(秒)：" + str(t))
            except Exception as tm_exp:
                print("百度人体分割失败：{}".format(str(tm_exp)))
            continue
        else:
            print("图片大小超过4M,不做分割操作")


# 将图像的颜色值反转(黑白互转）
def reverse_image(input_file_path):
    old_img = cv2.imdecode(np.fromfile(input_file_path, dtype=np.uint8), -1)
    new_img = np.zeros(old_img.shape, np.uint8)
    img_height = old_img.shape[0]
    img_width = old_img.shape[1]
    for i in range(img_height):
        for j in range(img_width):
            new_img[i, j] = 255 - old_img[i, j]
    file_suffix = FileHelper.get_file_name_suffix(input_file_path)
    reverse_file_path = FileHelper.get_new_file_path_add_suffix(input_file_path, "reverse")
    cv2.imencode(file_suffix, new_img)[1].tofile(reverse_file_path)
    return reverse_file_path


# 将轮廓图外部颜色变白色，人体轮廓线换颜色，有问题
def change_outline_color(input_file_path, outside_color, bodyline_color):
    old_img = cv2.imdecode(np.fromfile(input_file_path, dtype=np.uint8), -1)
    new_img = np.zeros(old_img.shape, np.uint8)
    img_height = old_img.shape[0]
    img_width = old_img.shape[1]
    for i in range(img_height):
        for j in range(img_width):
            if (j < img_width - 1) and (not np.array_equal(old_img[i, j], old_img[i, j + 1])):
                new_img[i, j] = 64
            else:
                new_img[i, j] = old_img[i, j]
    file_suffix = FileHelper.get_file_name_suffix(input_file_path)
    reverse_file_path = FileHelper.get_new_file_path_add_suffix(input_file_path, "change_line")
    cv2.imencode(file_suffix, new_img)[1].tofile(reverse_file_path)


# 提取轮廓线,线是白色的
def get_edge_extract(input_file_path):
    input_img = cv2.imdecode(np.fromfile(input_file_path, dtype=np.uint8), -1)
    # 高斯平滑
    gaussian = cv2.GaussianBlur(input_img, (5, 5), 3)
    # 边缘检测
    outline_img = cv2.Canny(input_img, 30, 100)
    file_suffix = FileHelper.get_file_name_suffix(input_file_path)
    out_file_path = FileHelper.get_new_file_path_add_suffix(input_file_path, "edge")
    cv2.imencode(file_suffix, outline_img)[1].tofile(out_file_path)
    return out_file_path


# 提取膝盖之间的最大间隔，并标绘在图上
def get_gap_between_knee(edge_file_path, lip_y, ankle_y):
    max_gap = 0
    max_row_index = 0
    edge_img = cv2.imdecode(np.fromfile(edge_file_path, dtype=np.uint8), -1)
    edge_all_points = []
    img_height = edge_img.shape[0]
    img_width = edge_img.shape[1]
    for row in range(img_height):
        each_row_points = []
        for col in range(img_width):
            if edge_img[row, col] == 255:
                each_point = {}
                each_point["x"] = col
                each_point["y"] = row
                each_row_points.append(each_point)
        edge_all_points.append(each_row_points)

    for row_index in range(len(edge_all_points)):
        each_row_points = edge_all_points[row_index]
        # 轮廓线有很多锯齿，暂时无法消除,需要计算4个交点，发现有很多地方，包括上面的衣服褶皱处，下面的脚趾处，因此需要人工设置上下两道边界线
        # 找到有四个交点，且在臀部提取点和脚踝提取点之间，计算第二个点和第三个点的距离最大值
        if len(each_row_points) == 4:
            left_x = each_row_points[1].get("x")
            right_x = each_row_points[2].get("x")
            point_y = each_row_points[1].get("y")
            if (right_x - left_x) > max_gap and point_y > lip_y and point_y < ankle_y:
                max_gap = right_x - left_x
                max_row_index = row_index
    return edge_all_points[max_row_index]


# 在原来的二值图绘制间隔最大的线，并计算长度
def draw_max_gap_line(origin_file_path, max_row_points):
    image = Image.open(origin_file_path)
    draw = ImageDraw.Draw(image)
    left_x = max_row_points[1].get("x")
    left_y = max_row_points[1].get("y")
    right_x = max_row_points[2].get("x")
    right_y = max_row_points[2].get("y")
    draw.line([(left_x, left_y),
               (right_x, right_y)], width=5, fill=128)
    label_text = str(right_x - left_x)
    font = ImageFont.truetype('simhei.ttf', 40)
    fillColor = (0, 100, 0)
    outlineColor = (0, 100, 0)
    draw.text(((right_x + left_x) / 2 - 20, left_y - 40), label_text, font=font, fill=fillColor,
              outline=outlineColor)
    # file_suffix = FileHelper.get_file_name_suffix(origin_file_path)
    out_file_path = FileHelper.get_new_file_path_add_suffix(origin_file_path, "maxgap")
    image.save(out_file_path)


if __name__ == '__main__':
    # label_file_path = 'E:\\tiqu\\2021-08-08 112517_调整大小_tiqu.png'
    # getBodyLeftandRightPoint(964, label_file_path)
    # baidu_ak = ""
    # baidu_sk = ""
    # getBodyOutlinePic(baidu_ak,baidu_sk,tiqu_file_dir)
    outline_file_path = "E:\\人像分割\\第1疗程\\第1次\\DSCF0536_调整大小_tiqu.JPG"
    # reverse_image(outline_file_path)
    # change_outline_color(outline_file_path, 29, 48)
    edge_file_path = get_edge_extract(outline_file_path)
    max_row_points = get_gap_between_knee(edge_file_path, 800, 2050)
    reverse_file_path = reverse_image(outline_file_path)
    draw_max_gap_line(reverse_file_path, max_row_points)
