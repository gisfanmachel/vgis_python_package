#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2021/9/24 14:10
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : aiSettings.py
# @Descr   : 人体识别AI程序
# @Software: PyCharm


import os
import platform
import subprocess


class AIParser:
    # 初始化
    def __init__(self, ai_program_path):
        self.ai_program_path = ai_program_path

    # 切换工作目录
    def switch_ai_dir(self):
        # 切换AI程序目录
        if platform.system() == 'Windows':
            os.chdir(self.ai_program_path)
        else:
            os.system(self.ai_program_path)

    # 识别图片的身体25个点并输出json
    def parse_image_part(self, origin_image_path, render_image_path, json_data_path):
        self.switch_ai_dir()
        get_result_image_cmd = "OpenPose --image_dir {} --write_images {} --write_images_format jpg --write_json {} --display 0".format(
            origin_image_path,
            render_image_path, json_data_path)
        print("-----开始识别图片-----")
        print(get_result_image_cmd)
        r_v = os.system(get_result_image_cmd)
        print(r_v)
        if r_v == 0:
            print("图片识别提取成功")
        else:
            print("图片识别提取失败")
        return r_v

    # 只识别图片的身体25个点
    def parse_imag_part2(self, origin_image_path, render_image_path):
        self.switch_ai_dir()
        get_result_image_cmd = "OpenPose --image_dir {} --write_images {} --write_images_format jpg --display 0".format(
            origin_image_path,
            render_image_path)
        print("-----开始识别图片-----")
        print(get_result_image_cmd)
        r_v = os.system(get_result_image_cmd)
        print(r_v)
        if r_v == 0:
            print("图片识别提取成功")
        else:
            print("图片识别提取失败")
        return r_v

    # 只输出识别身体25个点json
    def parse_image_part3(self, origin_image_path, json_data_path):
        self.switch_ai_dir()
        get_result_image_cmd = "OpenPose --image_dir {} --write_json {} --display 0 --render_pose 0".format(
            origin_image_path,
            json_data_path)
        print("-----开始识别图片-----")
        print(get_result_image_cmd)
        r_v = os.system(get_result_image_cmd)
        print(r_v)
        if r_v == 0:
            print("图片识别提取成功")
        else:
            print("图片识别提取失败")
        return r_v

    # # 识别图片的脸部并输出json
    def parse_image_face(self, origin_image_path, render_image_path, json_data_path):
        self.switch_ai_dir()
        get_result_image_cmd = "OpenPose --image_dir {} --face --write_images {} --write_images_format jpg --write_json {} –net_resolution 320x176 --display 0".format(
            origin_image_path,
            render_image_path, json_data_path)
        print("-----开始识别图片-----")
        print(get_result_image_cmd)
        # r_v = os.system(get_result_image_cmd)
        r_v = subprocess.Popen(get_result_image_cmd, shell=True)
        print(r_v)
        if r_v == 0:
            print("图片识别提取成功")
        else:
            print("图片识别提取失败")
        return r_v

    # 识别图片的手部并输出
    def parse_image_hand(self, origin_image_path, render_image_path, json_data_path):
        self.switch_ai_dir()
        get_result_image_cmd = "OpenPose --image_dir {} --hand --write_images {} --write_images_format jpg --write_json {} --display 0".format(
            origin_image_path,
            render_image_path)
        print("-----开始识别图片-----")
        print(get_result_image_cmd)
        r_v = os.system(get_result_image_cmd)
        print(r_v)
        if r_v == 0:
            print("图片识别提取成功")
        else:
            print("图片识别提取失败")
        return r_v

    # 识别视频
    def parse_video(self):
        pass

    # 识别网络摄像头
    def parse_webcam(self):
        pass

    # 设置标注框的样式（包括字体大小，长度、宽度等），根据输入图片的大小自动计算
    def get_label_box_style(self, origin_image_width):
        # 标注字体大小
        label_font_size = round(origin_image_width / 1200 * 20)
        # 标注框的X最小值
        label_polygon_left_x = round(origin_image_width / 1200 * 5)
        # 标注框的X最大值
        label_polygon_right_x = round(origin_image_width / 1200 * 425)
        # 标注框的Y最大值
        label_polygon_top_y = round(origin_image_width / 1200 * 5)
        # 标注框的Y最小值
        label_polygon_bottom_y = round(origin_image_width / 1200 * 402)
        # 左侧或右侧标注框的高度差值
        label_size_offset = round(origin_image_width / 1200 * 280)
        # 垂直绘制红线的长度
        vertical_red_line_length = round(origin_image_width / 1200 * 1000)
        # 身体绘制的圆圈的半径
        label_body_circle_radius = round(
            origin_image_width / 1200 * 6)
        # 身体绘制的圆圈的线宽
        label_body_circle_line = round(
            origin_image_width / 1200 * 3)
        # 脸部绘制的圆圈的半径
        label_face_circle_radius = round(
            origin_image_width / 350 * 4)
        # 脸部绘制的圆圈的线宽
        label_face_circle_line = round(
            origin_image_width / 350 * 2)
        style_obj = {
            "label_font_size": label_font_size,
            "label_polygon_left_x": label_polygon_left_x,
            "label_polygon_top_y": label_polygon_top_y,
            "label_polygon_right_x": label_polygon_right_x,
            "label_polygon_bottom_y": label_polygon_bottom_y,
            "label_size_offset": label_size_offset,
            "vertical_red_line_length": vertical_red_line_length,
            "label_body_circle_radius": label_body_circle_radius,
            "label_body_circle_line": label_body_circle_line,
            "label_face_circle_radius": label_face_circle_radius,
            "label_face_circle_line": label_face_circle_line
        }
        return style_obj
