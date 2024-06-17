#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2022/10/28 18:56
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : gisTools.py
# @Descr   : 
# @Software: PyCharm


class ProjHelper:

    def __init__(self):
        pass

    @staticmethod
    def convertJgwToGadlTransform(jgwFilePath: str) -> str:
        """
        将世界投影文件jpw格式转为gdal的投影六参数数组
        jgw格式为：0.0000197051\n 0.0000000000\n 0.0000000000\n -0.0000197051\n 104.595572656171356\n 38.815550616869423\n
            #  A 表示影像数据与矢量数据在 X 方向的比例关系;X方向 每像素的精度值
            #  D 表示影像数据与矢量数据在 Y方向的比例关系, 但它为负值, 这是由于空间坐标系与影像数据的存储坐标系在 Y方向上相反, 要匹配, 必须将 E 设为负值;Y方向 每像素的精度值
            #  E、F 表示影像数据的左上角点的像元对应的空间坐标的 X、Y 坐标;
            #  B、C 表示影像数据的旋转参数, 但是在 MapObjects2. 0 中不支持影像数据的旋转, 因此 这两个参数的数值是被忽略的, 缺省记录为 0。
        gdal transform格式为[114.0, 0.000001, 0, 34.0, 0, -0.000001]
            # 左上角点坐标X
            # x方向的分辨
            # 旋转系数，如果为0，就是标准的正北向图像
            # 左上角点坐标Y
            # 旋转系数，如果为0，就是标准的正北向图像
            # Y方向的分辨率

        :param jgwFilePath: 世界投影文件路径
        :return: gdal的几何投影六参数数组
        """
        f = open(jgwFilePath)
        line = f.readline()
        row = 0
        while line:
            row += 1
            if row == 1:
                x_scale_value = line.rstrip("\n")
            if row == 2:
                x_rotate_value = line.rstrip("\n")
            if row == 3:
                y_rotate_value = line.rstrip("\n")
            if row == 4:
                y_scale_value = line.rstrip("\n")
            if row == 5:
                x_leftupper_value = line.rstrip("\n")
            if row == 6:
                y_leftupper_value = line.rstrip("\n")
            line = f.readline()
        f.close()
        gdal_transform = [float(x_leftupper_value), float(x_scale_value), float(x_rotate_value),
                          float(y_leftupper_value), float(y_rotate_value),
                          float(y_scale_value)]
        return gdal_transform
