#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/6/12 12:08
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : tifTools.py
# @Descr   : gadl,rastrio等库处理tif数据
# @Software: PyCharm
from PIL import Image
from osgeo import gdal


class TifFileOperator:
    # 初始化
    def __init__(self):
        pass

    @staticmethod
    # 写入tiff
    def create_tiff(save_path_tif, rows, clos, src_proj, src_transform, img_change):
        Driver = gdal.GetDriverByName('GTiff')
        out_img = Driver.Create(save_path_tif, rows, clos, 1, gdal.GDT_Byte)
        out_img.SetProjection(src_proj)  # 投影信息
        out_img.SetGeoTransform(src_transform)  # 仿射信息
        out_img.GetRasterBand(1).WriteArray(img_change)  # 写入数值

    @staticmethod
    # 读取tiff
    def read_tiff(input_file):
        """
        读取影像
        :param input_file:输入影像
        :return:波段数据，仿射变换参数，投影信息、行数、列数、波段数
        """
        dataset = gdal.Open(input_file)
        rows = dataset.RasterYSize
        cols = dataset.RasterXSize

        geo = dataset.GetGeoTransform()
        proj = dataset.GetProjection()

        couts = dataset.RasterCount

        # # 行列数过大，会报内存出错
        # array_data = np.zeros((couts, rows, cols))
        # for i in range(couts):
        #     band = dataset.GetRasterBand(i + 1)
        #     array_data[i, :, :] = band.ReadAsArray()

        band = dataset.GetRasterBand(1)
        im_datas = band.ReadAsArray(0, 0, cols, rows)

        return im_datas, geo, proj, rows, cols, couts

    @staticmethod
    # 计算tif图像的每个像素对应的经纬度值
    def get_priexl_px_degree(tif_path):
        img_m = Image.open(tif_path)
        tif_width = img_m.width  # 图片的宽
        tif_height = img_m.height  # 图片的高
        gdal.AllRegister()
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        dataset = gdal.Open(tif_path)
        xsize = dataset.RasterXSize
        ysize = dataset.RasterYSize
        adfGeoTransform = dataset.GetGeoTransform()
        # 左上角地理坐标
        left_lon = adfGeoTransform[0]
        top_lat = adfGeoTransform[3]
        right_lon = adfGeoTransform[0] + xsize * adfGeoTransform[1] + ysize * adfGeoTransform[2]
        bottom_lat = adfGeoTransform[3] + xsize * adfGeoTransform[4] + ysize * adfGeoTransform[5]
        pre_px_degree = (right_lon - left_lon) / tif_width
        return pre_px_degree, left_lon, top_lat

    @staticmethod
    # 获取tif坐标系
    def getCoordsInfoOfTif(tifFilePath):
        print(tifFilePath)
        # 为了支持中文路径，请添加下面这句代码
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        ds = gdal.Open(tifFilePath, 0)
        # 得到坐标系信息
        src_wkt = ds.GetProjectionRef()
        coordNameArray = src_wkt.split("\"")
        coordName = coordNameArray[1]
        print("tif的坐标系名称：" + coordName)

    @staticmethod
    # 获取tif空间范围
    def get_env_of_tif(tif_path):
        dataset = gdal.Open(tif_path)  # 打开tif
        adfGeoTransform = dataset.GetGeoTransform()  # 读取tif的六参数
        iXSize = dataset.RasterXSize  # 列数
        iYSize = dataset.RasterYSize  # 行数
        # 左上角
        tif_minx = adfGeoTransform[0]
        tif_maxy = adfGeoTransform[3]
        # 右下角
        tif_maxx = adfGeoTransform[0] + iXSize * adfGeoTransform[1] + iYSize * adfGeoTransform[2]
        tif_miny = adfGeoTransform[3] + iXSize * adfGeoTransform[4] + iYSize * adfGeoTransform[5]
        return tif_minx, tif_miny, tif_maxx, tif_maxy
