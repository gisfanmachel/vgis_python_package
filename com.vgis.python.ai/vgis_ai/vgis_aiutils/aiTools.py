"""
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Project :pythonCodeSnippet
@File    :aiTools.py
@IDE     :PyCharm
@Author  :chenxw
@Date    :2023/9/13 11:53
@Descr:
"""
import os

import cv2
import numpy as np
import pycocotools.mask as mask_util
from PIL.Image import Image
from osgeo import ogr, gdal
from vgis_gis.shpTools import ShpFileOperator
from vgis_rs.rsTools import RsToolsOperatoer

from vgis_utils.vgis_image.imageTools import ImageHelper
from vgis_utils.vgis_list.listTools import ListHelper


class AIHelper:
    def __init__(self):
        pass

    @staticmethod
    # 计算一个 ground truth 边界盒和 k 个先验框(Anchor)的交并比(IOU)值。
    def __iou(box, clusters):
        """
        计算一个 ground truth 边界盒和 k 个先验框(Anchor)的交并比(IOU)值。
        参数box: 元组或者数据，代表 ground truth 的长宽。
        参数clusters: 形如(k,2)的numpy数组，其中k是聚类Anchor框的个数
        返回：ground truth和每个Anchor框的交并比。
        """
        x = np.minimum(clusters[:, 0], box[0])
        y = np.minimum(clusters[:, 1], box[1])
        if np.count_nonzero(x == 0) > 0 or np.count_nonzero(y == 0) > 0:
            raise ValueError("Box has no area")
        intersection = x * y
        box_area = box[0] * box[1]
        cluster_area = clusters[:, 0] * clusters[:, 1]
        iou_ = intersection / (box_area + cluster_area - intersection)
        return iou_

    @staticmethod
    # 计算一个ground truth和k个Anchor的交并比的均值。
    def avg_iou(boxes, clusters):
        """
        计算一个ground truth和k个Anchor的交并比的均值。
        """
        return np.mean([np.max(AIHelper.__iou(boxes[i], clusters)) for i in range(boxes.shape[0])])

    @staticmethod
    # 利用IOU值进行K-means聚类
    def kmeans(boxes, k, dist=np.median):
        """
        利用IOU值进行K-means聚类
        参数boxes: 形状为(r, 2)的ground truth框，其中r是ground truth的个数
        参数k: Anchor的个数
        参数dist: 距离函数
        返回值：形状为(k, 2)的k个Anchor框
        """
        # 即是上面提到的r
        rows = boxes.shape[0]
        # 距离数组，计算每个ground truth和k个Anchor的距离
        distances = np.empty((rows, k))
        # 上一次每个ground truth"距离"最近的Anchor索引
        last_clusters = np.zeros((rows,))
        # 设置随机数种子
        np.random.seed()

        # 初始化聚类中心，k个簇，从r个ground truth随机选k个
        clusters = boxes[np.random.choice(rows, k, replace=False)]
        # 开始聚类
        while True:
            # 计算每个ground truth和k个Anchor的距离，用1-IOU(box,anchor)来计算
            for row in range(rows):
                distances[row] = 1 - AIHelper.__iou(boxes[row], clusters)
            # 对每个ground truth，选取距离最小的那个Anchor，并存下索引
            nearest_clusters = np.argmin(distances, axis=1)
            # 如果当前每个ground truth"距离"最近的Anchor索引和上一次一样，聚类结束
            if (last_clusters == nearest_clusters).all():
                break
            # 更新簇中心为簇里面所有的ground truth框的均值
            for cluster in range(k):
                clusters[cluster] = dist(boxes[nearest_clusters == cluster], axis=0)
            # 更新每个ground truth"距离"最近的Anchor索引
            last_clusters = nearest_clusters

        return clusters

    @staticmethod
    # 获取两个矩形框的重叠面积
    #     rect1 = [0, 0, 5, 5]
    #     rect2 = [3, 3, 8, 8]
    def get_overlay_radio_of_two_box(rect1, rect2):
        x_overlap = max(0, min(rect1[2], rect2[2]) - max(rect1[0], rect2[0]))
        y_overlap = max(0, min(rect1[3], rect2[3]) - max(rect1[1], rect2[1]))
        overlap_area = x_overlap * y_overlap
        rect1_eara = (rect1[2] - rect1[0]) * (rect1[3] - rect1[1])
        overlap_radio = overlap_area / rect1_eara
        return overlap_radio

    @staticmethod
    # yolov8结果框转化为shapefile文件
    # xyxy_box_list:[[pixel_minx,pixel_miny,pixel_maxx,pixel_maxy],[pixel_minx2,pixel_miny2,pixel_maxx2,pixel_maxy2]]
    # image_shape:(width,height)
    # image_map_env:(map_minx,map_miny,map_maxx,map_maxy)
    def convert_yolo_box_to_shape(yolov_xyxy_box_list, names, image_path, image_map_env, map_epsg, out_shp_path):
        # img = cv2.imread(image_path)
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
        image_shape = img.shape

        map_coords_list = []
        for xyxy_box in yolov_xyxy_box_list:
            pixel_x_min = xyxy_box[0]
            pixel_y_min = xyxy_box[1]
            pixel_x_max = xyxy_box[2]
            pixel_y_max = xyxy_box[3]
            conf = xyxy_box[4]
            cls = xyxy_box[5]
            name = names[cls]
            image_height = image_shape[0]
            image_width = image_shape[1]
            image_minx_map = image_map_env[0]
            image_miny_map = image_map_env[1]
            image_maxx_map = image_map_env[2]
            image_maxy_map = image_map_env[3]
            map_x_min = image_minx_map + (image_maxx_map - image_minx_map) / image_width * pixel_x_min
            map_y_min = image_maxy_map - (image_maxy_map - image_miny_map) / image_height * pixel_y_max
            map_x_max = image_minx_map + (image_maxx_map - image_minx_map) / image_width * pixel_x_max
            map_y_max = image_maxy_map - (image_maxy_map - image_miny_map) / image_height * pixel_y_min
            map_coords_list.append([map_x_min, map_y_min, map_x_max, map_y_max, conf, cls, name])
        ShpFileOperator.convert_box_points_and_attr_into_shp(map_coords_list, map_epsg, out_shp_path)

    @staticmethod
    # mmdetv3结果框转化为shapefile文件
    # mmdet_prediction:{'labels':'','scores':'','bboxes':'','masks':''}
    # image_shape:(width,height)
    # image_map_env:(map_minx,map_miny,map_maxx,map_maxy)
    def convert_mmdet_pred_to_shape(mmdet_prediction, conf_value, names, image_path, image_map_env, map_epsg,
                                    out_boxs_shp_path,
                                    out_polys_shp_path):
        # img = cv2.imread(image_path)
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
        image_shape = img.shape
        map_box_coords_list = []
        map_poly_coords_list = []
        for index in range(len(mmdet_prediction["labels"])):
            label = mmdet_prediction["labels"][index]
            score = mmdet_prediction["scores"][index]
            # 满足置信度阈值的
            if score >= conf_value:
                bbox = mmdet_prediction["bboxes"][index]
                if out_polys_shp_path is not None:
                    # 将rle转为polygon
                    mask_rle = mmdet_prediction["masks"][index]
                    # rle_counts = mask_rle["counts"]
                    mask_data = AIHelper.convert_rle_to_mask(mask_rle)
                    poly = AIHelper.convert_mask_to_poly(mask_data)

                pixel_x_min = bbox[0]
                pixel_y_min = bbox[1]
                pixel_x_max = bbox[2]
                pixel_y_max = bbox[3]
                conf = score
                cls = label
                name = names[cls]
                image_height = image_shape[0]
                image_width = image_shape[1]
                image_minx_map = image_map_env[0]
                image_miny_map = image_map_env[1]
                image_maxx_map = image_map_env[2]
                image_maxy_map = image_map_env[3]
                # 像素坐标转换为地图坐标
                map_x_min = image_minx_map + (image_maxx_map - image_minx_map) / image_width * pixel_x_min
                map_y_min = image_maxy_map - (image_maxy_map - image_miny_map) / image_height * pixel_y_max
                map_x_max = image_minx_map + (image_maxx_map - image_minx_map) / image_width * pixel_x_max
                map_y_max = image_maxy_map - (image_maxy_map - image_miny_map) / image_height * pixel_y_min
                map_box_coords_list.append([map_x_min, map_y_min, map_x_max, map_y_max, conf, cls, name])
                if out_polys_shp_path is not None:
                    map_poly = []
                    for poly_point in poly:
                        pixel_poly_point_x = poly_point[0]
                        pixel_poly_point_y = poly_point[1]
                        map_poly_point_x = image_minx_map + (
                                image_maxx_map - image_minx_map) / image_width * pixel_poly_point_x
                        map_poly_point_y = image_maxy_map - (
                                image_maxy_map - image_miny_map) / image_height * pixel_poly_point_y
                        map_poly_point = [map_poly_point_x, map_poly_point_y]
                        map_poly.append(map_poly_point)
                    map_poly_coords_list.append([map_poly, conf, cls, name])
        if out_boxs_shp_path is not None:
            ShpFileOperator.convert_box_points_and_attr_into_shp(map_box_coords_list, map_epsg, out_boxs_shp_path)
        if out_polys_shp_path is not None:
            ShpFileOperator.convert_polygon_points_and_attr_into_shp(map_poly_coords_list, map_epsg, out_polys_shp_path)

    @staticmethod
    # rle(dict)转mask(ndarray)
    def convert_rle_to_mask(rle):
        mask = np.array(mask_util.decode(rle), dtype=np.float32)
        return mask

    @staticmethod
    # rles(list)转masks(ndarray)
    def convert_rles_to_masks(rles):
        masks = []
        for rle in rles:
            mask = np.array(mask_util.decode(rle), dtype=np.float32)
            masks.append(mask)
        masks = np.array(masks)
        return masks

    @staticmethod
    # mask(ndarray)转rle(dict)
    def convert_mask_to_rle(mask):
        # encoded with RLE
        rle = mask_util.encode(
            np.array(mask[:, :, np.newaxis], order='F',
                     dtype='uint8'))[0]
        if isinstance(rle['counts'], bytes):
            rle['counts'] = rle['counts'].decode()
        return rle

    @staticmethod
    # mask(ndarray)转rle(dict)方法2
    def convert_mask_to_rle_2(mask):
        rle = mask_util.encode(np.array(mask[:, :, None], order='F', dtype="uint8"))[0]
        rle["counts"] = rle["counts"].decode("utf-8")
        return rle

    @staticmethod
    # masks(ndarray)转rles(list)
    def convert_masks_to_rles(masks):
        rles = []
        for mask in masks:
            # encoded with RLE
            rle = mask_util.encode(
                np.array(mask[:, :, np.newaxis], order='F',
                         dtype='uint8'))[0]
            if isinstance(rle['counts'], bytes):
                rle['counts'] = rle['counts'].decode()
            rles.append(rle)

        return rles

    @staticmethod
    # polys(list)装rles(list)
    # polys:[[x1,y1,x2,y2...xn,yn],....]
    def convert_polys_to_rles(polys, width, height):
        rles = mask_util.frPyObjects(pyobj=polys, h=height, w=width)
        return rles

    @staticmethod
    # labelme_polys:[[[x1,y1],[x2,y2]...[xn,yn]],...]
    # coco_polys:[[x1,y1,x2,y2...xn,yn],....]
    def convert_labelme_polys_to_coco_polys(labelme_polys):
        coco_polys = []
        for labelme_poly in labelme_polys:
            # 二维数据打散到一维数据
            coco_poly = [num for sublist in labelme_poly for num in sublist]
            coco_polys.append(coco_poly)
        return coco_polys

    @staticmethod
    # labelme_polys:[[[x1,y1],[x2,y2]...[xn,yn]],...]
    # coco_polys:[[x1,y1,x2,y2...xn,yn],....]
    def convert_coco_polys_to_labelme_polys(coco_polys):
        labelme_polys = []
        for coco_poly in coco_polys:
            # 一维数据分到二维数据(每两个数字为一行)
            # 计算需要分组的次数
            group_count = len(coco_poly) // 2 + (len(coco_poly) % 2 != 0)
            # 利用列表切片进行分组并添加到新的二维列表中
            labelme_poly = [[coco_poly[i], coco_poly[i + 1]] for i in range(0, group_count * 2, 2)]
            labelme_polys.append(labelme_poly)
        return labelme_polys

    @staticmethod
    # 在图上画polys
    # polys:[[[x1,y1],[x2,y2]...[xn,yn]],[[x1,y1],[x2,y2]...[xn,yn]]...]
    def draw_polys_on_image(base_image_path, polys, merge_image_path):
        img = cv2.imread(base_image_path)
        # 每个poly的长度可能不太一样，所以需要一个一个绘制
        for poly in polys:
            polys_points = np.array([poly], dtype=np.int32)
            cv2.polylines(img, polys_points, True, (255, 0, 0), 3)
        # 保存图像
        cv2.imwrite(merge_image_path, img)

    @staticmethod
    # polys(list)转masks(ndarry)
    def convert_polys_to_masks(polys, width, height):
        masks = np.zeros((width, height), dtype=np.int32)
        obj = np.array(polys, dtype=np.int32)
        cv2.fillPoly(masks, obj, 1)
        return masks

    @staticmethod
    # masks(ndarry)转polys(list)#
    #  通过opencv的轮廓检测（等值线捕获）方法
    # 返回[[[x1,y1],[x2,y2]...[xn,yn]],[...]],[[x1,y1],[x2,y2]...[xn,yn]],[...]],...]
    def convert_masks_to_polys(masks, tolerance=0.001):
        polygon_points = []
        # masks = cv2.imdecode(np.fromfile(mask_file, dtype=np.uint8), 0)

        masks = masks.astype(np.uint8)

        # 二值图边缘线，只能读单波段的灰度图
        contours, _ = cv2.findContours(masks, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            epsilon = tolerance * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) < 5:
                continue
            each_poly_points = []
            for point in approx:
                x, y = point[0].tolist()
                each_poly_points.append([x, y])
            polygon_points.append(each_poly_points)
        return polygon_points

        # def close_contour(contour):
        #     if not np.array_equal(contour[0], contour[-1]):
        #         contour = np.vstack((contour, contour[0]))
        #     return contour
        #
        # """Converts a binary mask to COCO polygon representation
        # Args:
        # binary_mask: a 2D binary numpy array where '1's represent the object
        # tolerance: Maximum distance from original points of polygon to approximated
        # polygonal chain. If tolerance is 0, the original coordinate array is returned.
        # """
        # polygons = []
        # # pad mask to close contours of shapes which start and end at an edge
        # padded_binary_mask = np.pad(masks, pad_width=1, mode='constant', constant_values=0)
        # contours = measure.find_contours(padded_binary_mask, 0.5)
        # contours = np.subtract(contours, 1)
        # for contour in contours:
        #     contour = close_contour(contour)
        #     contour = measure.approximate_polygon(contour, tolerance)
        #     if len(contour) < 3:
        #         continue
        #     contour = np.flip(contour, axis=1)
        #     segmentation = contour.ravel().tolist()
        #     # after padding and subtracting 1 we may get -0.5 points in our segmentation
        #     segmentation = [0 if i < 0 else i for i in segmentation]
        #     polygons.append(segmentation)
        # return polygons

    @staticmethod
    # mask(ndarry)转poly(list)#
    #  通过opencv的轮廓检测（等值线捕获）方法
    # 返回[[x1,y1],[x2,y2]...[xn,yn]],[...]]]
    def convert_mask_to_poly(mask, tolerance=0.001):
        each_poly_points = []
        # masks = cv2.imdecode(np.fromfile(mask_file, dtype=np.uint8), 0)

        mask = mask.astype(np.uint8)

        # 二值图边缘线，只能读单波段的灰度图
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            contour = contours[0]
            epsilon = tolerance * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) >= 5:
                for point in approx:
                    x, y = point[0].tolist()
                    each_poly_points.append([x, y])
        return each_poly_points

    @staticmethod
    # masks数据(ndarry)转mask二值图
    def convert_masks_to_image(mask_image_path, mask_data):
        color = np.array([30 / 255, 144 / 255, 255 / 255, 0.6])
        h, w = mask_data.shape[-2:]
        # 转换为是三维数组,mask为True,采用样色值(0.11764706,0.56470588,1.0,0.6),mask为False，设置为（0,0,0,0）
        mask_image = mask_data.reshape(h, w, 1) * color.reshape(1, 1, -1)
        # 生成一个灰度图图片
        # 获取图片每个通道数据
        r, g, b, a = mask_image[:, :, 0], mask_image[:, :, 1], mask_image[:, :, 2], mask_image[:, :, 3]
        # 目标是255白色，背景是0黑色
        mask_image_grey = np.where(r > 0, 255, 0)
        # 保存mask的二值图
        cv2.imwrite(mask_image_path, mask_image_grey)

    @staticmethod
    # mask二值图转shp
    # 通过gdal的栅格转矢量的方法
    def convert_mask_image_to_shape(mask_image_path: str, mask_image_tranform: list, file_prefix: str,
                                    shp_file_path: str,
                                    logger: object) -> str:
        """
        将mask二值图转换为shp文件，通过GDAL的栅格转矢量方法

        :param mask_image_path: 二值图栅格文件路径.
        :param mask_image_tranform: 栅格文件的几何转换六参数，格式为[左上角点坐标X, x方向的分辨, 旋转系数:如果为0就是标准的正北向图像, 左上角点坐标Y, 旋转系数:如果为0就是标准的正北向图像, Y方向的分辨率].
        :param file_prefix: 文件前缀
        :param shp_file_path: 转换的shp文件路径
        :param logger: 日志对象
        :return: 转后的矢量shp路径
        """
        if logger is not None:
            logger.info("对二值图转换为shp文件")
        shp_file_dir = os.path.join(os.getcwd(), "shp", "convert_by_mask")
        if not os.path.exists(shp_file_dir):
            os.makedirs(shp_file_dir)
        (file_pre_path, temp_filename) = os.path.split(mask_image_path)
        (shot_name, file_ext) = os.path.splitext(temp_filename)
        if shp_file_path is None:
            shp_file_path = os.path.join(shp_file_dir, '{}.shp'.format(shot_name))
        if logger is not None:
            logger.info("shp文件路径：{}".format(shp_file_path))
        RsToolsOperatoer.raster_to_vector(mask_image_path, mask_image_tranform, shp_file_path, "ESRI Shapefile")
        return shp_file_path

    @staticmethod
    # mask二值图转polygon
    # 通过opencv的轮廓检测（等值线捕获）方法
    # 返回[[[x1,y1],[x2,y2]...[xn,yn]],[...]],[[x1,y1],[x2,y2]...[xn,yn]],[...]]...]
    def convert_mask_image_to_polygon(mask_file, epsilon_factor=0.001):
        polygon_points = []
        # binary_mask = cv2.imread(mask_file, cv2.IMREAD_GRAYSCALE)
        binary_mask = cv2.imdecode(np.fromfile(mask_file, dtype=np.uint8), 0)
        # 二值图边缘线，只能读单波段的灰度图
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            epsilon = epsilon_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) < 5:
                continue
            each_poly_points = []
            for point in approx:
                x, y = point[0].tolist()
                each_poly_points.append([x, y])
            polygon_points.append(each_poly_points)
        return polygon_points

    @staticmethod
    # mask二值图转polygon
    # 通过opencv的轮廓检测（等值线捕获）方法
    # 提高轮廓检测的精度，你可以使用更高级的图像分割技术，如分水岭分割或GrabCut算法
    # 返回[[[x1,y1],[x2,y2]...[xn,yn]],[...]]
    def convert_mask_image_to_polygon2(mask_file, epsilon_factor=0.001):

        # 定义GrabCut函数
        def grabcut_segmentation(image):
            # 创建掩码
            mask = np.zeros(image.shape[:2], np.uint8)
            # 创建背景和前景模型
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)
            # 定义矩形区域（这里使用整个图像）
            rect = (0, 0, image.shape[1], image.shape[0])
            # 运行GrabCut算法
            cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
            # 提取前景
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            return mask2

        polygon_points = []
        binary_mask = cv2.imread(mask_file, cv2.IMREAD_GRAYSCALE)

        segmented_mask = grabcut_segmentation(binary_mask)
        # 使用轮廓检测来提取多边形坐标
        contours, _ = cv2.findContours(segmented_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            epsilon = epsilon_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) < 5:
                continue
            each_poly_points = []
            for point in approx:
                x, y = point[0].tolist()
                each_poly_points.append([x, y])
            polygon_points.append(each_poly_points)
        return polygon_points

    @staticmethod
    # 多边形转换为mask二值图
    # polygons:[[(x1,y1),(x2,y2)...(xn,yn)],[...]]
    def convert_polygon_to_mask_image(img_file, mask_file, polygons):
        def get_image_size(image_file):
            with Image.open(image_file) as img:
                width, height = img.size
                return width, height

        image_width, image_height = get_image_size(img_file)
        image_shape = (image_height, image_width)
        binary_mask = np.zeros(image_shape, dtype=np.uint8)
        for polygon_points in polygons:
            np_polygon = np.array(polygon_points, np.int8)
            np_polygon = np_polygon.reshape((-1, 1, 2))
            cv2.fillPoly(binary_mask, [np_polygon], color=255)
        cv2.imwrite(mask_file, binary_mask)

    @staticmethod
    # 多边形转为mask二值图方法2
    # polygons:['x1,y1,x2,y2...xn,yn','x1,y1,x2,y2...xn,yn'...]
    def convert_polygon_to_mask_image_2(img_file, mask_file, polygons):
        ImageHelper.build_binary_image(img_file, mask_file, polygons)

    @staticmethod
    # 处理AI提取结果，删除多余的提取框
    # 非极大值抑制(Non-maximum supression)简称NMS,其作用是去除冗余的检测框,去冗余手段是剔除与极大值重叠较多的检测框结果
    def handle_ai_result_of_nms(input_shp_path):
        # 注册所有驱动
        gdal.AllRegister()
        # 解决中文路径乱码问题
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
        driver = ogr.GetDriverByName('ESRI Shapefile')
        origin_pFeatureDataset = driver.Open(input_shp_path, 1)
        origin_pFeaturelayer = origin_pFeatureDataset.GetLayer(0)
        copy_pFeatureDataset = ShpFileOperator.get_clone_shape(input_shp_path)
        copy_pFeaturelayer = copy_pFeatureDataset.GetLayer(0)
        copy_featureLayerNum = copy_pFeaturelayer.GetFeatureCount(0)
        # 获取要素
        for t in range(0, copy_featureLayerNum):
            copy_ofeature = copy_pFeaturelayer.GetFeature(t)
            copy_geom = copy_ofeature.GetGeometryRef()
            # copy_geom_wkt = copy_geom.ExportToWkt()
            del_id_list = AIHelper.__find_overlap_feature(copy_geom, origin_pFeaturelayer, 0.5)
        del_id_list_only = ListHelper.remove_same_item(del_id_list)
        for del_id in del_id_list_only:
            print("----正在删除要素ID:" + str(del_id))
            origin_pFeaturelayer.DeleteFeature(del_id)
        strSQL = "REPACK " + str(origin_pFeaturelayer.GetName())
        origin_pFeatureDataset.ExecuteSQL(strSQL, None, "")
        origin_pFeaturelayer = None
        origin_pFeatureDataset = None

    @staticmethod
    # 删除发现的重叠要素
    # 指阈值以上的重叠区域的两个要素，删除面积小的那个要素
    def __find_overlap_feature(search_geom, originFeaturelayer, threshold=0.5):
        del_id_list = []
        origin_feature_num = originFeaturelayer.GetFeatureCount(0)
        search_geom_id = 0
        origin_geom_wkt_list = []
        origin_geom_id_list = []

        for t in range(0, origin_feature_num):
            originFeature = originFeaturelayer.GetFeature(t)
            origin_geom_id = originFeature.GetFID()
            origin_geom = originFeature.GetGeometryRef()
            origin_geom_wkt = origin_geom.ExportToWkt()
            origin_geom_wkt_list.append(origin_geom_wkt)
            origin_geom_id_list.append(origin_geom_id)
            if search_geom.Equal(origin_geom):
                search_geom_id = origin_geom_id

        print("当前查询要素{}".format(str(search_geom_id)))
        if search_geom_id in del_id_list:
            print("----要素{}已经在删除序列中，不再进行重叠查询".format(str(search_geom_id)))
        else:
            for t in range(0, len(origin_geom_wkt_list)):
                origin_geom_id = origin_geom_id_list[t]
                origin_geom = ogr.CreateGeometryFromWkt(origin_geom_wkt_list[t])
                if search_geom_id not in del_id_list:
                    if search_geom_id == origin_geom_id:
                        continue
                    elif search_geom.Contains(origin_geom):
                        if origin_geom_id not in del_id_list:
                            del_id_list.append(origin_geom_id)
                            print("----要素{}包含要素{},删除要素{}".format(str(search_geom_id), str(origin_geom_id),
                                                                           str(origin_geom_id)))
                    elif search_geom.Within(origin_geom):
                        if search_geom_id not in del_id_list:
                            del_id_list.append(search_geom_id)
                            print("----要素{}包含要素{},删除要素{}".format(str(origin_geom_id), str(search_geom_id),
                                                                           str(search_geom_id)))
                    elif search_geom.Intersect(origin_geom):
                        inter_geom = search_geom.Intersection(origin_geom)
                        if ShpFileOperator.get_area_envelop(inter_geom) / ShpFileOperator.get_area_envelop(
                                search_geom) > threshold or ShpFileOperator.get_area_envelop(
                            inter_geom) / ShpFileOperator.get_area_envelop(origin_geom) > threshold:
                            if ShpFileOperator.get_area_envelop(search_geom) > ShpFileOperator.get_area_envelop(
                                    origin_geom):
                                if origin_geom_id not in del_id_list:
                                    del_id_list.append(origin_geom_id)
                                    print("----要素{}与要素{}大面积相交,删除要素{}".format(str(search_geom_id),
                                                                                           str(origin_geom_id),
                                                                                           str(origin_geom_id)))
                            else:
                                if search_geom_id not in del_id_list:
                                    del_id_list.append(search_geom_id)
                                    print("----要素{}与要素{}大面积相交,删除要素{}".format(str(search_geom_id),
                                                                                           str(origin_geom_id),
                                                                                           str(search_geom_id)))
        return del_id_list

    # --------------------------------------
    # -----停用方法------
    # ------------------------------------
    @staticmethod
    # (方法名停用，但为了兼容以前的系统，不做删除)
    # mask二值图转shp
    # 通过gdal的栅格转矢量的方法
    def convert_mask_to_shape(mask_image_path: str, mask_image_tranform: list, file_prefix: str, shp_file_path: str,
                              logger: object) -> str:
        """
        将mask二值图转换为shp文件，通过GDAL的栅格转矢量方法

        :param mask_image_path: 二值图栅格文件路径.
        :param mask_image_tranform: 栅格文件的几何转换六参数，格式为[左上角点坐标X, x方向的分辨, 旋转系数:如果为0就是标准的正北向图像, 左上角点坐标Y, 旋转系数:如果为0就是标准的正北向图像, Y方向的分辨率].
        :param file_prefix: 文件前缀
        :param shp_file_path: 转换的shp文件路径
        :param logger: 日志对象
        :return: 转后的矢量shp路径
        """
        if logger is not None:
            logger.info("对二值图转换为shp文件")
        shp_file_dir = os.path.join(os.getcwd(), "shp", "convert_by_mask")
        if not os.path.exists(shp_file_dir):
            os.makedirs(shp_file_dir)
        (file_pre_path, temp_filename) = os.path.split(mask_image_path)
        (shot_name, file_ext) = os.path.splitext(temp_filename)
        if shp_file_path is None:
            shp_file_path = os.path.join(shp_file_dir, '{}.shp'.format(shot_name))
        if logger is not None:
            logger.info("shp文件路径：{}".format(shp_file_path))
        RsToolsOperatoer.raster_to_vector(mask_image_path, mask_image_tranform, shp_file_path, "ESRI Shapefile")
        return shp_file_path

    @staticmethod
    # (方法名停用，但为了兼容以前的系统，不做删除)
    # 多边形转换为mask二值图
    # polygons:[[(x1,y1),(x2,y2)...(xn,yn)],[...]]
    def polygon_to_mask(img_file, mask_file, polygons):
        def get_image_size(image_file):
            with Image.open(image_file) as img:
                width, height = img.size
                return width, height

        image_width, image_height = get_image_size(img_file)
        image_shape = (image_height, image_width)
        binary_mask = np.zeros(image_shape, dtype=np.uint8)
        for polygon_points in polygons:
            np_polygon = np.array(polygon_points, np.int8)
            np_polygon = np_polygon.reshape((-1, 1, 2))
            cv2.fillPoly(binary_mask, [np_polygon], color=255)
        cv2.imwrite(mask_file, binary_mask)

    @staticmethod
    # (方法名停用，但为了兼容以前的系统，不做删除)
    # 多边形转为mask二值图方法2
    # polygons:['x1,y1,x2,y2...xn,yn','x1,y1,x2,y2...xn,yn'...]
    def polygon_to_mask2(img_file, mask_file, polygons):
        ImageHelper.build_binary_image(img_file, mask_file, polygons)

    @staticmethod
    # (方法名停用，但为了兼容以前的系统，不做删除)
    # mask二值图转polygon
    # 通过opencv的轮廓检测（等值线捕获）方法
    # 返回[[[x1,y1],[x2,y2]...[xn,yn]],[...]],[[x1,y1],[x2,y2]...[xn,yn]],[...]]...]
    def mask_to_polygon(mask_file, epsilon_factor=0.001):
        polygon_points = []
        # binary_mask = cv2.imread(mask_file, cv2.IMREAD_GRAYSCALE)
        binary_mask = cv2.imdecode(np.fromfile(mask_file, dtype=np.uint8), 0)
        # 二值图边缘线，只能读单波段的灰度图
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            epsilon = epsilon_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) < 5:
                continue
            each_poly_points = []
            for point in approx:
                x, y = point[0].tolist()
                each_poly_points.append([x, y])
            polygon_points.append(each_poly_points)
        return polygon_points

    @staticmethod
    # (方法名停用，但为了兼容以前的系统，不做删除)
    # mask二值图转polygon
    # 通过opencv的轮廓检测（等值线捕获）方法
    # 提高轮廓检测的精度，你可以使用更高级的图像分割技术，如分水岭分割或GrabCut算法
    # 返回[[[x1,y1],[x2,y2]...[xn,yn]],[...]]
    def mask_to_polygon2(mask_file, epsilon_factor=0.001):

        # 定义GrabCut函数
        def grabcut_segmentation(image):
            # 创建掩码
            mask = np.zeros(image.shape[:2], np.uint8)
            # 创建背景和前景模型
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)
            # 定义矩形区域（这里使用整个图像）
            rect = (0, 0, image.shape[1], image.shape[0])
            # 运行GrabCut算法
            cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
            # 提取前景
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            return mask2

        polygon_points = []
        binary_mask = cv2.imread(mask_file, cv2.IMREAD_GRAYSCALE)

        segmented_mask = grabcut_segmentation(binary_mask)
        # 使用轮廓检测来提取多边形坐标
        contours, _ = cv2.findContours(segmented_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            epsilon = epsilon_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            if len(approx) < 5:
                continue
            each_poly_points = []
            for point in approx:
                x, y = point[0].tolist()
                each_poly_points.append([x, y])
            polygon_points.append(each_poly_points)
        return polygon_points


if __name__ == '__main__':
    box_points_list = [[660.2479858398438, 280.0595397949219, 701.6737060546875, 320.72589111328125],
                       [559.2014770507812, 221.1412353515625, 592.9896240234375, 254.13226318359375],
                       [477.0056457519531, 309.0809020996094, 505.49664306640625, 337.82135009765625],
                       [517.1990966796875, 194.45872497558594, 551.4634399414062, 227.95953369140625],
                       [721.5293579101562, 321.0753173828125, 757.498291015625, 354.52435302734375],
                       [546.3658447265625, 345.80072021484375, 577.3338012695312, 374.9428405761719],
                       [340.64898681640625, 68.33817291259766, 362.81884765625, 90.0564956665039],
                       [776.2349853515625, 355.7030029296875, 812.4939575195312, 390.0914306640625],
                       [617.8046264648438, 401.6883850097656, 648.726318359375, 430.9305419921875],
                       [682.6495361328125, 443.026123046875, 716.3787231445312, 474.0211486816406],
                       [470.60125732421875, 164.7460479736328, 504.5323181152344, 197.5280303955078],
                       [119.45063018798828, 467.18597412109375, 141.20028686523438, 488.65411376953125],
                       [594.6969604492188, 420.94134521484375, 607.457275390625, 433.63287353515625],
                       [247.9298095703125, 497.092041015625, 259.27301025390625, 508.6060485839844]]
    image_path = 'G:\\AI\\test_data\\storagetank\\storagetank1.jpeg'
    jgw_path = 'G:\\AI\\test_data\\storagetank\\storagetank1.jgw'
    shp_path = 'G:\\AI\\test_data\\storagetank\\storagetank1.shp'

    image_env = RsToolsOperatoer.get_env_of_pic(image_path, jgw_path)
    AIHelper.convert_yolo_box_to_shape(box_points_list, image_path, image_env, 4326, shp_path)
