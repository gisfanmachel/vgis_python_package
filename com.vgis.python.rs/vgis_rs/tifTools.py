#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/6/12 12:08
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : tifTools.py
# @Descr   : gadl,rastrio等库处理tif数据
# @Software: PyCharm
import json
import re
import subprocess
from pyproj import Transformer
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

    @staticmethod
    # 从投影信息获取UTM信息
    def get_utm_from_proj(self, proj_txt):
        # 适配不同的标识符
        # JB卫星: PROJCS[\"WGS_1984_UTM_Zone_54N\",GEOGCS
        # GJ卫星: PROJCRS[\"WGS 84 \ UTM zone 17N\",BASEGEOGCRS
        if proj_txt.strip().startswith("PROJCS"):
            proj = re.findall("PROJCS(.*?)GEOGCS", proj_txt)[0].lstrip("[")[:-1]
        elif proj_txt.strip().startswith("PROJCRS"):
            proj = re.findall("PROJCRS(.*?)BASEGEOGCRS", proj_txt)[0].lstrip("[")[:-1]
        return proj

    @staticmethod
    # 通过投影信息得到EPSG
    def get_utm_epsg(self, projection, center_lon, center_lat):
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

        # 获取投影信息
        # 构建命令
        command = ['gdalinfo', '-json', tif_path]
        # 执行命令并获取输出
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)
        result_str = result.decode('utf-8')
        # "{description"+str(result).lstrip("b").split("description")[-1].replace("\\r\\n","").replace("\\"","\"").replace("\\n","")+"}"
        # 解析JSON字符串
        info_dict = json.loads(result_str)
        proj_wkt = info_dict['coordinateSystem']['wkt']

        # 获取波段数
        band_count = dataset.RasterCount

        # 获取每个带的位深度
        depth = None
        depths = []
        for i in range(band_count):
            band = dataset.GetRasterBand(i + 1)
            metadata_item = band.GetMetadataItem('GDAL_DATA', 'TIFF')
            if metadata_item:
                depth = int(metadata_item.split('=')[-1])
                depths.append(depth)
        # 如果所有带的位深度一致，则返回它，否则返回None
        if len(set(depths)) == 1:
            depth = depths[0]

        # 地理坐标，经纬度
        # 转换为米，进行面积计算和分辨率计算
        resolution = None
        area = None
        if proj_wkt.strip().startswith("GEOGCS"):
            # 针对UTM分带的处理
            if proj_wkt.find("utm") != -1 or proj_wkt.find("UTM") != -1:
                center_lon = (tif_maxx - tif_minx) / 2
                center_lat = (tif_maxy - tif_miny) / 2
                proj = TifFileOperator.get_utm_from_proj(proj_wkt)
                epsg = TifFileOperator.get_utm_epsg(proj, center_lon, center_lat)
                print("转换前的espg:{}".format(epsg))
                transformer = Transformer.from_crs("epsg:4326", "epsg:" + str(epsg))
                tif_minx, tif_maxy = transformer.transform(tif_minx, tif_maxy)
                tif_maxx, tif_miny = transformer.transform(tif_minx, tif_maxy)
            # 其他标准的投影，如4326等
            else:
                prosrs = osr.SpatialReference()
                prosrs.ImportFromWkt(proj_wkt)
                geosrs = prosrs.CloneGeogCS()
                ct = osr.CoordinateTransformation(geosrs, prosrs)
                coords = ct.TransformPoint(tif_minx, tif_maxy)
                tifminx, tif_maxy = coords[:2][0], coords[:2][1]
                coords = ct.TransformPoint(tif_maxx, tif_miny)
                tif_maxx, tif_miny = coords[:2][0], coords[:2][1]
        # 投影坐标，米
        elif proj_wkt.strip().startswith("PROJCRS"):
            pass
        resolution = (tif_maxx - tifminx) / cols
        area = (tif_maxx - tifminx) * (tif_maxy - tif_miny)

        return rows, cols, band_count, depth, resolution, area, (
            tif_minx, tif_maxy, tif_maxx, tif_miny), proj_wkt

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
    tif_path = "c:/data/TW2015_3857.tif"
    print(TifFileOperator.get_all_meta_of_tif(tif_path))
