#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/6/12 12:08
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : tifTools.py
# @Descr   : gadl,rastrio等库处理tif数据
# @Software: PyCharm
import json
import platform
import re
import subprocess
from pyproj import Transformer, CRS, Proj, transform
from PIL import Image
from osgeo import gdal, osr


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

        epsg_code = -1
        try:
            self.logger.info("转换前的proj:{}".format(projection))
            utm_code = projection.replace(" ", "").replace("_", "").lower()
            # wgs84 utm分带投影的epsg计算
            if "utmzone" in utm_code and ("wgs84" in utm_code or "wgs1984" in utm_code):
                if len(re.findall("zone(.*?)n", utm_code)) > 0:
                    # 北半球 epsg=32600+wgs84 utm分度带号
                    utm_code_zone = int(re.findall("zone(.*?)n", utm_code)[0])
                    epsg_code = 32600 + utm_code_zone
                if len(re.findall("zone(.*?)s", utm_code)) > 0:
                    # 南半球 epsg=32700+wgs84 utm分度带号
                    utm_code_zone = int(re.findall("zone(.*?)s", utm_code)[0])
                    epsg_code = 32700 + utm_code_zone
            # utm没有分带投影的epsg计算
            elif "utm" in utm_code and "utmzone" not in utm_code:
                # 东半球
                if float(center_lon) > 0:
                    utm_code_zone = 31 + int(float(center_lon) / 6)
                # 西半球
                if float(center_lon) < 0:
                    utm_code_zone = 30 - int(abs(float(center_lon) / 6))
                # 北半球
                if float(center_lat) > 0:
                    epsg_code = 32600 + utm_code_zone
                # 南半球
                if float(center_lat) < 0:
                    epsg_code = 32700 + utm_code_zone

        except Exception as exp:
            self.logger.error("通过投影获取EPSG失败：" + str(exp))
            # epsg_code=3857
            self.logger.info(exp)
            self.logger.info(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            self.logger.info(exp.__traceback__.tb_lineno)  # 发生异常所在的行数
        return int(epsg_code)

    @staticmethod
    # 通过gdalinfo命令获取完整的project wkt信息
    def get_projection_by_gdalinfo(tif_path):
        # 执行cmd命令
        cmd = "gdalinfo -json {}".format(tif_path)
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 获取标准输出和错误信息
        stdout = result.stdout
        stderr = result.stderr

        # 打印输出结果
        # print(stdout)

        # 如果有错误信息，也打印它们
        if stderr:
            print("错误信息：" + stderr)
        info_dict = json.loads(stdout)
        proj_wkt = info_dict['coordinateSystem']['wkt']
        # 如果调用gdalinfo命令报错，
        # windows环境,在这里单元测试通过staticmethod方法会报这些错，但是普通方法不报错，如果打包好vgis-rs,在别的地方调用没问题
        # linux环境，不会出现这些问题
        # ERROR 1: PROJ: proj_create_from_database: C:\Program Files\gdal\bin\proj6\share\proj.db lacks DATABASE.LAYOUT.VERSION.MAJOR / DATABASE.LAYOUT.VERSION.MINOR metadata. It comes from another PROJ installation.
        # ERROR 1: PROJ: proj_create_from_database: C:\Program Files\gdal\bin\proj6\share\proj.db lacks DATABASE.LAYOUT.VERSION.MAJOR / DATABASE.LAYOUT.VERSION.MINOR metadata. It comes from another PROJ installation.
        # ERROR 1: PROJ: proj_get_ellipsoid: CRS has no geodetic CRS
        # ERROR 1: PROJ: proj_get_ellipsoid: Object is not a CRS or GeodeticReferenceFrame
        # 这个时候得到的projection是不完整的，开头：ENGCRS["WGS_1984_Web_Mercator_Auxiliary_Sphere",
        print(proj_wkt)
        return proj_wkt

    @staticmethod
    # 获取tif的投影信息、行数、列数、波段数、分辨率（米为单位）、面积（平方米）、空间范围（原始坐标）、
    def get_all_meta_of_tif(tif_path):
        dataset = gdal.Open(tif_path)
        rows = dataset.RasterYSize
        cols = dataset.RasterXSize
        adfGeoTransform = dataset.GetGeoTransform()  # 读取tif的六参数
        # 左上角
        tif_minx = adfGeoTransform[0]
        tif_maxy = adfGeoTransform[3]
        # 右下角
        tif_maxx = adfGeoTransform[0] + cols * adfGeoTransform[1] + rows * adfGeoTransform[2]
        tif_miny = adfGeoTransform[3] + cols * adfGeoTransform[4] + rows * adfGeoTransform[5]
        envelop = (tif_minx, tif_miny, tif_maxx, tif_maxy)

        # 获取投影信息
        proj_wkt = TifFileOperator.get_projection_by_gdalinfo(tif_path)

        # 获取波段数
        band_count = dataset.RasterCount

        # 获取每个带的位深度
        # 获取第一个波段
        band = dataset.GetRasterBand(1)

        # 获取数据类型的位深
        data_type = band.DataType
        bit_depth = gdal.GetDataTypeSize(data_type)


        # 地理坐标，经纬度
        # 转换为米，进行面积计算和分辨率计算
        resolution = None
        area = None
        if proj_wkt.strip().startswith("GEOGCS") or proj_wkt.strip().startswith("GEOGCRS"):
            # 初始化4326和3857的pyproj投影对象
            p4326 = Proj(init='epsg:4326')  # WGS 84
            p3857 = Proj(init='epsg:3857')  # Web 墨卡托
            # 使用transform函数进行坐标转换
            tif_minx, tif_maxy = transform(p4326, p3857, tif_minx, tif_maxy)
            tif_maxx, tif_miny = transform(p4326, p3857, tif_maxx, tif_miny)
        # 投影坐标，米
        elif proj_wkt.strip().startswith("PROJCRS"):
            pass
        resolution = (tif_maxx - tif_minx) / cols
        area = (tif_maxx - tif_minx) * (tif_maxy - tif_miny)

        return rows, cols, band_count, bit_depth, resolution, area, envelop, proj_wkt

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
        return coordName, coordNameArray

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


if __name__ == '__main__':
    sysstr = platform.system()
    if sysstr == "Windows":
        test_tif_path = "y:/data/test_images/TW2015_4326.TIF"
    elif sysstr == "Linux":
        test_tif_path = "/mnt/share/data/test_images/TW2015_4326.TIF"

    # cmd = "gdalinfo -json {}".format(test_tif_path)
    # result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #
    # # 获取标准输出和错误信息
    # stdout = result.stdout
    # stderr = result.stderr

    # 打印输出结果
    # print(stdout)

    # 如果有错误信息，也打印它们
    # if stderr:
    #     print("错误信息：" + stderr)
    # info_dict = json.loads(stdout)
    # proj_wkt = info_dict['coordinateSystem']['wkt']

    # print(proj_wkt)

    result_list = TifFileOperator.get_all_meta_of_tif(test_tif_path)
    for result in result_list:
        print(result)
