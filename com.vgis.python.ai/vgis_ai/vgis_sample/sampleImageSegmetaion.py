#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/7/4 14:10
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    :
# @Descr   : 样本图片裁切
# @Software: PyChar
import math
import os
from os import path
import cv2
import numpy as np


class SegmenationImageHelper:
    def __init__(self):
        pass

    # 裁剪大图到小图，按照crop_width, crop_height尺寸，按照尺寸进行外扩填充
    @staticmethod
    def seg_img_by_size_with_padding(input_img_file_path, crop_width, crop_height, crop_img_save_path, crop_file_prefix,
                                     file_ext):

        def __crop_image(img, crop_width, crop_height):
            # m是图像height，行数，y方向
            # n是图像width，列数，X方向
            m, n = img.shape[0], img.shape[1]

            # a1 是 裁剪的行数（边缘不够尺寸的也要裁剪算行数），Y方向
            a1 = (m // crop_height) + 1
            # b1 是 裁剪的列数（边缘不够尺寸的也要裁剪算列数），X方向
            b1 = (n // crop_width) + 1

            # a 是 Y 方向不够的像素
            a = a1 * crop_height - m
            # b 是 X 方向不够的像素
            b = b1 * crop_width - n

            # 将原影像填充,满足（crop_width,crop_height）的倍数，填充部分为黑色
            # 原来的Y 为13659 ，现在变成了13824，增加了a=165
            # 原来的X 为15632，现在变成了15772，增加了b=240
            img_padding = cv2.copyMakeBorder(img, 0, a, 0, b, cv2.BORDER_CONSTANT, value=(0, 0, 0))

            img_crops = []
            # Y方向
            for i in range(a1):
                # X 方向
                for j in range(b1):
                    img_c = img_padding[i * crop_height:(i + 1) * crop_height, j * crop_width:(j + 1) * crop_width]
                    img_crops.append(img_c)
            return img_crops

        # img_input = cv2.imread(input_img_file_path, 1)
        img_input = cv2.imdecode(np.fromfile(input_img_file_path, dtype=np.uint8), 1)

        img_input_segs = __crop_image(img_input, crop_width, crop_height)

        for j in range(len(img_input_segs)):
            output_file = path.join(crop_img_save_path, crop_file_prefix + '_' + str(j) + '.' + file_ext)
            # cv2.imwrite(output_file, img_input_segs[j])
            cv2.imencode("." + file_ext, img_input_segs[j])[1].tofile(output_file)
            print("生成裁剪文件:{}".format(output_file))

        print("裁剪{}*{}已保存".format(crop_width, crop_height))

    # 裁剪大图到小图，按照crop_width, crop_height尺寸，不足尺寸的保留大小
    @staticmethod
    def seg_img_by_size_with_remain(input_image_path: str, output_folder: str, crop_file_prefix: str, file_ext: str,
                                    crop_size: tuple,
                                    ) -> None:
        """
        按照制定尺寸裁切大图，如果小图不够尺寸，保留小图自己的尺寸

        @param input_image_path: 大图路径
        @param output_folder: 裁切小图所在目录，按照规定要求命令，比cropped_0.jpg,cropped_1.jpg,...cropped_n.jpg,其中n为裁切的序号
        @param crop_file_prefix:裁切图片名的前缀，比如cropped
        @param file_ext: 裁切图片的后缀
        @param crop_size: 裁切尺寸，格式为：(height,width)
        """
        print("进入大图裁剪")

        # 读取大图片
        # img = cv2.imread(input_image_path, 1)
        img = cv2.imdecode(np.fromfile(input_image_path, dtype=np.uint8), 1)

        # 图像height，行数，y方向
        # 图像width，列数，X方向
        height, width = img.shape[0], img.shape[1]
        crop_height = crop_size[0]
        crop_width = crop_size[1]

        if height <= crop_height and width <= crop_width:
            pass
        else:
            # 裁剪的行数（边缘不够尺寸的也要裁剪算行数），Y方向
            rows = math.ceil(float(height) / crop_height)
            # rows = (height // crop_height) + 1
            # 裁剪的列数（边缘不够尺寸的也要裁剪算列数），X方向
            cols = math.ceil(float(width) / crop_width)
            # cols = (width // crop_width) + 1

            # Y 方向填充的像素
            y_padd = rows * crop_height - height
            # X 方向填充的像素
            x_padd = cols * crop_width - width

            # 将原影像填充,满足裁切尺寸的倍数，填充部分为黑色
            # 原来的Y 为13659 ，现在变成了13824，增加了y_padd=165
            # 原来的X 为15632，现在变成了15772，增加了x_padd=240
            img_padding = cv2.copyMakeBorder(img, 0, y_padd, 0, x_padd, cv2.BORDER_CONSTANT, value=(0, 0, 0))

            img_crops = []
            # Y方向,循环行
            for i in range(rows):
                # X 方向,循环列
                for j in range(cols):
                    start_y = i * crop_height
                    end_y = (i + 1) * crop_height
                    start_x = j * crop_width
                    end_x = (j + 1) * crop_width
                    # 最下面的 需要去掉Y方向扩充
                    if i == rows - 1 and y_padd != 0:
                        end_y = i * crop_height + (crop_height - y_padd)
                    # 最右边的，需要去掉X方向扩展
                    if j == cols - 1 and x_padd != 0:
                        end_x = j * crop_width + (crop_width - x_padd)
                    img_c = img_padding[start_y:end_y, start_x:end_x]
                    img_crops.append(img_c)
                    # cv2.imwrite(os.path.join(output_folder, 'cropped_{}_{}.jpg'.format(i, j)), img_c)
            for t in range(len(img_crops)):
                output_file = output_folder + "/{}_{}.{}".format(crop_file_prefix, t, file_ext)
                # output_file = os.path.join(output_folder, '{}_{}.{}'.format(crop_file_prefix, t, file_ext))
                # cv2.imwrite(output_file, img_crops[t])
                cv2.imencode("." + file_ext, img_crops[t])[1].tofile(output_file)
                print("生成裁剪文件:{}".format(output_file))
            print("裁剪{}*{}已保存".format(crop_width, crop_height))

    # 将裁切后小图拼接成大图
    @staticmethod
    def concatenate_seg_images_by_size_with_remain(input_folder: str, output_image_path: str, big_image_shape: tuple,
                                                   crop_file_prefix: str, file_ext: str,
                                                   crop_size: tuple, ) -> None:
        """
        将裁切后的小图拼成大图

        @param input_folder: 裁切小图所在目录，按照规定要求命令，如cropped_0.jpg,cropped_1.jpg,...cropped_n.jpg,其中n为裁切的序号
        @param output_image_path: 拼接后的图片路径
        @param big_image_shape: 原大图尺寸，格式为： (height,width,bands)
        @param crop_file_prefix: 裁切图片名的前缀,如 cropped
        @param file_ext: 裁切图片的后缀
        @param crop_size: 裁切尺寸，格式为：(height,width)
        """

        print("进入裁剪小图拼接大图")
        # 计算裁剪后的行数和列数
        crop_height = crop_size[0]
        crop_width = crop_size[1]
        height, width = big_image_shape
        # 裁剪的行数（边缘不够尺寸的也要裁剪算行数），Y方向
        rows = (height // crop_height) + 1
        # 裁剪的列数（边缘不够尺寸的也要裁剪算列数），X方向
        cols = (width // crop_width) + 1

        # Y 方向填充的像素
        y_padd = rows * crop_height - height
        # X 方向填充的像素
        x_padd = cols * crop_width - width

        # 创建大图的空白画布
        output_img = np.zeros((height, width, 3), dtype=np.uint8)

        # Y方向
        for i in range(rows):
            # X方向
            for j in range(cols):
                #  cols是裁剪的列数，cols * i + j 表示第几个裁剪的图片提取的变化二值图（将所有裁剪图片拉平）
                cropped_image_path = os.path.join(input_folder,
                                                  '{}_'.format(crop_file_prefix) + str(
                                                      cols * i + j) + '.' + file_ext)
                # cropped_image = cv2.imread(cropped_image_path, 1)
                cropped_image = cv2.imdecode(np.fromfile(cropped_image_path, dtype=np.uint8), 1)

                start_y = i * crop_height
                end_y = (i + 1) * crop_height
                start_x = j * crop_width
                end_x = (j + 1) * crop_width
                # 最下面的 需要去掉Y方向扩充
                if i == rows - 1 and y_padd != 0:
                    end_y = i * crop_height + (crop_height - y_padd)
                # 最右边的，需要去掉X方向扩展
                if j == cols - 1 and x_padd != 0:
                    end_x = j * crop_width + (crop_width - x_padd)
                output_img[start_y:end_y, start_x:end_x] = cropped_image

        # 保存拼接后的大图
        # cv2.imwrite(output_image_path, output_img)
        cv2.imencode("." + file_ext, output_img)[1].tofile(output_image_path)
        print("拼接大图完成")


if __name__ == "__main__":
    input_img_file_path = "E:/系统开发/AI/luojianet-master/model_zoo/rs_change_detection/Building_CD_v2/CD_data/Building change detection dataset_add/1. The two-period image data/change_label/train/change_label.tif"
    crop_width = 512
    crop_height = 512
    crop_img_save_path = "E:/系统开发/AI/luojianet-master/model_zoo/rs_change_detection/Building_CD_v2/CD_data/Building change detection dataset_add/1. The two-period image data/change_label/train/splitt_images"
    crop_file_prefix = "0"
    file_ext = "tif"
    # 方法1裁切
    # SegmenationImageHelper.seg_img_by_size_with_padding(input_img_file_path, crop_width, crop_height,
    #                                                     crop_img_save_path, file_ext)

    crop_size = (crop_height, crop_width)

    # 方法2裁切
    crop_img_save_path = "E:/系统开发/AI/luojianet-master/model_zoo/rs_change_detection/Building_CD_v2/CD_data/Building change detection dataset_add/1. The two-period image data/change_label/train/spllitt_images2"
    # SegmenationImageHelper.seg_img_by_size_with_remain(input_img_file_path, crop_img_save_path, crop_file_prefix,file_ext,crop_size)

    concatenate_seg_images_save_path = "E:/系统开发/AI/luojianet-master/model_zoo/rs_change_detection/Building_CD_v2/CD_data/Building change detection dataset_add/1. The two-period image data/change_label/train/merge_image2/result.jpg"

    big_image_shape = cv2.imdecode(np.fromfile(input_img_file_path, dtype=np.uint8), -1).shape
    SegmenationImageHelper.concatenate_seg_images_by_size_with_remain(crop_img_save_path,
                                                                      concatenate_seg_images_save_path, big_image_shape,
                                                                      crop_file_prefix, file_ext, crop_size)
