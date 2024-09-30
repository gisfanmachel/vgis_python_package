"""
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Project :pythonCodeSnippet
@File    :downloadTilesTools.py
@IDE     :PyCharm
@Author  :chenxw
@Date    :2023/11/2 13:52
@Descr:  地图瓦片下载
"""
import json
import multiprocessing
import os
import shutil
import uuid
from datetime import datetime
from math import floor, log, tan, cos, pi, atan, exp
from multiprocessing.dummy import Pool as ThreadPool

import cv2
import numpy as np
import requests as req
from PIL import Image
from vgis_gis.geoserverTools import GeoserverOperatoer
from vgis_gis.gisTools import GISHelper


# 在线地图服务瓦片下载帮助类
class downloadTilesHelper:

    # 构造函数
    def __init__(self, tile_pic_suffix, merge_pic_name, resolution, tile_size, image_service_info, image_service_type,
                 tile_pic_path,
                 vcontat_img_path,
                 out_image_path, is_multi_thread, logger):
        # 瓦片图片后缀
        self.tile_pic_suffix = tile_pic_suffix
        # 合成图片名称
        self.merge_pic_name = merge_pic_name
        # 分辨率，每像素对应的地图单位值，值越小，精度越高，合成图片越大
        self.resolution = resolution
        # 下载瓦片像素大小
        self.tile_size = tile_size
        # 要下载瓦片的影像服务信息
        self.image_service_info = image_service_info
        # 要下载瓦片的影像服务类型，如wms,wmts,tms,xyz等
        self.image_service_type = image_service_type
        # 对于非wms服务，需要重新计算分辨率和瓦片像素大小，比如geoserver的wmts
        if image_service_type != "wms" and "geoserver" in image_service_info["service_type"]:
            self.resolution, self.tile_size, self.tile_coords = self.get_details_of_zoomlevel_in_geoserver(
                self.image_service_info["zoom_level"], self.image_service_info["gridset_name"])

        # 为每个用户线程创建一个临时目录
        tem_dir_name = str(uuid.uuid4())

        # 瓦片存储路径
        self.tile_pic_path = tile_pic_path if tile_pic_path is not None else os.path.join(os.getcwd(), ".cache",
                                                                                          "allTiles_"+tem_dir_name)
        # 每列瓦片拼接的竖条图片存放路径
        self.vcontat_img_path = vcontat_img_path if vcontat_img_path is not None else os.path.join(os.getcwd(),
                                                                                                   ".cache",
                                                                                                   "vMTiles_"+tem_dir_name)
        # 所有瓦片合成大图存放路径
        self.out_image_path = out_image_path
        # 是否使用多线程
        self.is_multi_thread = is_multi_thread
        self.logger = logger
        self.retry_download_curent = 0
        self.retry_download_count = 5
        self.delete_cache()
        self.mkdir(self.tile_pic_path)
        self.mkdir(self.vcontat_img_path)
        self.mkdir(self.out_image_path)

    # 获取geoserver切片里指定分级对应的分辨率
    def get_details_of_zoomlevel_in_geoserver(self, zoom_level, grid_set_name):
        geoserverOperatoer = GeoserverOperatoer(self.image_service_info["service_url"].split("/gwc/")[0],
                                                self.image_service_info["geoserver_username"],
                                                self.image_service_info["geoserver_password"])
        gridset_info = geoserverOperatoer.get_grid_set_info(grid_set_name)
        gridset_json = json.loads(gridset_info)
        return gridset_json["gridSet"]["resolutions"][zoom_level], gridset_json["gridSet"]["tileWidth"], \
            gridset_json["gridSet"]["extent"]["coords"]

    # 根据坐标范围计算瓦片的行列号
    def compute_tile_col_row_by_coords(self, xmin, xmax, ymin, ymax):
        tileMinCol, tileMaxCol, tileMinRow, tileMaxRow = None, None, None, None
        image_service_type = self.image_service_type
        # 为补偿浮点计算的不准确性
        epsilon = 1e-6
        # 左上角为原点
        if image_service_type == "wmts" or image_service_type == "xyz" or image_service_type == "quad":
            if self.image_service_info["service_type"] == "geoserver_wmts":
                # 基于瓦片分辨率、瓦片全部范围、瓦片大小
                # 原点（左上角）
                tileMatrixMinx = self.tile_coords[0]
                tileMatrixMaxY = self.tile_coords[3]
                tileMinCol = round(floor(abs(xmin - tileMatrixMinx) / self.resolution / self.tile_size + epsilon))
                tileMaxCol = round(floor(abs(xmax - tileMatrixMinx) / self.resolution / self.tile_size - epsilon))
                tileMinRow = round(floor(abs(tileMatrixMaxY - ymax) / self.resolution / self.tile_size + epsilon))
                tileMaxRow = round(floor(abs((tileMatrixMaxY - ymin)) / self.resolution / self.tile_size - epsilon))
            elif self.image_service_info["service_type"] == "google_xyz" or self.image_service_info[
                "service_type"] == "arcgis_xyz" or self.image_service_info[
                "service_type"] == "tdt_xyz" or self.image_service_info["service_type"] == "bing_quad":
                # 原点（左上角）
                # 基于瓦片级别,适合经纬度坐标范围
                zoom_level = self.image_service_info["zoom_level"]
                tileMinCol = floor((xmin + 180) / 360 * pow(2, zoom_level))
                tileMaxCol = floor((xmax + 180) / 360 * pow(2, zoom_level))
                tileMinRow = floor(
                    (1 - log(tan(ymax * pi / 180) + 1 / cos(ymax * pi / 180)) / pi) / 2 * pow(2, zoom_level))
                tileMaxRow = floor(
                    (1 - log(tan(ymin * pi / 180) + 1 / cos(ymin * pi / 180)) / pi) / 2 * pow(2, zoom_level))


        # 左下角为原点
        elif image_service_type == "tms":
            if self.image_service_info["service_type"] == "geoserver_tms":
                tileMatrixMinx = self.tile_coords[0]
                tileMatrixMiny = self.tile_coords[1]
                tileMinCol = round(floor(abs(xmin - tileMatrixMinx) / self.resolution / self.tile_size + epsilon))
                tileMaxCol = round(floor(abs(xmax - tileMatrixMinx) / self.resolution / self.tile_size - epsilon))
                tileMinRow = round(floor(abs(ymax - tileMatrixMiny) / self.resolution / self.tile_size + epsilon))
                tileMaxRow = round(floor(abs(ymin - tileMatrixMiny) / self.resolution / self.tile_size - epsilon))
        # 判断行列号是否越界
        matrixWidth = pow(2, self.image_service_info["zoom_level"] + 1)
        matrixHeight = pow(2, self.image_service_info["zoom_level"])
        if tileMinCol < 0:
            tileMinCol = 0
        if tileMaxCol >= matrixWidth:
            tileMaxCol = matrixWidth - 1
        if tileMinRow < 0:
            tileMinRow = 0
        if tileMaxRow >= matrixHeight:
            tileMaxRow = matrixHeight - 1
        return tileMinCol, tileMaxCol, tileMinRow, tileMaxRow

    # 下载wmts/tms/xyz瓦片
    def loop_download_tiles(self, xmin, xmax, ymin, ymax):
        # 得到瓦片行列号范围
        tileMinCol, tileMaxCol, tileMinRow, tileMaxRow = self.compute_tile_col_row_by_coords(xmin, xmax, ymin, ymax)
        if self.image_service_type == "wmts":
            # 单线程
            if not self.is_multi_thread:
                for col in range(tileMinCol, tileMaxCol + 1):
                    param = [col, tileMinRow, tileMaxRow]
                    self.loop_download_wmts_tiles_follow_col(param)

            # 多线程
            else:
                param_list = []
                for col in range(tileMinCol, tileMaxCol + 1):
                    param = [col, tileMinRow, tileMaxRow]
                    param_list.append(param)
                self.multi_thread_workder(self.loop_download_wmts_tiles_follow_col, param_list)
            # 同时计算左上角瓦片的地图单位
            # 瓦片原点在左上角
            left_top_tile_bounds = self.get_bounds_of_wmts_tile(self.image_service_info["zoom_level"],
                                                                tileMinRow, tileMinCol)
        elif self.image_service_type == "tms":
            pass
            # 同时计算左上角瓦片的地图单位
            # 瓦片原点在左下角
            if "geoserver" in self.image_service_info["service_type"]:
                pass
        elif self.image_service_type == "xyz" or self.image_service_type == "quad":

            for col in range(tileMinCol, tileMaxCol + 1):
                # 单线程
                if not self.is_multi_thread:
                    param = [col, tileMinRow, tileMaxRow]
                    if self.image_service_type == "xyz":
                        self.loop_download_xyz_tiles_follow_col(param)
                    elif self.image_service_type == "quad":
                        self.loop_download_quad_tiles_follow_col(param)
                # 多线程
                else:
                    param_list = []
                    for col in range(tileMinCol, tileMaxCol + 1):
                        param = [col, tileMinRow, tileMaxRow]
                        param_list.append(param)
                    if self.image_service_type == "xyz":
                        self.multi_thread_workder(self.loop_download_xyz_tiles_follow_col, param_list)
                    elif self.image_service_type == "quad":
                        self.multi_thread_workder(self.loop_download_quad_tiles_follow_col, param_list)

            # 同时计算左上角瓦片的地图单位
            # 瓦片原点在左上角
            # 得到瓦片的经纬度
            # 这个方法适合xyz和quad
            left_top_tile_bounds = self.get_bounds_of_xyz_tile(self.image_service_info["zoom_level"],
                                                               tileMinRow,
                                                               tileMinCol)
            # 如果地图底图是3857，需要转成经纬度
            if self.image_service_info["epsg"] == 3857:
                point_lb = GISHelper.convert_point_from_wgs84_to_mercator(
                    [left_top_tile_bounds[0], left_top_tile_bounds[1]])
                point_rt = GISHelper.convert_point_from_wgs84_to_mercator(
                    [left_top_tile_bounds[2], left_top_tile_bounds[3]])
                left_top_tile_bounds = [point_lb[0], point_lb[1], point_rt[0], point_rt[1]]

        return left_top_tile_bounds

    # 获取wmts瓦片的地图坐标范围
    def get_bounds_of_wmts_tile(self, level, row, col):
        tile_bounds = None
        if self.image_service_info["service_type"] == "geoserver_wmts":
            tile_url = self.build_wmts_tile_pic_url(col, row, level)
            payload = {}
            headers = {}
            response = req.request("GET", tile_url, headers=headers, data=payload)
            headers = response.headers
            # 109.8193359375,22.69775390625,109.8248291015625,22.7032470703125
            tile_bounds = headers["geowebcache-tile-bounds"]
            return tile_bounds.split(",")

    #  通过瓦片的行列号及层级 获取xyz瓦片的地图坐标范围
    def get_bounds_of_xyz_tile(self, level, row, col):
        tile_bounds = None
        if self.image_service_info["service_type"] == "google_xyz" or self.image_service_info[
            "service_type"] == "arcgis_xyz" or self.image_service_info[
            "service_type"] == "tdt_xyz" or self.image_service_info["service_type"] == "bing_quad":
            left_lon = col / pow(2, level) * 360 - 180
            right_lon = (col + 1) / pow(2, level) * 360 - 180
            n = pi - (2 * pi * row) / pow(2, level)
            top_lat = 180 / pi * atan(0.5 * (exp(n) - exp(-n)))
            n = pi - (2 * pi * (row + 1)) / pow(2, level)
            bottom_lat = 180 / pi * atan(0.5 * (exp(n) - exp(-n)))
            tile_bounds = [left_lon, bottom_lat, right_lon, top_lat]
        return tile_bounds

    # 执行多线程任务
    def multi_thread_workder(self, function, param_list):
        # 启动多线程，跟CPU核数对应
        cpu_count = multiprocessing.cpu_count()
        pool = ThreadPool(cpu_count)
        self.logger.info('执行多线程，线程数:{}'.format(cpu_count))
        pool.map(function, param_list)
        # 结束多线程
        pool.close()
        pool.join()

    # 按照指定范围下载瓦片并拼接成大图
    # 地图底图 4326, 下载范围坐标为经纬度，生成的瓦片大图坐标为经纬度，瓦片大图投影为4326，瓦片分辨率为4326方案
    # 地图底图 3857，下载范围坐标为经纬度，生成的瓦片大图坐标为米，瓦片大图投影为3857，瓦片分辨率为3857方案
    # 上面两种方式，才能保证下载的瓦片大图与地图底图能吻合上
    def fetch_tiles(self, xmin, xmax, ymin, ymax):
        try:
            # 对影像服务的指定区域进行瓦片下载（针对下载不成功的进行重试），拼接成jpg/png，并生成jgw/pgw
            # 如果已经下载则跳过
            # 目录及文件命名形式：
            left_x = xmin
            top_y = ymax

            # 先判断缓存里有没有合成的图片数据，没有再去重新下载
            if not os.path.exists(os.path.join(self.out_image_path, self.merge_pic_name)):
                if self.image_service_type == "wms":
                    # 单线程
                    if not self.is_multi_thread:
                        # 按照每个瓦片的大小作为步长进行下载
                        # 沿着X方向（列）,逐步长滑动
                        while xmin < xmax:
                            param = [xmin, ymin, ymax]
                            self.loop_download_wms_tiles_follow_y(param)
                            xmin += (self.resolution * self.tile_size)
                    # 多线程实现并行下载每一列
                    else:
                        # pass
                        # 按照每个瓦片的大小作为步长进行下载
                        # 沿着X方向（列）,逐步长滑动
                        param_list = []
                        while xmin < xmax:
                            param = [xmin, ymin, ymax]
                            param_list.append(param)
                            xmin += (self.resolution * self.tile_size)
                        self.multi_thread_workder(self.loop_download_wms_tiles_follow_y, param_list)
                elif self.image_service_type == "wmts" or self.image_service_type == "tms" or self.image_service_type == "xyz" or self.image_service_type == "quad":

                    left_top_tile_bounds = self.loop_download_tiles(xmin, xmax, ymin, ymax)

                self.logger.info('瓦片下载完成')

                # 拼接瓦片图片
                self.logger.info('正在拼接瓦片为图片')
                try:
                    # 合成瓦片成大图
                    self.merge_tiles_to_image()
                    # 生成world文件需要的参数
                    # 根据坐标范围反算瓦片的行列号，最后拼成的瓦片大图，比输入的坐标范围要大些，因为需要重新计算左上角点的地图坐标
                    if self.image_service_type != "wms":
                        left_x, top_y = float(left_top_tile_bounds[0]), float(left_top_tile_bounds[3])
                        if self.image_service_type == "xyz" or self.image_service_type == "quad":
                            if self.image_service_info["epsg"] == 4326:
                                self.resolution = 0.703125 * 2 / pow(2,
                                                                     self.image_service_info[
                                                                         "zoom_level"])
                            elif self.image_service_info["epsg"] == 3857:
                                self.resolution = 78271.51696399994 * 2 / pow(2,
                                                                              self.image_service_info[
                                                                                  "zoom_level"])

                    # 生成world文件
                    self.build_merge_image_world_file_info(left_x, top_y)
                except Exception as tm_exp:
                    self.logger.error("瓦片拼接失败，请检查瓦片：{}".format(str(tm_exp)))
                    self.logger.error(tm_exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
                    self.logger.error(tm_exp.__traceback__.tb_lineno)  # 发生异常所在的行数
            else:
                self.logger.warning("之前已拼接过图片")
            self.delete_cache()
        except Exception as exp:
            self.logger.error("下载瓦片失败：{}".format(str(exp)))
            self.logger.error(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            self.logger.error(exp.__traceback__.tb_lineno)  # 发生异常所在的行数

    def delete_cache(self):
        # 清空下载的瓦片缓存（中间数据）
        if os.path.exists(self.tile_pic_path):
            shutil.rmtree(self.tile_pic_path)
        # 清空拼接的竖条瓦片图片（中间数据）
        if os.path.exists(self.vcontat_img_path):
            shutil.rmtree(self.vcontat_img_path)

    # 将瓦片合并成大图
    def merge_tiles_to_image(self):
        #  瓦片数据目录组织，是按照每个下载步长
        tiles_stride_dirs = os.listdir(self.tile_pic_path)
        # 先生成所有的竖条
        for tile_stride_dir in tiles_stride_dirs:
            self.vconcat_tileImage(tile_stride_dir)
        # 对所有竖条进行拼接成最终大图
        final, width, height = self.hconcat_vconcatImages(self.vcontat_img_path)
        self.logger.info('瓦片拼接完成')
        final.save(os.path.join(self.out_image_path, self.merge_pic_name))

    # 生成每一列的图片,即竖条
    def vconcat_tileImage(self, tile_stride_dir):
        tile_img_dir = os.path.join(self.tile_pic_path, tile_stride_dir)  # 原始文件目录
        names = os.listdir(tile_img_dir)
        #
        if self.image_service_type == "wms":
            # 竖着的瓦片要从上往下粘贴，对应的图片名称，Y的值越大越往上，所以做了反转
            # names.reverse()
            names = sorted(names, reverse=True)
            # sorted_names = sorted(names, key=self.custom_sort, reverse=True)
        # windows环境不用，linux环境需要下面的代码
        elif self.image_service_type == "wmts" or self.image_service_type == "xyz" or self.image_service_type == "quad":
            # wmts/xyz的原点在左下方，因此COL值越小越往上，不做反转
            names = sorted(names)

        images = []
        for name in names:
            img_path = os.path.join(tile_img_dir, name)
            # 拼接图片不稳定，如果图片中只有少量，就会报错
            # error: (-215:Assertion failed) src[i].dims <= 2 && src[i].cols == src[0].cols && src[i].type() == src[0].type() in function 'cv::vconcat'
            # 不完整的瓦片多了一个通道，需要删除，导致拼接的图片shape不一致,正确图片shape为(256,256,3) 错误瓦片shape为(256,256,4)
            # 修改by chenxw 将参数里的-1改成了1，有些不完整的瓦片通道变成了四个，需要这里只读前三个通道，和完整瓦片的三通道保持一致
            image = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), 1)
            images.append(image)
        img = cv2.vconcat(images)
        compress_rate = 1
        height, width = img.shape[:2]
        # 双三次插值
        img_resize = cv2.resize(img, (int(width * compress_rate), int(height * compress_rate)),
                                interpolation=cv2.INTER_AREA)
        # 保存每列瓦片竖条合成图
        vconcat_pic_path = os.path.join(self.vcontat_img_path, '{}.{}'.format(tile_stride_dir, self.tile_pic_suffix))
        # 解决中文路径保存问题
        cv2.imencode('.{}'.format(self.tile_pic_suffix), img_resize)[1].tofile(vconcat_pic_path)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # 对所有每一列竖条图片进行合并生成大图
    def hconcat_vconcatImages(self, img_dir):
        images = os.listdir(img_dir)
        # 每个竖条图片名称为x值，或者col，从小到大，依次对应大图的从左到右
        images = sorted(images)

        # 只需要图片,过滤掉目录里非图片
        def file_filter(f):
            if os.path.splitext(f)[1] in ['.jpg', '.jpeg', '.png', '.bmp']:
                return True
            else:
                return False

        images = list(filter(file_filter, images))
        img = Image.open(os.path.join(img_dir, images[0]))
        width = img.size[0] * len(images)
        height = img.size[1]
        final = Image.new('RGB', (width, height))

        for index, image in enumerate(images):
            img = Image.open(os.path.join(img_dir, image))
            final.paste(img, ((img.size[0] * index), 0))

        return final, width, height

    # 生成jgw/pgw --world file世界投影文件
    def build_merge_image_world_file_info(self, left_x, top_y):
        world_file_suffix = "jgw"
        if self.tile_pic_suffix == "jpg" or self.tile_pic_suffix == "jpeg":
            world_file_suffix = "jgw"
        elif self.tile_pic_suffix == "png":
            world_file_suffix = "pgw"
        file_pre_path, file_name = os.path.split(self.merge_pic_name)
        shotname, suffix = os.path.splitext(file_name)
        filename = os.path.join(self.out_image_path, "{}.{}".format(shotname, world_file_suffix))
        with open(filename, 'w') as file:
            # 在X方向的比例关系;每像素对应的经度值
            file.write("{}\n".format(self.resolution))
            # 影像数据的旋转参数，一般忽略，记录为0
            file.write("0.0000000000\n")
            # 影像数据的旋转参数，一般忽略，记录为0
            file.write("0.0000000000\n")
            # 在Y方向的比例关系;;每像素对应的纬度值，为负值, 这是由于空间坐标系与影像图片像素坐标系在Y方向上相反
            file.write("-{}\n".format(self.resolution))
            # 影像图片左上角点对应的空间坐标的X坐标
            file.write(str(left_x) + "\n")
            # 影像图片左上角点对应的空间坐标的Y坐标
            file.write(str(top_y) + "\n")

    # 沿着Y方向循环下载wms瓦片
    # param=[xmin, ymin, ymax]
    # 方向为从上往下
    def loop_download_wms_tiles_follow_y(self, param):
        xmin = param[0]
        ymin = param[1]
        ymax = param[2]
        # 沿着Y方向
        while ymax > ymin:
            bbox = str(xmin) + "%2C" + str(ymax - (self.resolution * self.tile_size)) + "%2C" + str(
                xmin + (self.resolution * self.tile_size)) + "%2C" + str(ymax)
            tile_url = self.build_wms_tile_pic_url(bbox)
            # 下载瓦片
            # self.retry_download_curent = 0
            retry_count = 0
            self.download_each_tile(retry_count, tile_url, "y=" + str(ymax) + "&x=" + str(xmin), xmin)
            ymax -= (self.resolution * self.tile_size)

    # param:[currentCol,tileMinRow,tileMaxRow]
    def loop_download_wmts_tiles_follow_col(self, param):
        col = param[0]
        tileMinRow = param[1]
        tileMaxRow = param[2]
        for row in range(tileMinRow, tileMaxRow + 1):
            tile_url = self.build_wmts_tile_pic_url(col, row, self.image_service_info["zoom_level"])
            # 下载瓦片
            # self.retry_download_curent = 0
            retry_count = 0
            self.download_each_tile(retry_count, tile_url, "row=" + str(row) + "&col=" + str(col), col)

    # param:[currentCol,tileMinRow,tileMaxRow]
    def loop_download_xyz_tiles_follow_col(self, param):
        col = param[0]
        tileMinRow = param[1]
        tileMaxRow = param[2]
        for row in range(tileMinRow, tileMaxRow + 1):
            tile_url = self.build_xyz_tile_pic_url(col, row, self.image_service_info["zoom_level"])
            # 下载瓦片
            # self.retry_download_curent = 0
            retry_count = 0
            self.download_each_tile(retry_count, tile_url, "row=" + str(row) + "&col=" + str(col), col)

    # param:[currentCol,tileMinRow,tileMaxRow]
    def loop_download_quad_tiles_follow_col(self, param):
        col = param[0]
        tileMinRow = param[1]
        tileMaxRow = param[2]
        for row in range(tileMinRow, tileMaxRow + 1):
            tile_url = self.build_quad_tile_pic_url(col, row, self.image_service_info["zoom_level"])
            # 下载瓦片
            # self.retry_download_curent = 0
            retry_count = 0
            self.download_each_tile(retry_count, tile_url, "row=" + str(row) + "&col=" + str(col), col)

    # 获取xyz瓦片下载地址
    def build_xyz_tile_pic_url(self, col, row, level):
        url = None
        if self.image_service_info["service_type"] == "google_xyz":
            url = "{}{}&x={}&y={}&z={}".format(
                self.image_service_info["service_url"], self.image_service_info["layer_name"],
                col, row, level)
        elif self.image_service_info["service_type"] == "arcgis_xyz":
            url = "{}{}/MapServer/tile/{}/{}/{}".format(
                self.image_service_info["service_url"], self.image_service_info["layer_name"],
                level, row, col)
            # print(url)
        # 需要天地图许可--服务器端
        elif self.image_service_info["service_type"] == "tdt_xyz":
            url = "{}T={}&x={}&y={}&l={}&tk=6b059214ffa69ab16b57309422d77660".format(
                self.image_service_info["service_url"], self.image_service_info["layer_name"],
                col, row, level)
            # print(url)
        return url

    # 通过xyz获取quadtreekey
    def tile_xyz_to_quadkey(self, x, y, z):
        quadkey = ""
        for i in range(z, -1, -1):
            bitmask = 1 << i
            digit = 0
            if (x & bitmask) != 0:
                digit |= 1
            if (y & bitmask) != 0:
                digit |= 2
            quadkey += str(digit)
        if quadkey[0] == '0':
            quadkey = quadkey[1:]
        return quadkey

    # 获取quadtree瓦片下载地址
    def build_quad_tile_pic_url(self, col, row, level):
        quadkey = self.tile_xyz_to_quadkey(col, row, level)
        # url="https://ecn.t2.tiles.virtualearth.net/tiles/a13231.jpeg?g=14364"
        # url = "{}/tiles/{}{}.jpeg?g=14364"
        url = None
        if self.image_service_info["service_type"] == "bing_quad":
            url = "{}/tiles/{}{}.jpeg?g=14364".format(
                self.image_service_info["service_url"], self.image_service_info["layer_name"],
                quadkey)
        return url

    # 获取wmts瓦片下载地址
    def build_wmts_tile_pic_url(self, col, row, level):
        url = None
        if self.image_service_info["service_type"] == "geoserver_wmts":
            url = "{}layer={}&style=&tilematrixset={}&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image/{}&TileMatrix={}:{}&TileCol={}&TileRow={}".format(
                self.image_service_info["service_url"], self.image_service_info["layer_name"],
                self.image_service_info["gridset_name"], self.tile_pic_suffix, self.image_service_info["gridset_name"],
                level, col, row)
        else:
            pass
        return url

    # 构造下载的wms地图服务影像图片下载URL
    def build_wms_tile_pic_url(self, bbox):
        # geoserver发布的wms服务
        if self.image_service_info["service_type"] == "geoserver_wms":
            # url里的中文编码问题
            # layer_name = urllib.parse.quote(self.image_service_info["layer_name"].encode("gb2312"))
            data = {
                'LAYERS': self.image_service_info["layer_name"],
                'SERVICE': 'WMS',
                'REQUEST': 'GetMap',
                'SRS': 'EPSG:4326',
                'WIDTH': '{}'.format(self.tile_size),
                'HEIGHT': '{}'.format(self.tile_size),
                'STYLES': '',
                'BBOX': bbox,
                'FORMAT': "image/{}".format(self.tile_pic_suffix)
            }
            # 拼接url参数
            lt = []
            for k, v in data.items():
                lt.append(k + '=' + str(v))
            # 拼接url
            url = self.image_service_info["service_url"] + '&'.join(lt)
        # 卫星中心一张图2米WMS服务
        elif self.image_service_info["service_type"] == "satellite_center_wms":
            data = {
                'SERVICE': 'WMS',
                'REQUEST': 'GetMap',
                # 'SRS': 'EPSG%3A4326',
                'SRS': 'WGS84',
                'ACCOUNT': 'zkzy',
                'PASSWD': 'fee528666a542aeb9f086093883c453d',
                'WIDTH': '{}'.format(self.tile_size),
                'HEIGHT': '{}'.format(self.tile_size),
                'FORMAT': 'image/{}'.format(self.tile_pic_suffix),
                'STYLES': '',
                'BBOX': bbox
            }
            # 拼接url参数
            lt = []
            for k, v in data.items():
                lt.append(k + '=' + str(v))
            # 拼接url
            url = self.image_service_info["service_url"] + "/" + self.image_service_info[
                "layer_name"] + "/wms?" + '&'.join(lt)

        # self.logger.info("瓦片地址：" + url)
        return url

    # 下载每个小瓦片，适合单线程，因为要共用变量self.retry_download_curent
    def download_each_tile_bak(self, url, pic_name, pic_dir_name):
        if self.retry_download_curent <= 5:
            try:
                if self.retry_download_curent > 0:
                    self.logger.info("self.retry_download_curent:{}".format(self.retry_download_curent))
                self.retry_download_curent += 1
                # 读取远程图片
                path = os.path.join(self.tile_pic_path, str(pic_dir_name))
                if not os.path.exists(path):
                    # 创建文件夹
                    self.mkdir(path)
                    self.logger.info("创建文件夹:" + path + "--" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                tilefile = os.path.join(path, '{}.{}'.format(pic_name, self.tile_pic_suffix))
                # # 如果瓦片存在，但大于100K，说明有可能是损坏的瓦片，需要重新下载-修改chenxw
                # if os.path.exists(tilefile):
                #     fileSize = os.path.getsize(tilefile) / 1024
                #     if fileSize > 100:
                #         os.remove(tilefile)
                # 如果瓦片图片不存在才下载
                if not os.path.exists(tilefile):
                    # url中有中文问题
                    # pic = urllib.request.urlopen(url).read()
                    pic = req.get(url)
                    # 创建瓦片图片
                    with open(tilefile, 'wb') as f:
                        f.write(pic.content)
                # 如果已下载瓦片不完整，需要重新下载
                else:
                    # print("检查文件夹下的瓦片:" + path)
                    try:
                        img_cv = cv2.imdecode(np.fromfile(tilefile, dtype=np.uint8), -1)
                        if img_cv is not None:
                            if img_cv.shape[2] == 4:
                                self.logger.info(
                                    "下载瓦片不完整，需要重新下载：" + tilefile + "--" + datetime.now().strftime(
                                        '%Y-%m-%d %H:%M:%S'))
                                os.remove(tilefile)
                                self.download_each_tile(url, pic_name, pic_dir_name)
                            else:
                                pass
                                # self.logger.info("瓦片已存在且完整不再下载---" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    except BaseException as ex:
                        self.logger.error(
                            "读取瓦片文件失败---" + tilefile + "---" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        os.remove(tilefile)
                        # 瓦片下载失败，重试
                        self.download_each_tile(url, pic_name, pic_dir_name)
            except BaseException as ex:
                self.logger.error("下载失败" + str(ex) + "---" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                self.logger.error(url)
                if str(ex) != "HTTP Error 404: Not Found":
                    self.logger.error("正在重新下载---" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    # 瓦片下载失败，重试
                    self.download_each_tile(url, pic_name, pic_dir_name)

    # 下载每个小瓦片
    def download_each_tile(self, retry_count, url, pic_name, pic_dir_name):
        if retry_count <= 5:
            try:
                if retry_count > 0:
                    self.logger.info("retry_count:{}".format(retry_count))
                retry_count += 1
                # 读取远程图片
                path = os.path.join(self.tile_pic_path, str(pic_dir_name))
                if not os.path.exists(path):
                    # 创建文件夹
                    self.mkdir(path)
                    self.logger.info("创建文件夹:" + path + "--" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                tilefile = os.path.join(path, '{}.{}'.format(pic_name, self.tile_pic_suffix))
                # # 如果瓦片存在，但大于100K，说明有可能是损坏的瓦片，需要重新下载-修改chenxw
                # if os.path.exists(tilefile):
                #     fileSize = os.path.getsize(tilefile) / 1024
                #     if fileSize > 100:
                #         os.remove(tilefile)
                # 如果瓦片图片不存在才下载
                if not os.path.exists(tilefile):
                    # url中有中文问题
                    # pic = urllib.request.urlopen(url).read()
                    pic = req.get(url)
                    # 创建瓦片图片
                    with open(tilefile, 'wb') as f:
                        f.write(pic.content)
                # 如果已下载瓦片不完整，需要重新下载
                else:
                    # print("检查文件夹下的瓦片:" + path)
                    try:
                        img_cv = cv2.imdecode(np.fromfile(tilefile, dtype=np.uint8), -1)
                        if img_cv is not None:
                            if img_cv.shape[2] == 4:
                                self.logger.info(
                                    "下载瓦片不完整，需要重新下载：" + tilefile + "--" + datetime.now().strftime(
                                        '%Y-%m-%d %H:%M:%S'))
                                os.remove(tilefile)
                                self.download_each_tile(retry_count, url, pic_name, pic_dir_name)
                            else:
                                pass
                                # self.logger.info("瓦片已存在且完整不再下载---" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    except BaseException as ex:
                        self.logger.error(
                            "读取瓦片文件失败---" + tilefile + "---" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        os.remove(tilefile)
                        # 瓦片下载失败，重试
                        self.download_each_tile(retry_count, url, pic_name, pic_dir_name)
            except BaseException as ex:
                self.logger.error("下载失败" + str(ex) + "---" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                self.logger.error(url)
                if str(ex) != "HTTP Error 404: Not Found":
                    self.logger.error("正在重新下载---" + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    # 瓦片下载失败，重试
                    self.download_each_tile(retry_count, url, pic_name, pic_dir_name)

    # 创建文件夹
    def mkdir(self, path):
        folder = os.path.exists(path)
        # 判断是否存在文件夹如果不存在则创建为文件夹
        if not folder:
            # 创建文件时如果路径不存在会创建这个路径
            os.makedirs(path)

    # 删除文件夹内文件
    def rmdir(self, img_dir):
        images = os.listdir(img_dir)
        for name in images:
            img_path = os.path.join(img_dir, name)
            os.remove(img_path)


if __name__ == '__main__':
    pass
