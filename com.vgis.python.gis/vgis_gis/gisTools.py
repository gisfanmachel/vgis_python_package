#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2022/10/28 18:56
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : gisTools.py
# @Descr   : 
# @Software: PyCharm

# !/usr/bin/python3.9
# -*- coding: utf-8 -*-
"""
    地理中经常使用的数学计算，把地球简化成了一个标准球形，若是想要推广到任意星球能够改为类的写法，而后修改半径便可
"""
import math
import re

import numpy as np
from osgeo import gdal
from osgeo import osr
from pyproj import Proj, transform
from pyproj import Transformer
from shapely.geometry import Polygon


class GISHelper:
    earth_radius = 6370.856  # 地球平均半径，单位km，最简单的模型每每把地球当作完美的球形，这个值就是常说的RE
    math_2pi = math.pi * 2
    pis_per_degree = math_2pi / 360  # 角度一度所对应的弧度数，360对应2*pi

    def __init__(self):
        pass

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

    # 纬度差对应的KM
    def lat_degree2km(self, dif_degree, radius=earth_radius):
        """
        经过圆环求法，纯纬度上，度数差转距离(km)，与中间点所处的地球上的位置关系不大
        :param dif_degree: 度数差, 经验值0.0001对应11.1米的距离
        :param radius: 圆环求法的等效半径，纬度距离的等效圆环是经线环，因此默认都是earth_radius
        :return: 这个度数差dif_degree对应的距离，单位km
        """
        return radius * dif_degree * self.pis_per_degree

    # KM对应的纬度差
    def lat_km2degree(self, dis_km, radius=earth_radius):
        """
        经过圆环求法，纯纬度上，距离值转度数(diff)，与中间点所处的地球上的位置关系不大
        :param dis_km: 输入的距离，单位km，经验值111km相差约(接近)1度
        :param radius: 圆环求法的等效半径，纬度距离的等效圆环是经线环，因此默认都是earth_radius
        :return: 这个距离dis_km对应在纯纬度上差多少度
        """
        return dis_km / radius / self.pis_per_degree

    # 经度差对应的KM，需要提供中央纬度
    def lng_degree2km(self, dif_degree, center_lat):
        """
        经过圆环求法，纯经度上，度数差转距离(km)，纬度的高低会影响距离对应的经度角度差，具体表达式为：
        :param dif_degree: 度数差
        :param center_lat: 中心点的纬度，默认22为深圳附近的纬度值；为0时表示赤道，赤道的纬线环半径使得经度计算和上面的纬度计算基本一致
        :return: 这个度数差dif_degree对应的距离，单位km
        """
        # 修正后，中心点所在纬度的地表圆环半径
        real_radius = self.earth_radius * math.cos(center_lat * self.pis_per_degree)
        return self.lat_degree2km(dif_degree, real_radius)

    # KM对应的经度差，需要提供中央纬度
    def lng_km2degree(self, dis_km, center_lat):
        """
        纯经度上，距离值转角度差(diff)，单位度数。
        :param dis_km: 输入的距离，单位km
        :param center_lat: 中心点的纬度，默认22为深圳附近的纬度值；为0时表示赤道。
             赤道、中国深圳、中国北京、对应的修正系数分别约为： 1  0.927  0.766
        :return: 这个距离dis_km对应在纯经度上差多少度
        """
        # 修正后，中心点所在纬度的地表圆环半径
        real_radius = self.earth_radius * math.cos(center_lat * self.pis_per_degree)
        return self.lat_km2degree(dis_km, real_radius)

    # 两点（经纬度）之间的KM
    def ab_distance(self, a_lat, a_lng, b_lat, b_lng):
        """
        计算经纬度表示的ab两点的距离，这是种近似计算，当两点纬度差距不大时更为准确，产生近似的缘由也是来主要自于center_lat
        :param a_lat: a点纬度
        :param a_lng: a点经度
        :param b_lat: b点纬度
        :param b_lng: b点纬度
        :return:
        """
        center_lat = .5 * a_lat + .5 * b_lat
        lat_dis = self.lat_degree2km(abs(a_lat - b_lat))
        lng_dis = self.lng_degree2km(abs(a_lng - b_lng), center_lat)
        return math.sqrt(lat_dis ** 2 + lng_dis ** 2)

    # 构建矩形
    def get_rect_by_coords(self, coords):
        square = Polygon(
            ((coords[0], coords[2]), (coords[0], coords[3]), (coords[1], coords[3]), (coords[1], coords[2])))
        return square

    # 判断两个多边形是否相交
    # shaplely方法
    def is_overlap_of_polygons(self, poly1, poly2):
        return poly1.intersects(poly2) and not poly1.crosses(poly2) and not poly1.contains(poly2)

    # 通过经纬度得到像素坐标,根据地图高度宽度及地图经纬度范围
    def get_pixel_by_lnglat(self, point_x: float, point_y: float, map_boundary: str, map_witdh: int,
                            map_height: int) -> str:
        minx = float(map_boundary.split(",")[0])
        miny = float(map_boundary.split(",")[1])
        maxx = float(map_boundary.split(",")[2])
        maxy = float(map_boundary.split(",")[3])
        # 通过地图长宽和经纬度坐标获取像素坐标
        pixel_x = map_witdh / (maxx - minx) * (point_x - minx)
        pixel_y = map_height / (maxy - miny) * (maxy - point_y)
        return round(pixel_x), round(pixel_y)

    # 通过中心点坐标(经纬度)，图片宽度，图片高度，分辨率得到图片四个点坐标
    def get_box_by_center(self, data_centerpt: str, data_resolution: float, data_image_width: int,
                          data_image_height: int) -> str:

        data_minx = float(data_centerpt.split(",")[0]) - self.lng_km2degree(
            float(data_image_width) / 2 * float(data_resolution) / 1000, float(data_centerpt.split(",")[1]))
        data_maxx = float(data_centerpt.split(",")[0]) + self.lng_km2degree(
            float(data_image_width) / 2 * float(data_resolution) / 1000, float(data_centerpt.split(",")[1]))
        data_miny = float(data_centerpt.split(",")[1]) - self.lat_km2degree(
            float(data_image_height) / 2 * float(data_resolution) / 1000, 6370.856)
        data_maxy = float(data_centerpt.split(",")[1]) + self.lat_km2degree(
            float(data_image_height) / 2 * float(data_resolution) / 1000, 6370.856)
        return data_minx, data_maxx, data_miny, data_maxy

    # 转换坐标根据epsg
    @staticmethod
    def convert_points_from_epsg(point_list, from_epsg, to_epsg):
        from_prj = Proj(init='epsg:{}'.format(from_epsg))
        to_proj = Proj(init='epsg:{}'.format(to_epsg))
        new_point_list = []
        for point in point_list:
            x = point[0]
            y = point[1]
            x2, y2 = transform(from_prj, to_proj, x, y)
            new_point_list.append([x2, y2])
        return new_point_list

    # 4326坐标转3857坐标
    # point [[123.5,23.6]]
    @staticmethod
    def convert_point_from_wgs84_to_mercator(point):
        return_point = None
        # 地球半径
        earthRad = 6378137.0
        lng = point[0] * math.pi / 180 * earthRad
        param = point[1] * math.pi / 180
        lat = earthRad / 2 * math.log((1.0 + math.sin(param)) / (1.0 - math.sin(param)))
        return_point = [lng, lat]
        return return_point

    # 4326坐标转3857坐标
    # point [[350388,3957319.5]]
    @staticmethod
    def convert_point_from_mercator_to_wgs84(point):
        return_point = None
        lng = point[0] / 20037508.34 * 180
        lat = point[1] / 20037508.34 * 180
        lat = 180 / math.pi * (2 * math.atan(math.exp(lat * math.pi / 180)) - math.pi / 2)
        return_point = [lng, lat]
        return return_point

    # 投影坐标(米)到地理坐标（度）
    # proj_wkt： gdalinfo -json **.tif 得到json["coordinateSystem"]["wkt"]
    def convert_point_from_proj_to_geo(self, proj_wkt, x, y):
        # 地理坐标系是球面,投影坐标系是平面;
        # 地理坐标系的单位为“度”,投影坐标系的单位为“米”;
        prosrs = osr.SpatialReference()
        prosrs.ImportFromWkt(proj_wkt)
        geosrs = prosrs.CloneGeogCS()
        ct = osr.CoordinateTransformation(prosrs, geosrs)
        coords = ct.TransformPoint(x, y)
        # # 逆变换,实现投影到地理
        # p = Proj(projection)
        # lon, lat = p(x, y, inverse=True)
        return coords[:2][0], coords[:2][1]

    # 地理坐标（度）到投影坐标（米）
    # 输入的是要转的投影坐标系和经纬度
    def convert_point_from_geo_to_proj(self, proj_wkt, lon, lat):
        prosrs = osr.SpatialReference()
        prosrs.ImportFromWkt(proj_wkt)
        geosrs = prosrs.CloneGeogCS()
        ct = osr.CoordinateTransformation(geosrs, prosrs)
        coords = ct.TransformPoint(lon, lat)
        return coords[:2][0], coords[:2][1]

    # 投影坐标（米）到投影坐标（米）
    def convert_point_from_proj_to_proj(self, proj_wkt_source, proj_wkt_target, x, y):
        pass
        prosrs_source = osr.SpatialReference()
        prosrs_source.ImportFromWkt(proj_wkt_source)
        prosrs_target = osr.SpatialReference()
        prosrs_target.ImportFromWkt(proj_wkt_target)
        ct = osr.CoordinateTransformation(prosrs_source, prosrs_target)
        coords = ct.TransformPoint(x, y)
        return coords[:2][0], coords[:2][1]

    # 坐标转换（从一个坐标系到另一个坐标系），多个点
    # points:[[x1,y1],[x2,y2]....]
    # convert_method:proj_2_geo\geo_2_proj\proj_2_proj
    def convert_points_by_projwkt(self, points, proj_wkt, proj2_wkt, convert_method):
        try:
            point_list = []
            # 循环坐标点数组
            for point in points:
                x = point[0]
                y = point[1]
                if convert_method == "proj_2_geo":
                    x_convert, y_convert = self.convert_point_from_proj_to_geo(proj_wkt, x, y)
                if convert_method == "geo_2_proj":
                    x_convert, y_convert = self.convert_point_from_geo_to_proj(proj_wkt, x, y)
                if convert_method == "proj_2_proj":
                    x_convert, y_convert = self.convert_point_from_proj_to_proj(proj_wkt, proj2_wkt, x, y)

                point_list.append([x_convert, y_convert])

        except Exception as exp:
            print("坐标转换失败：" + str(exp))
            # 输出异常信息，错误行号等
            print(exp)
            print(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            print(exp.__traceback__.tb_lineno)  # 发生异常所在的行数

        return point_list

    # 针对WGS_1984_UTM_Zone_57N这种WGS84 UTM的分带投影做坐标转换
    # 从投影坐标米到地理坐标---单个点
    # point:[[350388,3957319.5]]
    # proj_wkt:"PROJCS[\"WGS 84 / UTM zone 54N\",GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4326\"]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",141],PARAMETER[\"scale_factor\",0.9996],PARAMETER[\"false_easting\",500000],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Easting\",EAST],AXIS[\"Northing\",NORTH],AUTHORITY[\"EPSG\",\"32654\"]]"
    def convert_point_from_utmproj_to_geo(self, point, proj_wkt, center_lon, center_lat):
        try:
            return_point = None
            point_x = point[0][0]
            point_y = point[0][1]
            proj_wkt = proj_wkt.upper()

            # 参数1：坐标系WKID WGS_1984_UTM_Zone_54N 对应 32654
            # 参数2：WGS84地理坐标系统 对应 4326
            # 如果是经纬度，就不用转
            if proj_wkt.strip().startswith("GEOGCS"):
                return_point = point
            else:
                proj = self.get_utm_from_proj(proj_wkt)
                epsg = self.get_utm_epsg_by_projection_info(proj, center_lon, center_lat)
                if epsg != -1:
                    print("转换前的espg:{}".format(epsg))
                    transformer = Transformer.from_crs("epsg:" + str(epsg), "epsg:4326")
                    lat, lon = transformer.transform(point_x, point_y)
                    return_point = [[lon, lat]]
                else:
                    print("坐标转换失败，通过投影没有获取到EPSG，请检查数据")
        except Exception as exp:
            print("坐标转换失败：" + str(exp))
            # 打印输出异常信息
            print(exp)
            print(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            print(exp.__traceback__.tb_lineno)  # 发生异常所在的行数

        return return_point

    # 转换坐标---从投影坐标米到地理坐标--多个点
    # points:[[350388,3957319.5],[352344,3966458.5]]
    # proj_wkt:"PROJCS[\"WGS 84 / UTM zone 54N\",GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4326\"]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",141],PARAMETER[\"scale_factor\",0.9996],PARAMETER[\"false_easting\",500000],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Easting\",EAST],AXIS[\"Northing\",NORTH],AUTHORITY[\"EPSG\",\"32654\"]]"
    def convert_points_from_utmproj_to_geo(self, points, proj_wkt, center_lon, center_lat):
        return_point_list = None
        try:
            res = ""
            # 参数1：坐标系WKID WGS_1984_UTM_Zone_54N 对应 32654
            # 参数2：WGS84地理坐标系统 对应 4326
            # 参数3: WGS84/UTM LJY,UTM无分带，强制对应为3857
            proj_wkt = proj_wkt.upper()
            print("投影信息：{}".format(proj_wkt))
            # 如果是经纬度，就不用转
            if proj_wkt.strip().startswith("GEOGCS"):
                return_point_list = points
            else:
                proj = self.get_utm_from_proj(proj_wkt)
                epsg = self.get_utm_epsg_by_projection_info(proj, center_lon, center_lat)
                print("转换前的espg:{}".format(epsg))
                transformer = Transformer.from_crs("epsg:" + str(epsg), "epsg:4326")
                point_list = []
                for point in points:
                    x = point[0]
                    y = point[1]
                    lat, lon = transformer.transform(x, y)
                    point_list.append([lon, lat])
                return_point_list = point_list
        except Exception as exp:
            print("坐标转换失败：" + str(exp))
            # 输出异常信息，错误行号等
            print(exp)
            print(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            print(exp.__traceback__.tb_lineno)  # 发生异常所在的行数
        return return_point_list

    # 针对WGS_1984_UTM_Zone_57N这种WGS84 UTM的分带投影做坐标转换
    # 地理坐标（经纬度）到投影坐标（米）--单个点
    def convert_point_from_geo_to_utmproj(self, point, proj_wkt, center_lon, center_lat):
        return_point = None
        try:
            lon = point[0][0]
            lat = point[0][1]
            proj_wkt = proj_wkt.upper()
            # 参数1：坐标系WKID WGS_1984_UTM_Zone_54N 对应 32654
            # 参数2：WGS84地理坐标系统 对应 4326
            # 投影1：PROJCS[\"WGS_1984_UTM_Zone_54N\",GEOGCS
            # 投影2：PROJCS[\"WGS 84 / UTM zone 54N\",GEOGCS
            proj = self.get_utm_from_proj(proj_wkt)
            epsg = self.get_utm_epsg_by_projection_info(proj, center_lon, center_lat)
            if epsg != -1:
                print("转换前的espg:{}".format(epsg))
                # 建立转换器
                transformer = Transformer.from_crs("epsg:4326", "epsg:" + str(epsg))
                # lat, lon = transformer.transform(point_x, point_y)
                point_x, point_y = transformer.transform(lat, lon)
                #             # 初始化4326和3857的pyproj投影对象
                #             p4326 = Proj(init='epsg:4326')  # WGS 84
                #             p3857 = Proj(init='epsg:3857')  # Web 墨卡托
                #             # 使用transform函数进行坐标转换
                #             tif_minx, tif_maxy= transform(p4326, p3857, tif_minx, tif_maxy)
                return_point = [[point_x, point_y]]
            else:
                print("坐标转换失败，通过投影没有获取到EPSG，请检查数据")
        except Exception as exp:
            print("坐标转换失败：" + str(exp))
            # 打印输出异常信息
            print(exp)
            print(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            print(exp.__traceback__.tb_lineno)  # 发生异常所在的行数

        return return_point

    # 转换坐标---地理坐标（经纬度）到投影坐标（米）---多个点
    # point:[[350388,3957319.5],[352344,3966458.5]]
    # proj_txt:"PROJCS[\"WGS 84 / UTM zone 54N\",GEOGCS[\"WGS 84\",DATUM[\"WGS_1984\",SPHEROID[\"WGS 84\",6378137,298.257223563,AUTHORITY[\"EPSG\",\"7030\"]],AUTHORITY[\"EPSG\",\"6326\"]],PRIMEM[\"Greenwich\",0,AUTHORITY[\"EPSG\",\"8901\"]],UNIT[\"degree\",0.0174532925199433,AUTHORITY[\"EPSG\",\"9122\"]],AUTHORITY[\"EPSG\",\"4326\"]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"latitude_of_origin\",0],PARAMETER[\"central_meridian\",141],PARAMETER[\"scale_factor\",0.9996],PARAMETER[\"false_easting\",500000],PARAMETER[\"false_northing\",0],UNIT[\"metre\",1,AUTHORITY[\"EPSG\",\"9001\"]],AXIS[\"Easting\",EAST],AXIS[\"Northing\",NORTH],AUTHORITY[\"EPSG\",\"32654\"]]"
    def convert_points_from_geo_to_utmproj(self, points, proj_wkt, center_lon, center_lat):
        return_point_list = None
        try:
            res = ""
            # 参数1：坐标系WKID WGS_1984_UTM_Zone_54N 对应 32654
            # 参数2：WGS84地理坐标系统 对应 4326
            proj_wkt = proj_wkt.upper()
            # 通过正则表达式得到坐标系
            # 投影1：PROJCS[\"WGS_1984_UTM_Zone_54N\",GEOGCS
            # 投影2：PROJCS[\"WGS 84 / UTM zone 54N\",GEOGCS
            proj = self.get_utm_from_proj(proj_wkt)
            epsg = self.get_utm_epsg_by_projection_info(proj, center_lon, center_lat)
            print("转换前的espg:{}".format(epsg))
            transformer = Transformer.from_crs("epsg:4326", "epsg:" + str(epsg))
            point_list = []
            # 循环坐标点数组
            for point in points:
                lon = point[0]
                lat = point[1]
                x, y = transformer.transform(lat, lon)
                point_list.append([x, y])
            return_point_list = point_list
        except Exception as exp:
            print("坐标转换失败：" + str(exp))
            # 输出异常信息，错误行号等
            print(exp)
            print(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            print(exp.__traceback__.tb_lineno)  # 发生异常所在的行数
        return return_point_list

    # 通过投影信息和中央经纬度得到EPSG
    def get_utm_epsg_by_projection_info(self, projection, center_lon, center_lat):
        epsg_code = -1
        try:
            print("转换前的proj:{}".format(projection))
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
            print("通过投影获取EPSG失败：" + str(exp))
            # epsg_code=3857
            print(exp)
            print(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            print(exp.__traceback__.tb_lineno)  # 发生异常所在的行数
        return int(epsg_code)

    # 计算多边形坐标的四至范围
    # 多边形坐标为[[point1x,point1y],[point2x,point2y],...[pointnx,pointny],[point1x,point1y]]
    @staticmethod
    def get_box_of_polygon_points(points):
        points_np = np.array(points)

        cols_min = np.min(points_np, axis=0)
        cols_max = np.max(points_np, axis=0)
        minx = cols_min[:1].tolist()[0]
        miny = cols_min[1:2].tolist()[0]
        maxx = cols_max[:1].tolist()[0]
        maxy = cols_max[1:2].tolist()[0]
        # minx = np.min(points_np[:, 0])
        # maxx = np.max(points_np[:, 0])
        # miny = np.min(points_np[:, 1])
        # maxy = np.max(points_np[:, 1])
        return minx, miny, maxx, maxy

    # 得到tif文件的投影信息
    def get_source_projection(self, tif_file):
        dataset = gdal.Open(tif_file)
        return dataset.GetProjection()

    @staticmethod
    def get_circle_polygons_by_center_and_radius( center, radius,num_points):
        """
        根据中心点和半径，生成圆形的多边形
        :param center: 中心点坐标，格式为[x,y]
        :param radius: 半径
        :return: 圆形的多边形
        """
        # 计算圆形的顶点坐标
        points = []
        for i in range(num_points + 1):
            angle = i * (360 / num_points)
            x = center[0] + (radius * math.cos(math.radians(angle)))
            y = center[1] + (radius * math.sin(math.radians(angle)))
            points.append([x, y])
        return points




if __name__ == '__main__':
    gisHelper = GISHelper()
    # print(gisHelper.lng_km2degree(0.5, 45))
    # dataset = gdal.Open("E:\\data\\123.tif")
    # print(dataset.GetProjection())
    # print(dataset.GetGeoTransform())

    print("---------------------------------")

    # dataset = gdal.Open("E:\\data\\sar1234\\1234.tiff")
    # print(dataset.GetProjection())
    # print(dataset.GetGeoTransform())

    # 得到原始tif的投影信息
    # source_projection = gisHelper.get_source_projection("E:\\data\\123.tif")
    # source_projection = gisHelper.get_source_projection("E:\\desktop\\DEM\\ribenxibu.tif")
    # # 输入原始tif的投影信息，需要转换的点的投影坐标（米）
    # result = gisHelper.convert_points_from_meter_to_lnglat(source_projection, 350388, 3957319.5)
    # # 输出 转换后的经纬度值（度）
    # print("lon:" + str(result[0]))
    # print("lat:" + str(result[1]))
    point = [113, 23]
    print(gisHelper.convert_point_from_wgs84_to_mercator(point))
    point = [12604705.942522367, 2632018.637586424]
    print(gisHelper.convert_point_from_mercator_to_wgs84(point))
