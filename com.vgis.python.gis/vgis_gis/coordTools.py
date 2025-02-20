"""
===================================
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Author: chenxw
@Email : gisfanmachel@gmail.com
@File: coordTools.py
@Date: Create in 2021/1/28 10:04
@Description: 坐标转换
（wgs84ll即GPS经纬度），2（gcj02ll即国测局经纬度坐标），3（bd09ll即百度经纬度坐标），4（bd09mc即百度米制坐标）
@ Software: PyCharm
===================================
"""

import math


class coordConverter:
    def __init__(self):
        self.x_pi = float(3.14159265358979324 * 3000.0 / 180.0)
        # //pai
        self.pi = float(3.1415926535897932384626)
        # //离心率
        self.ee = float(0.00669342162296594323)
        # //长半轴
        self.a = float(6378245.0)

    # //百度转国测局
    def bd09togcj02(self, bd_lon, bd_lat):
        x = (bd_lon - 0.0065)
        y = (bd_lat - 0.006)
        z = (math.sqrt(x * x + y * y)) - (0.00002 * math.sin(y * self.x_pi))
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * self.x_pi)
        gg_lng = z * math.cos(theta)
        gg_lat = z * math.sin(theta)

        return gg_lng, gg_lat

    # //国测局转百度
    def gcj02tobd09(self, lng, lat):
        z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * self.x_pi)
        theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * self.x_pi)
        bd_lng = z * math.cos(theta) + 0.0065
        bd_lat = z * math.sin(theta) + 0.006
        return bd_lng, bd_lat

    # //国测局转84
    def gcj02towgs84(self, lng, lat):
        dlat = self.transformlat(lng - 105.0, lat - 35.0)
        dlng = self.transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * self.pi
        magic = math.sin(radlat)
        magic = 1 - self.ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((self.a * (1 - self.ee)) / (magic * sqrtmagic) * self.pi)
        dlng = (dlng * 180.0) / (self.a / sqrtmagic * math.cos(radlat) * self.pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return [lng * 2 - mglng, lat * 2 - mglat]

    # //经度转换
    def transformlat(self, lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 * math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lat * self.pi) + 40.0 * math.sin(lat / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 * self.pi) + 320 * math.sin(lat * self.pi / 30.0)) * 2.0 / 3.0
        return ret

    # //纬度转换
    def transformlng(self, lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
        ret += (20.0 * math.sin(6.0 * lng * self.pi) + 20.0 * math.sin(2.0 * lng * self.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(lng * self.pi) + 40.0 * math.sin(lng / 3.0 * self.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * self.pi) + 300.0 * math.sin(lng / 30.0 * self.pi)) * 2.0 / 3.0
        return ret

    def getWgs84xy(self, x, y):
        # //先转 国测局坐标
        doubles_gcj = self.bd09togcj02(x, y)
        # //（x 117.   y 36. ）
        # //国测局坐标转wgs84
        doubles_wgs84 = self.gcj02towgs84(doubles_gcj[0], doubles_gcj[1])
        # //返回 纠偏后 坐标
        return doubles_wgs84

    # 腾讯坐标转化为gps坐标
    def convert_tencentCoords_2_gpscoords(self, lng, lat):
        def is_in_china(lng, lat):
            """判断坐标是否在中国境内"""
            return 72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271

        def transform_lat(x, y):
            """GCJ-02转换算法中的纬度变换"""
            ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
            ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
            ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
            ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
            return ret

        def transform_lng(x, y):
            """GCJ-02转换算法中的经度变换"""
            ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
            ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
            ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
            ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
            return ret

        def delta(lng, lat):
            """计算GCJ-02与WGS-84的经纬度偏移量"""
            a = 6378245.0  # 克拉索夫斯基椭球长半轴
            ee = 0.00669342162296594323  # 克拉索夫斯基椭球扁率
            dlat = transform_lat(lng - 105.0, lat - 35.0)
            dlng = transform_lng(lng - 105.0, lat - 35.0)
            rad_lat = lat / 180.0 * math.pi
            magic = math.sin(rad_lat)
            magic = 1 - ee * magic * magic
            sqrt_magic = math.sqrt(magic)
            dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrt_magic) * math.pi)
            dlng = (dlng * 180.0) / (a / sqrt_magic * math.cos(rad_lat) * math.pi)
            return dlat, dlng

        """将GCJ-02坐标转换为WGS-84坐标"""
        if not is_in_china(lng, lat):
            return lng, lat
        dlat, dlng = delta(lng, lat)
        wgs_lat = lat - dlat
        wgs_lng = lng - dlng
        # 第二次校正
        dlat2, dlng2 = delta(wgs_lng, wgs_lat)
        wgs_lat = lat - dlat2
        wgs_lng = lng - dlng2
        return wgs_lng, wgs_lat


#  编写单元测试
if __name__ == '__main__':
    coord_converter = coordConverter()

    # 示例：将腾讯地图坐标转换为GPS坐标
    tencent_lng = 116.397428  # 腾讯地图经度
    tencent_lat = 39.90923  # 腾讯地图纬度

    wgs_lng, wgs_lat = coord_converter.convert_tencentCoords_2_gpscoords(tencent_lng, tencent_lat)
    print(f"腾讯地图坐标 (GCJ-02)：经度={tencent_lng}, 纬度={tencent_lat}")
    print(f"转换后的GPS坐标 (WGS-84)：经度={wgs_lng}, 纬度={wgs_lat}")
