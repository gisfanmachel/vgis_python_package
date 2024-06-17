#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2021/12/4 14:10
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : aiSettings.py
# @Descr   : AI样本处理
# @Software: PyChar
import glob
import json
import os
import random
import shutil
import xml.etree.ElementTree as ET
from collections import namedtuple
from enum import Enum
from xml.dom.minidom import Document

import cv2
import imgaug as ia
import imgaug.augmenters as iaa
import numpy as np
from PIL import Image
from PIL import ImageDraw
from cityscapesscripts.helpers.annotation import Annotation
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
from shapely.geometry import Polygon

from vgis_aiutils.aiTools import AIHelper
from vgis_utils.vgis_file.fileTools import FileHelper
from vgis_utils.vgis_file.fileTools import JsonHelper
from vgis_utils.vgis_image.imageTools import ImageHelper
from vgis_utils.vgis_string.stringTools import StringHelper


# 目标类型
class Object_Name_Enum(Enum):
    # 飞机
    airplane = "airplane"
    # 船舶
    boat = "boat"
    # 汽车
    car = "car"
    # 烟囱
    chimney = "chimney"
    # 油罐
    storagetank = "storagetank"


# 标注类型
class Label_Data_Type_Enum(Enum):
    # 水平矩形框
    hbb = "hbb"
    # 旋转矩形框
    obb = "obb"
    # 多边形框
    mask = "mask"


# 算法类型
# 目标检测是指分类并定位图片中物体的任务。
# 实例分割是指分类，分割图片物体的任务。
# 全景分割是统一了语义分割（对图像的每个像素进行分类）和实例分割（检测出对象实例并进行分割）的检测任务。
# 语义分割的主要目的是把一张图片里的所有像素进行分类.

class Alg_Type_Enum(Enum):
    # YOLOV8 目标检测
    yolov8_obj_det = "yolov8_obj_det"
    # YOLOV8 实例分割
    yolov8_ins_seg = "yolov8_ins_seg"
    # mmdetectionv3 目标检测
    mmdetv3_obj_det = "mmdetv3_obj_det"
    # mmdetectionv3 实例分割
    mmdetv3_ins_seg = "mmdetv3_ins_seg"
    # mmdetectionv3 全景分割
    mmdetv3_pan_seg = "mmdetv3_pan_seg"
    # mmdetectionv1 语义分割
    mmsegv1_sem_seg = "mmsegv1_sem_seg"


# 算法模型
class Alg_Model_Enum(Enum):
    class YoloV3:
        pass

    class YoloV8:
        class Insseg:
            yolo_seg = "yolo_v8-insseg-yolo_seg"

        class Objdet:
            yolo_hbb = "yolo_v8-objdet-yolo_hbb"
            yolo_obb = "yolo_v8-objdet-yolo_obb"

    class MmdetV3:
        class Insseg:
            mask_rcnn = "mmdet_v3-insseg-mask_rcnn_mask"
            cascade_mask_rcnn = "mmdet_v3-insseg-cascade_mask_rcnn_mask"

        class Objdet:
            rtmdet = "mmdet_v3-objdet-rtmdet_hbb"
            cascade_rcnn = "mmdet_v3-objdet-cascade_rcnn_hbb"
            faster_rcnn = "mmdet_v3-objdet-faster_rcnn_hbb"

        class Panseg:
            panoptic_fpn = "mmdet_v3-panseg-panoptic_fpn_mask"

    class MmsegV1:
        class Semseg:
            segformer = "mmseg_v1-semseg-segformer_mask"
            deeplab = "mmseg_v1-semseg-deeplab_mask"
            pspnet = "mmseg_v1-semseg-pspnet_mask"

    # 武汉珞珈
    class LuojiaNet:
        pass

    # 中科院空天灵眸
    class RingMo:
        pass


# 标注目录
class Label_Json_Dir_Name_Enum(Enum):
    # 水平矩形标注
    hbb_label_json_dir_name = "HBBLabels"
    # 旋转矩形标注
    obb_label_json_dir_name = "OBBLabels"
    # 多边形标注
    mask_label_json_dir_name = "MaskLabels"


# 标注二值图目录
class Label_Binaray_Image_Dir_Name_Enum(Enum):
    # 水平矩形标注转为二值图图片
    hbb_binary_image_dir_name = "HBBBianryImages"
    # 旋转矩形标注转为二值图图片
    obb_binary_image_dir_name = "OBBBianryImages"
    # 多边形标注转为二值图图片
    mask_binary_image_dir_name = "MaskBianryImages"


# YOLOV8目录
class YoloV8_Dir_Name_Enum(Enum):
    # labelme矩形标注转换为yolov8目标检测coco8标注
    yolo_object_detect_txt_dir_name = "YoloV8ObjdetTxts"
    # YOLOV8目标检测训练数据的目录结构
    yolo_object_detect_train_dir_name = "Yolov8ObjdetTrain"
    # labelme多边形标注转换为yolov8实例分割coco8标注
    yolo_instance_segment_txt_dir_name = "YoloV8InssegTxts"
    # YOLOV8实例分割训练数据的目录结构
    yolo_instance_segment_train_dir_name = "Yolov8InssegTrain"


# MmdetectionV3目录
class MmdetV3_Dir_Name_Enum(Enum):
    # labelme标注转换为mmdetv3目标检测coco2017标注--暂时无用
    mmdet_object_detect_json_dir_name = "MmdetV3ObjdetJson"
    # MmdetectionV3目标检测训练数据的目录结构
    mmdet_object_detect_train_dir_name = "MmdetV3ObjdetTrain"
    # 存放labelme标注，转换为mmdetv3实例分割coco2017标注--暂时无用
    mmdet_instance_segment_json_dir_name = "MmdetV3InssegJson"
    # MmdetectionV3实例分割训练数据的目录结构
    mmdet_instance_segment_train_dir_name = "MmdetV3InssegTrain"
    # labelme标注转换为mmdetv3语义分割coco2017标注--暂时无用
    mmdet_panorama_segment_json_dir_name = "MmdetV3PansegJson"
    # MmdetectionV3语义分割训练数据的目录结构
    mmdet_panorama_segment_train_dir_name = "MmdetV3PansegTrain"


# MmsegmentaionV1目录
class MmsegV1_Dir_Name_Enum(Enum):
    # labelme标注转换为mmsegv1语义分割Cityscapes标注
    mmseg_semantics_segment_json_dir_name = "MmsegV1SemseqJson"
    # MmsegmentationV1语义分割训练数据的目录结构构
    mmdet_semantics_segment_train_dir_name = "MmsegV1SemsegTrain"


# AI样本格式转换
# 创建外部类对象 fileFormatConverter = FileFormatConverter()
class FileFormatConverter:
    def __init__(self):
        pass

    # 样本图片后缀
    img_suffix = ['jpg', 'jpeg', 'JPG', 'JPEG', 'gif', 'GIF', 'png', 'PNG', 'bmp', 'BMP']

    # 样本图片目录
    sample_image_dir_name = "SampleImages"

    ## 创建嵌套类对象 sample503Converter = FileFormatConverter.Sample503Converter()
    class Sample503Converter:
        def __init__(self):
            pass

        @staticmethod
        # 503样本xml像素坐标转成地理坐标
        def coord_convert_kshxml(xml_file_path, tif_minx, tif_miny, tif_maxx, tif_maxy, new_xml_file_path):

            # root = ET.Element('annotation')
            # ET.SubElement(root, 'folder').text = os.path.dirname(output_dir)
            # ET.SubElement(root, 'filename').text = os.path.basename(image_path)
            # size = ET.SubElement(root, 'size')
            # ET.SubElement(size, 'width').text = str(image_width)
            # ET.SubElement(size, 'height').text = str(image_height)
            # ET.SubElement(size, 'depth').text = '3'
            # xml_string = ET.tostring(root, encoding='utf-8')
            # dom = minidom.parseString(xml_string)
            # formatted_xml = dom.toprettyxml(indent='  ')
            # with open(output_dir, 'w',encoding='utf-8') as f:
            #     f.write(formatted_xml)
            #
            print(xml_file_path)
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            auxiliaryInfo = root.find('auxiliaryInfo')
            image_width = auxiliaryInfo.find('image_width').text
            image_height = auxiliaryInfo.find('image_height').text
            items = root.find('items')
            for objinfo in items.findall('objectInfo'):
                pointitems = objinfo.find('points').findall('item')
                for pointitem in pointitems:
                    pointx = pointitem.findall('item')[0]
                    pointy = pointitem.findall('item')[1]
                    pointx.text = str(tif_minx + (tif_maxx - tif_minx) / float(image_width) * float(pointx.text))
                    pointy.text = str(tif_maxy - (tif_maxy - tif_miny) / float(image_height) * float(pointy.text))
            # root为修改后的root
            new_tree = ET.ElementTree(root)
            # 保存为xml文件
            new_tree.write(new_xml_file_path, encoding='utf-8')

        # 503样本xml转换为json
        @staticmethod
        def kshxml2Json1(xml_file_path, json_file_path, epsg_code):
            json_file_dict = {}
            json_file_dict["type"] = "FeatureCollection"
            json_file_dict["crs"] = {'type': 'name', 'properties': {'name': 'EPSG:' + str(epsg_code)}}
            featureArray = []
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            items = root.find('items')
            objnum = 0
            for objinfo in items.findall('objectInfo'):
                objnum = objnum + 1
                label1 = objinfo.find('label1')
                label2 = objinfo.find('label2')
                label3 = objinfo.find('label3')
                label4 = objinfo.find('label4')
                label5 = objinfo.find('label5')
                label6 = objinfo.find('label6')
                objname = label6
                if objname == "":
                    objname = label5
                if objname == "":
                    objname = label4
                if objname == "":
                    objname = label3
                if objname == "":
                    objname = label2
                if objname == "":
                    objname = label1
                pointitems = objinfo.find('points').findall('item')
                coordsArray = []
                point1x = pointitems[0].findall('item')[0].text
                point1y = pointitems[0].findall('item')[1].text
                point2x = pointitems[1].findall('item')[0].text
                point2y = pointitems[1].findall('item')[1].text
                point3x = pointitems[2].findall('item')[0].text
                point3y = pointitems[2].findall('item')[1].text
                point4x = pointitems[3].findall('item')[0].text
                point4y = pointitems[3].findall('item')[1].text
                point1Array = [point1x, point1y]
                point2Array = [point2x, point2y]
                point3Array = [point3x, point3y]
                point4Array = [point4x, point4y]
                pointsArray = []
                pointsArray.append(point1Array)
                pointsArray.append(point2Array)
                pointsArray.append(point3Array)
                pointsArray.append(point4Array)
                pointsArray.append(point1Array)
                coordsArray.append(pointsArray)
                feature_dict = {'type': 'Feature', 'id': objnum,
                                'geometry': {'type': 'Polygon', 'coordinates': coordsArray},
                                'properties': {'FID': objnum, 'Id': 0, 'XH': objname, 'type': ''}}
                featureArray.append(feature_dict)
            json_file_dict["features"] = featureArray
            FileHelper.write_json_obj_into_file(json_file_dict, json_file_path)

        # 503样本xml转换为json
        @staticmethod
        def kshxml2Json(xml_file_path, json_file_path, epsg_code):
            json_file_dict = {}
            json_file_dict["type"] = "FeatureCollection"
            json_file_dict["crs"] = {"type": "name", "properties": {"name": "EPSG:" + str(epsg_code)}}
            featureArray = []
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            items = root.find('items')
            objnum = 0
            for objinfo in items.findall('objectInfo'):
                objnum = objnum + 1
                label1 = objinfo.find('label1')
                label2 = objinfo.find('label2')
                label3 = objinfo.find('label3')
                label4 = objinfo.find('label4')
                label5 = objinfo.find('label5')
                label6 = objinfo.find('label6')
                objname = label6.text
                if objname is None or objname == '':
                    objname = label5.text
                if objname is None or objname == '':
                    objname = label4.text
                if objname is None or objname == '':
                    objname = label3.text
                if objname is None or objname == '':
                    objname = label2.text
                if objname is None or objname == '':
                    objname = label1.text
                pointitems = objinfo.find('points').findall('item')
                coordsArray = []
                point1x = pointitems[0].findall('item')[0].text
                point1y = pointitems[0].findall('item')[1].text
                point2x = pointitems[1].findall('item')[0].text
                point2y = pointitems[1].findall('item')[1].text
                point3x = pointitems[2].findall('item')[0].text
                point3y = pointitems[2].findall('item')[1].text
                point4x = pointitems[3].findall('item')[0].text
                point4y = pointitems[3].findall('item')[1].text
                point1Array = [point1x, point1y]
                point2Array = [point2x, point2y]
                point3Array = [point3x, point3y]
                point4Array = [point4x, point4y]
                pointsArray = []
                pointsArray.append(point1Array)
                pointsArray.append(point2Array)
                pointsArray.append(point3Array)
                pointsArray.append(point4Array)
                pointsArray.append(point1Array)
                coordsArray.append(pointsArray)
                feature_dict = {"type": "Feature", "id": objnum,
                                "geometry": {"type": "Polygon", "coordinates": coordsArray},
                                "properties": {"FID": objnum, "Id": 0, "XH": objname, "type": ""}}
                featureArray.append(feature_dict)
            json_file_dict["features"] = featureArray

            FileHelper.write_json_obj_into_file(json_file_dict, json_file_path)

    class PascalVocConverter:
        def __init__(self):
            pass

        # pascalVoc转yolo
        @staticmethod
        def pascalVoc2Yolo(xml_file_path, class_file_path, txt_file_path):
            classes_dict = {}
            # class_file_path= "classes.names"
            with open(class_file_path, encoding='utf-8') as f:
                for idx, line in enumerate(f.readlines()):
                    class_name = line.strip()
                    classes_dict[class_name] = idx

            width, height, objects = FileFormatConverter.PascalVocConverter.__pascal_xml_reader(xml_file_path,
                                                                                                "ALLClass")

            lines = []
            # 标注内容的类别、归一化后的中心点x坐标，归一化后的中心点y坐标，归一化后的目标框宽度w，归一化后的目标况高度h（此处归一化指的是除以图片宽和高）
            for obj in objects:
                x, y, x2, y2 = obj['bbox']
                class_name = obj['name']
                label = classes_dict[class_name]
                cx = (x2 + x) * 0.5 / width
                cy = (y2 + y) * 0.5 / height
                w = (x2 - x) * 1. / width
                h = (y2 - y) * 1. / height
                line = "%s %.6f %.6f %.6f %.6f\n" % (label, cx, cy, w, h)
                lines.append(line)

            # txt_name = filename.replace(".xml", ".txt").replace("labels_voc", "labels")
            with open(txt_file_path, "w", encoding='utf-8') as f:
                f.writelines(lines)

        # 获取pascal文件中的class类型
        @staticmethod
        def get_class_name_array_in_pascal(file_path):
            class_name_array = []
            tree = ET.parse(file_path)
            for obj in tree.findall('object'):
                class_name = obj.find('name').text
                if class_name not in class_name_array:
                    class_name_array.append(class_name)
            return class_name_array

        # 解析pascal文件中的数据,根据指定class
        @staticmethod
        def __pascal_xml_reader(file_path, class_name):
            """ Parse a PASCAL VOC xml file """
            tree = ET.parse(file_path)
            size = tree.find('size')
            width = int(size.find('width').text)
            height = int(size.find('height').text)
            objects = []
            for obj in tree.findall('object'):
                obj_struct = {}
                if class_name == "ALLClass" or class_name == obj.find('name').text:
                    obj_struct['name'] = obj.find('name').text
                    if obj.find('bndbox') is not None:
                        bbox = obj.find('bndbox')
                        obj_struct['bbox'] = [int(bbox.find('xmin').text),
                                              int(bbox.find('ymin').text),
                                              int(bbox.find('xmax').text),
                                              int(bbox.find('ymax').text)]
                    if obj.find('polygon') is not None:
                        points = obj.find('polygon').iter()
                        obj_struct['polygon'] = []
                        for point in points:
                            if point.text != "\n":
                                obj_struct['polygon'].append(point.text)
                    objects.append(obj_struct)
            return width, height, objects

        # pascalVoc转labelme
        # class_name为AllClass表示全部class,否则按指定class类型类转换
        @staticmethod
        def pascalVoc2Labelme(xml_file_path, pic_file_path, json_file_path, class_name):
            width, height, objects = FileFormatConverter.PascalVocConverter.__pascal_xml_reader(xml_file_path,
                                                                                                class_name)
            shapes_array = []
            if len(objects) > 0:
                for obj in objects:
                    class_name = obj['name']
                    shape_dict = {}
                    shape_dict["label"] = class_name
                    points_array = []
                    if "bbox" in obj:
                        x, y, x2, y2 = obj['bbox']
                        points_array = [[float(x), float(y)], [float(x2), float(y)], [float(x2), float(y2)],
                                        [float(x), float(y2)]]
                    if "polygon" in obj:
                        for index in range(len(obj["polygon"])):
                            if index % 2 == 0:
                                points_array.append([float(obj["polygon"][index])] + [float(obj["polygon"][index + 1])])
                    shape_dict["points"] = points_array
                    shape_dict["group_id"] = None
                    shape_dict["shape_type"] = "polygon"
                    shape_dict["flags"] = {}
                    shapes_array.append(shape_dict)
                json_file_dict = FileFormatConverter.LablemeHelper.__build_lableme_json_dict(shapes_array,
                                                                                             pic_file_path)
                FileHelper.write_json_obj_into_file(json_file_dict, json_file_path)
            else:
                print("当前图片的标签数据为空")

    class LablemeHelper:
        def __init__(self):
            pass

        @staticmethod
        # 处理label名称
        def handle_label_name(old_label_name):
            new_label_name = old_label_name
            # 针对烟囱样本采集时classname不标准的情况
            if old_label_name == "yc":
                new_label_name = "chimney"
            # 针对油罐采集时classname不标准的情况
            if old_label_name == "oiltank":
                new_label_name = "storagetank"
            if old_label_name == "warcraft":
                new_label_name = "ship"
            return new_label_name

        # 获取labelme的标签文件里的所有label
        @staticmethod
        def get_all_label_of_labelme_json_files(json_dir_path):
            label_list = []
            all_json_list = FileHelper.get_file_list(json_dir_path, ["json"])
            print("样本json数量总共有{}个".format(len(all_json_list)))
            for i in range(len(all_json_list)):
                input_json_file_path = all_json_list[i]
                # 读取LabelMe格式的JSON标注数据
                with open(input_json_file_path, 'r', encoding='utf-8') as f:
                    labelme_data = json.load(f)
                    shapes = labelme_data["shapes"]
                    for shape in shapes:
                        label = shape["label"]
                        if label not in label_list:
                            label_list.append(label)
            return label_list

        @staticmethod
        def get_categorys_by_labellist(label_list):
            categorie_list = []
            for i in range(len(label_list)):
                obj = {}
                obj["id"] = i
                obj["name"] = FileFormatConverter.LablemeHelper.handle_label_name(label_list[i])
                if obj not in categorie_list:
                    categorie_list.append(obj)
            return categorie_list

        @staticmethod
        def get_categroy_id_by_category_name(category_name, categorie_list):
            return_id = 0
            for i in range(len(categorie_list)):
                if categorie_list[i]["name"] == category_name:
                    return_id = i
                    break
            return return_id

        # labelme转yolo hbb
        @staticmethod
        def labelme2YoloHbb(json_file_path, class_file_path, txt_file_path):
            classes_dict = {}
            # class_file_path= "classes.names"
            with open(class_file_path, encoding='utf-8') as f:
                for idx, line in enumerate(f.readlines()):
                    class_name = line.strip()
                    classes_dict[class_name] = idx
            lines = []
            with open(json_file_path, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)
                image_width = json_data.get("imageWidth")
                image_height = json_data.get("imageHeight")
                shapes_array = json_data.get("shapes")
                # 标注内容的类别、归一化后的中心点x坐标，归一化后的中心点y坐标，归一化后的目标框宽度w，归一化后的目标况高度h（此处归一化指的是除以图片宽和高）
                for shape_obj in shapes_array:
                    class_name = FileFormatConverter.LablemeHelper.handle_label_name(shape_obj.get("label"))
                    points_array = shape_obj.get("points")
                    x, y, x2, y2 = FileFormatConverter.RectHelper.get_envelop_of_points(points_array)
                    label = classes_dict[class_name]
                    cx = (x2 + x) * 0.5 / image_width
                    cy = (y2 + y) * 0.5 / image_height
                    w = (x2 - x) * 1. / image_width
                    h = (y2 - y) * 1. / image_height
                    line = "%s %.6f %.6f %.6f %.6f\n" % (label, cx, cy, w, h)
                    lines.append(line)
            # txt_name = filename.replace(".xml", ".txt").replace("labels_voc", "labels")
            with open(txt_file_path, "w", encoding='utf-8') as f:
                f.writelines(lines)

        # lableme转yolo obb或 yolo seg
        @staticmethod
        def labelme2YoloPolygon(json_file_path, class_file_path, txt_file_path):
            classes_dict = {}
            # class_file_path= "classes.names"
            with open(class_file_path, encoding='utf-8') as f:
                for idx, line in enumerate(f.readlines()):
                    class_name = line.strip()
                    classes_dict[class_name] = idx
            lines = []
            with open(json_file_path, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)
                image_width = json_data.get("imageWidth")
                image_height = json_data.get("imageHeight")
                shapes_array = json_data.get("shapes")
                # 标注内容的类别、归一化后的中心点x坐标，归一化后的中心点y坐标，归一化后的目标框宽度w，归一化后的目标况高度h（此处归一化指的是除以图片宽和高）
                for shape_obj in shapes_array:
                    class_name = FileFormatConverter.LablemeHelper.handle_label_name(shape_obj.get("label"))
                    points_array = shape_obj.get("points")
                    label = classes_dict[class_name]
                    line = "%s " % (label)
                    for point in points_array:
                        tmpx = point[0]
                        tmpy = point[1]
                        line += "%.6f %.6f " % (tmpx, tmpy)
                    # line +="\n"
                    lines.append(line)
            # txt_name = filename.replace(".xml", ".txt").replace("labels_voc", "labels")
            with open(txt_file_path, "w", encoding='utf-8') as f:
                f.writelines(lines)

        # labelme转coco2017
        @staticmethod
        def labelme2Coco2017(labelme_json_dir_path, label_suffix, coco2017_dir_path, alg_type):
            coco2017_json_file_path = os.path.join(coco2017_dir_path, "annotation_coco.json")
            all_lableme_list = FileHelper.get_file_list(labelme_json_dir_path, [label_suffix])
            print("样本lable图片数量总共有{}个".format(len(all_lableme_list)))
            # 得到所有的label类别
            label_list = FileFormatConverter.LablemeHelper.get_all_label_of_labelme_json_files(labelme_json_dir_path)
            # categories = [{
            #     'id': 0,
            #     'name': 'balloon'
            # }]
            categories = FileFormatConverter.LablemeHelper.get_categorys_by_labellist(label_list)
            annotations = []
            images = []
            obj_count = 0
            for i in range(len(all_lableme_list)):
                labelme_file_path = all_lableme_list[i]
                print("{}/{} 转换标签：{}".format(i + 1, len(all_lableme_list), labelme_file_path))
                with open(labelme_file_path, 'r', encoding='utf-8') as fp:
                    json_data = json.load(fp)
                    image_width = json_data.get("imageWidth")
                    image_height = json_data.get("imageHeight")
                    image_path = json_data.get("imagePath")
                    images.append(
                        dict(id=i, file_name=image_path, height=image_height, width=image_width))
                    shapes_array = json_data.get("shapes")
                    # 标注内容的类别、归一化后的中心点x坐标，归一化后的中心点y坐标，归一化后的目标框宽度w，归一化后的目标况高度h（此处归一化指的是除以图片宽和高）
                    for shape_obj in shapes_array:
                        label_name = FileFormatConverter.LablemeHelper.handle_label_name(shape_obj.get("label"))
                        category_id = FileFormatConverter.LablemeHelper.get_categroy_id_by_category_name(label_name,
                                                                                                         categories)
                        points_array = shape_obj.get("points")
                        # 获取box
                        x_min, y_min, x_max, y_max = FileFormatConverter.RectHelper.get_envelop_of_points(
                            points_array)

                        if alg_type == Alg_Type_Enum.mmdetv3_obj_det.value:
                            data_anno = dict(
                                image_id=i,
                                id=obj_count,
                                category_id=category_id,
                                bbox=[x_min, y_min, x_max - x_min, y_max - y_min],
                                area=(x_max - x_min) * (y_max - y_min),
                                iscrowd=0)

                        if alg_type == Alg_Type_Enum.mmdetv3_ins_seg.value:
                            # 获取mask
                            poly_array = []
                            for each_point in points_array:
                                poly_array.append(each_point[0])
                                poly_array.append(each_point[1])
                            poly = [poly_array]
                            data_anno = dict(
                                image_id=i,
                                id=obj_count,
                                category_id=category_id,
                                bbox=[x_min, y_min, x_max - x_min, y_max - y_min],
                                area=(x_max - x_min) * (y_max - y_min),
                                segmentation=poly,
                                iscrowd=0)

                        annotations.append(data_anno)
                        obj_count += 1

            coco_json_data = dict(
                images=images,
                annotations=annotations,
                categories=categories)
            JsonHelper.write_json_obj_into_file(coco_json_data, coco2017_json_file_path)

        # labelme转citycapes
        @staticmethod
        def labelme2Citycapes(labelme_json_dir_path, label_suffix, citycapes_dir_path, alg_type, category_name):

            all_lableme_list = FileHelper.get_file_list(labelme_json_dir_path, [label_suffix])
            print("样本lable图片数量总共有{}个".format(len(all_lableme_list)))
            for i in range(len(all_lableme_list)):
                labelme_file_path = all_lableme_list[i]
                labelme_file_name = os.path.splitext(os.path.split(labelme_file_path)[1])[0]
                citycapes_json_file_path = os.path.join(citycapes_dir_path,
                                                        "{}.json".format(labelme_file_name))
                print("{}/{} 转换标签：{}".format(i + 1, len(all_lableme_list), labelme_file_path))
                # 生成_polygons.json
                with open(labelme_file_path, 'r', encoding='utf-8') as fp:
                    json_data = json.load(fp)
                    image_width = json_data.get("imageWidth")
                    image_height = json_data.get("imageHeight")
                    shapes_array = json_data.get("shapes")
                    objects = []
                    for shape_obj in shapes_array:
                        label_name = FileFormatConverter.LablemeHelper.handle_label_name(shape_obj.get("label"))
                        points_array = shape_obj.get("points")
                        if alg_type == Alg_Type_Enum.mmsegv1_sem_seg.value:
                            object = dict(label=label_name, polygon=points_array)
                            objects.append(object)
                    citycapes_json_data = dict(
                        imgHeight=image_height,
                        imgWidth=image_width,
                        objects=objects)
                    JsonHelper.write_json_obj_into_file(citycapes_json_data, citycapes_json_file_path)
                # 将json转为png
                citycapes_lable_file_path = os.path.join(citycapes_dir_path,
                                                         "{}.png".format(labelme_file_name))
                annotation = Annotation()
                annotation.fromJsonFile(citycapes_json_file_path)
                name2label = FileFormatConverter.CityScapesHelper.build_name2label(category_name)
                labelImg = FileFormatConverter.CityScapesHelper.createLabelImage(annotation, "color", name2label)
                labelImg.save(citycapes_lable_file_path)

        # 对实例采集的labmel数据转换为OBB旋转矩形框labelme数据
        @staticmethod
        def handle_mask_label_data_to_obb_label_data(mask_data_dir, rect_data_dir, label_suffix):
            if not os.path.exists(rect_data_dir):
                os.makedirs(rect_data_dir)
            all_json_list = FileHelper.get_file_list(mask_data_dir, [label_suffix])
            print("样本json数量总共有{}个".format(len(all_json_list)))
            for i in range(len(all_json_list)):
                input_json_file_path = all_json_list[i]
                file_name = os.path.splitext(os.path.split(input_json_file_path)[1])[0]
                print("转换为obb:{}/{},file_name:{}".format(i + 1, len(all_json_list), file_name))
                out_json_file_path = os.path.join(rect_data_dir, os.path.split(input_json_file_path)[1])
                FileFormatConverter.LablemeHelper.convert_seg_points_to_obb_of_labelme(input_json_file_path,
                                                                                       out_json_file_path)

        # 对obb采集的labmel数据转换为HBB旋转矩形框labelme数据
        @staticmethod
        def handle_obb_label_data_to_hbb_label_data(obb_data_dir, hbb_data_dir, label_suffix):
            if not os.path.exists(hbb_data_dir):
                os.makedirs(hbb_data_dir)
            all_json_list = FileHelper.get_file_list(obb_data_dir, [label_suffix])
            print("样本json数量总共有{}个".format(len(all_json_list)))
            for i in range(len(all_json_list)):
                input_json_file_path = all_json_list[i]
                file_name = os.path.splitext(os.path.split(input_json_file_path)[1])[0]
                print("转换为hbb:{}/{},file_name:{}".format(i + 1, len(all_json_list), file_name))
                out_json_file_path = os.path.join(obb_data_dir, os.path.split(input_json_file_path)[1])
                FileFormatConverter.LablemeHelper.convert_obb_points_to_hbb_of_labelme(input_json_file_path,
                                                                                       out_json_file_path)

        # 对实例采集的labmel数据转换为HBB旋转矩形框labelme数据
        @staticmethod
        def handle_mask_label_data_to_hbb_label_data(mask_data_dir, hbb_data_dir, label_suffix):
            if not os.path.exists(hbb_data_dir):
                os.makedirs(hbb_data_dir)
            all_json_list = FileHelper.get_file_list(mask_data_dir, [label_suffix])
            print("样本json数量总共有{}个".format(len(all_json_list)))
            for i in range(len(all_json_list)):
                input_json_file_path = all_json_list[i]
                file_name = os.path.splitext(os.path.split(input_json_file_path)[1])[0]
                print("转换为hbb:{}/{},file_name:{}".format(i + 1, len(all_json_list), file_name))
                out_json_file_path = os.path.join(hbb_data_dir, os.path.split(input_json_file_path)[1])
                FileFormatConverter.LablemeHelper.convert_seg_points_to_hbb_of_labelme(input_json_file_path,
                                                                                       out_json_file_path)

        @staticmethod
        # obb labelme转换为HBB水平转矩形labelme
        def convert_obb_points_to_hbb_of_labelme(intput_json_file_path, output_json_file_path):

            json_data = JsonHelper.get_json_obj_by_file(intput_json_file_path)
            shapes_array = json_data.get("shapes")
            for shape_obj in shapes_array:
                points_array = shape_obj.get("points")
                new_points_array = FileFormatConverter.RectHelper.get_horizon_rect_of_points_array(points_array)
                shape_obj["points"] = new_points_array
            JsonHelper.write_json_obj_into_file(json_data, output_json_file_path)

        @staticmethod
        # 实例点labelme转换为OBB转旋转矩形labelme
        def convert_seg_points_to_obb_of_labelme(intput_json_file_path, output_json_file_path):

            json_data = JsonHelper.get_json_obj_by_file(intput_json_file_path)
            shapes_array = json_data.get("shapes")
            for shape_obj in shapes_array:
                points_array = shape_obj.get("points")
                new_points_array = FileFormatConverter.RectHelper.get_rotate_rect_of_points_array(points_array)
                # # 这里处理下，对超过4个点的坐标进行去除，因为obb只需要四个点，不用首尾相同
                # if len(new_points_array) > 4:
                #     new_points_array = new_points_array[:4]
                shape_obj["points"] = new_points_array
            JsonHelper.write_json_obj_into_file(json_data, output_json_file_path)

        @staticmethod
        # 实例点labelme转换为HBB水平转矩形labelme
        def convert_seg_points_to_hbb_of_labelme(intput_json_file_path, output_json_file_path):

            json_data = JsonHelper.get_json_obj_by_file(intput_json_file_path)
            shapes_array = json_data.get("shapes")
            for shape_obj in shapes_array:
                points_array = shape_obj.get("points")
                new_points_array = FileFormatConverter.RectHelper.get_horizon_rect_of_points_array(points_array)
                shape_obj["points"] = new_points_array
            JsonHelper.write_json_obj_into_file(json_data, output_json_file_path)

        @staticmethod
        # 加载自己的数据集，只需要所有 labelme 标注出来的 json 文件即可
        def load_labelme_dataset(path):
            dataset = []
            for json_file_path in glob.glob("{}/*json".format(path)):
                with open(json_file_path, 'r', encoding='utf8') as fp:
                    json_data = json.load(fp)
                    image_width = json_data.get("imageWidth")
                    image_height = json_data.get("imageHeight")
                    shapes_array = json_data.get("shapes")
                    for shape_obj in shapes_array:
                        points_array = shape_obj.get("points")
                        xmin, ymin, xmax, ymax = FileFormatConverter.RectHelper.get_envelop_of_points(
                            points_array)
                        # 偏移量
                        xmin = int(xmin) / image_width
                        ymin = int(ymin) / image_height
                        xmax = int(xmax) / image_width
                        ymax = int(ymax) / image_height
                        xmin = np.float64(xmin)
                        ymin = np.float64(ymin)
                        xmax = np.float64(xmax)
                        ymax = np.float64(ymax)
                        # 将Anchor的宽和高放入dateset，运行kmeans获得Anchor
                        dataset.append([xmax - xmin, ymax - ymin])
            return np.array(dataset)

        @staticmethod
        # 内部函数，构建labelme的json字典数据
        def __build_lableme_json_dict(shapes_array, pic_file_path):

            json_file_dict = {}
            json_file_dict["version"] = "4.6.0"
            json_file_dict["flags"] = {}
            json_file_dict["shapes"] = shapes_array
            json_file_dict["imagePath"] = FileHelper.get_file_name(pic_file_path)
            # 图像的base64取值有问题
            # json_file_dict["imageData"] = imageOperator.convert2Base64(pic_file_path)
            json_file_dict["imageData"] = None
            img = Image.open(pic_file_path)
            json_file_dict["imageHeight"] = img.height
            json_file_dict["imageWidth"] = img.width
            return json_file_dict

        @staticmethod
        # 根据labelme标签数据生成二值图
        def build_binary_image_by_lableme(input_pic_file_path, result_pic_file_path, json_file_path):
            while_region_array = []
            with open(json_file_path, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)
                shapes_array = json_data.get("shapes")
                for shape_obj in shapes_array:
                    points_array = shape_obj.get("points")
                    region_data = []
                    for each_point in points_array:
                        region_data.append(int(each_point[0]))
                        region_data.append(int(each_point[1]))
                    while_region_array.append(region_data)
            ImageHelper.build_binary_image(input_pic_file_path, result_pic_file_path, while_region_array)

        @staticmethod
        # 将二值图mask图片转成labelme标签文件
        # 有个问题，如果mask是连着的，生成的json也是连接的，没法分成一个一个单独的标注目标
        def build_labelme_json_by_binary_image(label_name, mask_pic_file_path, labelme_json_file_path):
            # [[(x1,y1),(x2,y2)...(xn,yn)],[...]]
            polygons = AIHelper.mask_to_polygon(mask_pic_file_path)
            shapes_array = []
            for polygon in polygons:
                shape_dict = {}
                shape_dict["label"] = label_name
                shape_dict["points"] = polygon
                shape_dict["group_id"] = None
                shape_dict["shape_type"] = "polygon"
                shape_dict["flags"] = {}
                shapes_array.append(shape_dict)
            if len(shapes_array) > 0:
                json_file_dict = FileFormatConverter.LablemeHelper.__build_lableme_json_dict(shapes_array,
                                                                                             mask_pic_file_path)
                FileHelper.write_json_obj_into_file(json_file_dict, labelme_json_file_path)
            else:
                print("当前二值图的标签数据为空")

        # 将图片和标注同步，多余的图片和标注删除
        @staticmethod
        def syn_pic_and_label(pic_dir_path, pic_suffix, label_dir_path, lalel_suffix):
            pic_file_names = os.listdir(pic_dir_path)
            for temp in pic_file_names:
                pic_file = os.path.join(pic_dir_path, temp)
                fname, ext = os.path.splitext(pic_file)
                base_name = os.path.basename(fname)
                label_name = base_name + "." + lalel_suffix
                if not FileHelper.is_has_file_in_dir(label_dir_path, label_name):
                    print("{}图片没有标签文件".format(pic_file))
                    # os.remove(pic_file)
            label_file_names = os.listdir(label_dir_path)
            for temp in label_file_names:
                label_file = os.path.join(label_dir_path, temp)
                fname, ext = os.path.splitext(label_file)
                base_name = os.path.basename(fname)
                pic_name = base_name + "." + pic_suffix
                if not FileHelper.is_has_file_in_dir(pic_dir_path, pic_name):
                    print("{}标签没有图片文件".format(label_file))
                    # os.remove(label_file)

        # 处理包含lableme标签的样本数据，生成二值图
        @staticmethod
        def handle_sample_data_contains_labelme(sample_type, origin_pic_dir_path, json_dir_path):
            binary_pic_dir_path = os.path.join(origin_pic_dir_path, "BianryImages")
            if not os.path.exists(binary_pic_dir_path):
                os.makedirs(binary_pic_dir_path)
            print("开始处理{}数据，工作目录为{}".format(sample_type, origin_pic_dir_path))
            all_pic_list = FileHelper.get_file_list(origin_pic_dir_path, FileFormatConverter.img_suffix)
            print("样本图片数量总共有{}个".format(len(all_pic_list)))
            for i in range(len(all_pic_list)):
                pic_file_path = all_pic_list[i]
                pic_file_name_prefix = FileHelper.get_file_name_prefix(pic_file_path)
                pic_file_name = FileHelper.get_file_name(pic_file_path)
                print("当前位置为{},处理样本图片为{},".format(str(i + 1) + "/" + str(len(all_pic_list)), pic_file_name))
                json_file_path = os.path.join(json_dir_path, pic_file_name_prefix + ".json")
                # 有可能图片个数大于标签个数
                if os.path.exists(json_file_path):
                    binary_pic_file_path = os.path.join(binary_pic_dir_path, pic_file_name)
                    FileFormatConverter.LablemeHelper.build_binary_image_by_lableme(pic_file_path, binary_pic_file_path,
                                                                                    json_file_path)
                else:
                    print("该样本图片没有标签，需要在labelme软件中制作标签")

        # 处理包含lableme标签的样本数据，生成二值图
        @staticmethod
        def make_binaray_image_of_sample_data_contains_labelme(origin_pic_dir_path, binary_pic_dir_path, label_suffix,
                                                               json_dir_path):
            all_pic_list = FileHelper.get_file_list(origin_pic_dir_path, FileFormatConverter.img_suffix)
            print("样本图片数量总共有{}个".format(len(all_pic_list)))
            for i in range(len(all_pic_list)):
                pic_file_path = all_pic_list[i]
                pic_file_name_prefix = FileHelper.get_file_name_prefix(pic_file_path)
                pic_file_name = FileHelper.get_file_name(pic_file_path)
                print("当前位置为{},处理样本图片为{},".format(str(i + 1) + "/" + str(len(all_pic_list)), pic_file_name))
                json_file_path = os.path.join(json_dir_path, pic_file_name_prefix + "." + label_suffix)
                # 有可能图片个数大于标签个数
                if os.path.exists(json_file_path):
                    binary_pic_file_path = os.path.join(binary_pic_dir_path, pic_file_name)
                    FileFormatConverter.LablemeHelper.build_binary_image_by_lableme(pic_file_path, binary_pic_file_path,
                                                                                    json_file_path)
                else:
                    print("该样本图片没有标签，需要在labelme软件中制作标签")

        # 处理包含lableme标签的样本数据，生成二值图
        # 针对文件夹内的各个子文件夹进行添加后缀重命名，并统一复制到合并的子文件夹中，并生成二值图
        # 比如烟囱样本目录下，分了高烟囱，矮烟囱等子目录，需要汇总
        @staticmethod
        def handle_sample_data_contains_labelme_by_split_dir(sample_type, origin_data_path):
            print("开始处理{}数据，工作目录为{}".format(sample_type, origin_data_path))
            # 为每个子目录里的文件增加后缀
            sub_fix = 0
            dirs = os.listdir(origin_data_path)
            for eachdir in dirs:
                each_dir_path = os.path.join(origin_data_path, eachdir)
                print("开始为目录{}进行文件增加后缀{}".format(each_dir_path, "_" + str(sub_fix)))
                FileHelper.add_subfix_on_file_name(each_dir_path, "_" + str(sub_fix))
                sub_fix = sub_fix + 1
            # 新建相关文件夹
            total_data_path = os.path.join(origin_data_path, sample_type + "_汇总")
            if os.path.exists(total_data_path):
                shutil.rmtree(total_data_path)
            os.makedirs(total_data_path)
            origin_pic_dir_path = os.path.join(total_data_path, "SampleImages")
            if os.path.exists(origin_pic_dir_path):
                shutil.rmtree(origin_pic_dir_path)
            os.makedirs(origin_pic_dir_path)
            label_json_dir_path = os.path.join(total_data_path, "LabelImages")
            if os.path.exists(label_json_dir_path):
                shutil.rmtree(label_json_dir_path)
            os.makedirs(label_json_dir_path)
            binary_pic_dir_path = os.path.join(total_data_path, "BianryImages")
            if os.path.exists(binary_pic_dir_path):
                shutil.rmtree(binary_pic_dir_path)
            os.makedirs(binary_pic_dir_path)

            dirs = os.listdir(origin_data_path)
            for eachdir in dirs:
                if "_汇总" not in eachdir:
                    each_dir_path = os.path.join(origin_data_path, eachdir)
                    print("开始将目录{}内图像文件拷贝到目录{}".format(each_dir_path, origin_pic_dir_path))
                    FileHelper.sfile_to_dfile(each_dir_path, ".jpg", origin_pic_dir_path)
                    print("开始将目录{}内标签文件拷贝到目录{}".format(each_dir_path, label_json_dir_path))
                    FileHelper.sfile_to_dfile(each_dir_path, ".json", label_json_dir_path)

            # 针对有标签和图片没有一致的处理
            FileFormatConverter.LablemeHelper.syn_pic_and_label(origin_pic_dir_path, "jpg", label_json_dir_path, "json")
            # 基于标签数据制作二值图
            all_pic_list = FileHelper.get_file_list(origin_pic_dir_path, FileFormatConverter.img_suffix)
            print("样本图片数量总共有{}个".format(len(all_pic_list)))
            for i in range(len(all_pic_list)):
                pic_file_path = all_pic_list[i]
                pic_file_name_prefix = FileHelper.get_file_name_prefix(pic_file_path)
                pic_file_name = FileHelper.get_file_name(pic_file_path)
                print(
                    "当前位置为{},处理样本图片为{},生成二值图".format(str(i + 1) + "/" + str(len(all_pic_list)),
                                                                      pic_file_name))
                json_file_path = os.path.join(label_json_dir_path, pic_file_name_prefix + ".json")
                binary_pic_file_path = os.path.join(binary_pic_dir_path, pic_file_name)
                FileFormatConverter.LablemeHelper.build_binary_image_by_lableme(pic_file_path, binary_pic_file_path,
                                                                                json_file_path)

        # 处理labelme的json里的标签名为统一的标签名
        @staticmethod
        def handle_labelme_json_lable(json_dir):
            all_file_list = FileHelper.get_file_list(json_dir, ["json"])
            for i in range(len(all_file_list)):
                json_file_path = all_file_list[i]
                with open(json_file_path, 'r', encoding='utf8') as fp:
                    json_data = json.load(fp)
                shapes_array = json_data.get("shapes")
                for shape_obj in shapes_array:
                    shape_obj["label"] = FileFormatConverter.LablemeHelper.handle_label_name(shape_obj.get("label"))
                with open(json_file_path, 'w', encoding='utf-8') as outfile:
                    json.dump(json_data, outfile)

    class OpenmmLabHelper:
        def __init__(self):
            pass

        @staticmethod
        def get_config_file_by_alg_model(alg_model):
            config_path = None
            if alg_model == "mmdet_v3-insseg-mask_rcnn_mask":
                config_path = "mask_rcnn/mask-rcnn_r50-caffe_fpn_ms-poly-3x_coco.py"
            elif alg_model == "mmdet_v3-objdet-cascade_rcnn_hbb":
                config_path = "cascade_rcnn/cascade-rcnn_r101_fpn_1x_coco.py"
            elif alg_model == "mmdet_v3-insseg-cascade_mask_rcnn_mask":
                config_path = "cascade_rcnn/cascade-mask-rcnn_r50_fpn_ms-3x_coco.py"
            return config_path

        @staticmethod
        def get_checkpoint_file_by_alg_model(alg_model, object_name):
            checkpoint_path = None
            dirname = alg_model.split("-")[0].split("_")[0] + "-" + alg_model.split("-")[1]
            if alg_model == "mmdet_v3-insseg-mask_rcnn_mask":
                checkpoint_path = "{}/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth".format(
                    dirname)
            elif alg_model == "mmdet_v3-objdet-cascade_rcnn_hbb":
                checkpoint_path = "{}/cascade_rcnn_r101_fpn_1x_coco_20200317-0b6a2fbf.pth".format(
                    dirname)
            elif alg_model == "mmdet_v3-insseg-cascade_mask_rcnn_mask":
                checkpoint_path = "{}/cascade_mask_rcnn_r50_caffe_fpn_mstrain_3x_coco_20210707_002651-6e29b3a6.pth".format(
                    dirname)
            return checkpoint_path

        @staticmethod
        def get_workdir_by_alg_model(alg_model, object_name):
            workdir = None
            # mmdet-insseg-cascade_rcnn_mask_airplane
            alg_name = alg_model.split("-")[2]
            workdir = "{}_{}".format(alg_name, object_name)
            return workdir

        @staticmethod
        def get_new_config_name_by_alg_model(alg_model, object_name):

            dirname = alg_model.split("-")[0].split("_")[0] + "-" + alg_model.split("-")[1]
            new_config_path = "{}/{}/{}.py".format(dirname, object_name,
                                                   FileFormatConverter.OpenmmLabHelper.get_workdir_by_alg_model(
                                                       alg_model, object_name))
            return new_config_path

        @staticmethod
        def is_has_mask_result(alg_model):
            is_has_mask = False
            if alg_model.split("_")[-1] == "mask":
                is_has_mask = True
            return is_has_mask

        @staticmethod
        # alg_model = "mmdet_v3-objdet-cascade_rcnn_hbb"
        # object_name = "airplane"
        def config_builder(alg_model, object_name):
            """
            #!/usr/bin/python3.9
            # -*- coding: utf-8 -*-
            @Project :mmdetection_main
            @File    :build_config.py
            @IDE     :PyCharm
            @Author  :chenxw
            @Date    :2024/1/16 14:25
            @Descr:
            """
            from mmengine import Config

            # alg_model = "mmdet_v3-insseg-mask_rcnn_mask"
            alg_model = "mmdet_v3-objdet-cascade_rcnn_hbb"
            object_name = "airplane"

            # 读取算法配置文件基类
            cfg = Config.fromfile(
                '../configs/{}'.format(FileFormatConverter.OpenmmLabHelper.get_config_file_by_alg_model(alg_model)))
            # 定义数据目录
            data_root = './data/mmdet-insseg/airplane'
            # 定义数据类别和调色板
            metainfo = {
                'classes': ('transportplane', 'fighter', 'helicopter', 'transport'),
                'palette': [(101, 205, 228), (240, 128, 128), (154, 205, 50), (34, 139, 34)]
            }
            # 定义数据分类数量
            num_classes = len(metainfo["classes"])
            # 定义训练的epochs
            max_epochs = 100
            # 定义训练数据(单卡)的batch size
            train_batch_size_per_gpu = 16
            # 加载训练数据(batch)的线程数
            train_num_workers = 4
            # 定义验证数据(单卡)的batch size
            val_batch_size_per_gpu = 1
            # 加载验证数据(batch)的线程数
            val_num_workers = 2
            # 根据训练batch数调整训练的学习率， 原来的0.004 是 8卡x32 的学习率
            base_lr = train_batch_size_per_gpu * 0.004 / (32 * 8)
            # 定义要采用的COCO预训练权重
            load_from = './data/{}'.format(get_checkpoint_file_by_alg_model(alg_model, object_name))  # noqa

            # 设置输出的工作目录
            work_dirs = '/root/work/mmdetection-main/work_dirs/{}'.format(
                FileFormatConverter.OpenmmLabHelper.get_workdir_by_alg_model(alg_model, object_name))

            # Modify dataset classes and color
            cfg.metainfo = metainfo

            # Modify dataset type and path
            cfg.data_root = data_root

            cfg.train_dataloader.batch_size = train_batch_size_per_gpu
            cfg.train_dataloader.num_workers = train_num_workers
            cfg.train_dataloader.pin_memory = False
            cfg.train_dataloader.dataset.ann_file = 'train/annotation_coco.json'
            cfg.train_dataloader.dataset.data_root = cfg.data_root
            cfg.train_dataloader.dataset.data_prefix.img = 'train/'
            cfg.train_dataloader.dataset.metainfo = cfg.metainfo

            cfg.val_dataloader.batch_size = val_batch_size_per_gpu
            cfg.val_dataloader.num_workers = val_num_workers
            cfg.val_dataloader.dataset.ann_file = 'val/annotation_coco.json'
            cfg.val_dataloader.dataset.data_root = cfg.data_root
            cfg.val_dataloader.dataset.data_prefix.img = 'val/'
            cfg.val_dataloader.dataset.metainfo = cfg.metainfo

            cfg.test_dataloader = cfg.val_dataloader

            # Modify metric config
            cfg.val_evaluator.ann_file = cfg.data_root + '/' + 'val/annotation_coco.json'
            cfg.test_evaluator = cfg.val_evaluator

            # box框的分类数
            if isinstance(cfg.model.roi_head.bbox_head, dict):
                cfg.model.roi_head.bbox_head.num_classes = num_classes
            elif isinstance(cfg.model.roi_head.bbox_head, list):
                for bbox_head in cfg.model.roi_head.bbox_head:
                    bbox_head.num_classes = num_classes

            if FileFormatConverter.OpenmmLabHelper.is_has_mask_result(alg_model):
                # mask的分类数
                if isinstance(cfg.model.roi_head.mask_head, dict):
                    cfg.model.roi_head.mask_head.num_classes = num_classes
                elif isinstance(cfg.model.roi_head.mask_head, list):
                    for mask_head in cfg.model.roi_head.mask_head:
                        mask_head.num_classes = num_classes

            # We can still the pre-trained Mask RCNN model to obtain a higher performance
            cfg.load_from = load_from

            # Set up working dir to save files and logs.
            cfg.work_dir = work_dirs

            # We can set the evaluation interval to reduce the evaluation times
            cfg.train_cfg.val_interval = 5
            cfg.train_cfg.max_epochs = max_epochs

            # We can set the checkpoint saving interval to reduce the storage cost
            cfg.default_hooks.checkpoint.interval = 5
            # cfg.default_hooks.checkpoint.max_keep_ckpts = 2
            # cfg.default_hooks.checkpoint.save_best = 'auto'

            # cfg.default_hooks.logger.type = 'LoggerHook'
            cfg.default_hooks.logger.interval = 5

            # cfg.param_scheduler[0].type = 'LinearLR'
            # cfg.param_scheduler[0].start_factor = 1.0e-5
            # cfg.param_scheduler[0].by_epoch = False
            # cfg.param_scheduler[0].begin = 0
            # cfg.param_scheduler[0].end = 1000
            #
            # cfg.param_scheduler[1].type = 'CosineAnnealingLR'
            # cfg.param_scheduler[1].eta_min = base_lr * 0.05
            # cfg.param_scheduler[1].begin = max_epochs // 2
            # cfg.param_scheduler[1].end = max_epochs
            # cfg.param_scheduler[1].T_max = max_epochs // 2
            # cfg.param_scheduler[1].by_epoch = True
            # cfg.param_scheduler[1].convert_to_iter_based = True

            # param_scheduler = [
            #     dict(
            #         type='LinearLR',  # 使用线性学习率预热
            #         start_factor=0.001, # 学习率预热的系数
            #         by_epoch=False,  # 按 iteration 更新预热学习率
            #         begin=0,  # 从第一个 iteration 开始
            #         end=500),  # 到第 500 个 iteration 结束
            #     dict(
            #         type='MultiStepLR',  # 在训练过程中使用 multi step 学习率策略
            #         by_epoch=True,  # 按 epoch 更新学习率
            #         begin=0,   # 从第一个 epoch 开始
            #         end=12,  # 到第 12 个 epoch 结束
            #         milestones=[8, 11],  # 在哪几个 epoch 进行学习率衰减
            #         gamma=0.1)  # 学习率衰减系数
            # ]

            # 之前训练的报错，缺少type，是指这个地方，没有写 , type='OptimWrapper'
            cfg.optim_wrapper.optimizer.lr = base_lr
            # cfg.optim_wrapper = dict(optimizer=dict(lr=base_lr, momentum=0.9, type='SGD', weight_decay=0.0001), type='OptimWrapper')

            # # Change the evaluation metric since we use customized dataset.
            # cfg.evaluation.metric = 'mAP'
            # # We can set the evaluation interval to reduce the evaluation times
            # cfg.evaluation.interval = 12
            # # We can set the checkpoint saving interval to reduce the storage cost
            # cfg.checkpoint_config.interval = 12
            #
            # # Set seed thus the results are more reproducible
            # cfg.seed = 0
            # set_random_seed(0, deterministic=False)
            # cfg.gpu_ids = range(1)
            #
            #
            # # We can also use tensorboard to log the training process
            # cfg.visualizer.vis_backends.append({"type":'TensorboardVisBackend'})

            # ------------------------------------------------------

            config = f'./' + FileFormatConverter.OpenmmLabHelper.get_new_config_name_by_alg_model(alg_model,
                                                                                                  object_name)
            with open(config, 'w') as f:
                f.write(cfg.pretty_text)

        # 初始化mmdetv3,mmsegv1需要的数据目录
        @staticmethod
        def init_mm_data_dir(dest_path, category_name):
            mm_train_data_dir = os.path.join(dest_path, "data", category_name, "train")
            mm_val_data_dir = os.path.join(dest_path, "data", category_name, "val")
            mm_test_data_dir = os.path.join(dest_path, "data", category_name, "test")
            FileHelper.mkdirs(
                [mm_train_data_dir, mm_val_data_dir, mm_test_data_dir])

        @staticmethod
        # 生成mmdetection训练算法配置文件
        def write_config_file_of_mm_train_old(mmdet_train_dir_path, mmdet_config_file_path, category_name, label_list,
                                              alg_mode):
            if alg_mode == Alg_Model_Enum.MmdetV3.Insseg.mask_rcnn:
                base_config_py = "mask_rcnn/mask-rcnn_r50-caffe_fpn_ms-poly-3x_coco.py"
                base_pth_file_name = "mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco_bbox_mAP-0.408__segm_mAP-0.37_20200504_163245-42aa3d00.pth"
                base_pth_download = 'https://download.openmmlab.com/mmdetection/v2.0/mask_rcnn/mask_rcnn_r50_caffe_fpn_mstrain-poly_3x_coco/{}'.format(
                    base_pth_file_name)
                base_pth_path = os.path.join(os.path.join(mmdet_train_dir_path, "data", category_name),
                                             "{}".format(base_pth_file_name))
                data_sub_dir_name = "mmdet-insseg-mm_rcnn"
                # 在外面用第三方软件下载，这里不下载了
                # FileFormatConverter.OpenmmLabHelper.download_pth(base_pth_download, base_pth_path)
                load_from = './data/{}/{}/{}'.format(data_sub_dir_name, category_name, base_pth_file_name)

            classes = tuple(label_list)
            palette_list = [
                (101, 205, 228), (240, 128, 128), (154, 205, 50), (34, 139, 34),
                (139, 0, 0), (255, 165, 0), (255, 0, 255), (255, 255, 0),
                (29, 123, 243), (0, 255, 255), (187, 255, 255), (174, 238, 238), (150, 205, 205), (102, 139, 139),
                (152, 245, 255), (142, 229, 238), (122, 197, 205),
            ]
            palette = palette_list[:len(label_list)]
            config_info = f"""
            _base_ = '../../../configs/{base_config_py}'
            data_root = './data/{data_sub_dir_name}/{category_name}/'

            # 非常重要
            metainfo = {{
                # # 类别名，注意 classes 需要是一个 tuple，因此即使是单类，
                # # 你应该写成 `cat,` 很多初学者经常会在这犯错
                # 'classes': ('cat',),
                # 'palette': [
                #     (220, 20, 60),
                # ]

                'classes':{classes},
                'palette': {palette}
            }}
            num_classes = {len(label_list)}

            # 训练 100 epoch
            max_epochs = 100
            # 训练单卡 bs= 16
            train_batch_size_per_gpu = 16
            # 可以根据自己的电脑修改
            train_num_workers = 4

            # 验证集 batch size 为 1
            val_batch_size_per_gpu = 1
            val_num_workers = 2

            # RTMDet 训练过程分成 2 个 stage，第二个 stage 会切换数据增强 pipeline
            # num_epochs_stage2 = 5

            # batch 改变了，学习率也要跟着改变， 0.004 是 8卡x32 的学习率
            base_lr = 16 * 0.004 / (32*8)

            # 采用 COCO 预训练权重
            load_from = '{load_from}'  # noqa

            # model = dict(
                # 考虑到数据集太小，且训练时间很短，我们把 backbone 完全固定
                # 用户自己的数据集可能需要解冻 backbone
                # backbone=dict(frozen_stages=4),
                # 不要忘记修改 num_classes
                # bbox_head=dict(dict(num_classes=num_classes)))
            # 我们还需要更改 head 中的 num_classes 以匹配数据集中的类别数
            # 目标检测  box_head, 实例分割 mask_head
            # 如果数据集太小，可以将backbone完全固定，backbone=dict(frozen_stages=4)
            model = dict(
            roi_head=dict(
                bbox_head=dict(num_classes=num_classes), mask_head=dict(num_classes=num_classes)))

            # 数据集不同，dataset 输入参数也不一样
            train_dataloader = dict(
                batch_size=train_batch_size_per_gpu,
                num_workers=train_num_workers,
                pin_memory=False,
                dataset=dict(
                    data_root=data_root,
                    metainfo=metainfo,
                    ann_file='train/annotation_coco.json',
                    data_prefix=dict(img='train/')))

            val_dataloader = dict(
                batch_size=val_batch_size_per_gpu,
                num_workers=val_num_workers,
                dataset=dict(
                    metainfo=metainfo,
                    data_root=data_root,
                    ann_file='val/annotation_coco.json',
                    data_prefix=dict(img='val/')))

            test_dataloader = val_dataloader

            # 默认的学习率调度器是 warmup 1000，但是 cat 数据集太小了，需要修改 为 30 iter
            param_scheduler = [
                dict(
                    type='LinearLR',
                    start_factor=1.0e-5,
                    by_epoch=False,
                    begin=0,
                    end=1000),
                dict(
                    type='CosineAnnealingLR',
                    eta_min=base_lr * 0.05,
                    begin=max_epochs // 2,  # max_epoch 也改变了
                    end=max_epochs,
                    T_max=max_epochs // 2,
                    by_epoch=True,
                    convert_to_iter_based=True),
            ]
            optim_wrapper = dict(optimizer=dict(lr=base_lr))

            # 第二 stage 切换 pipeline 的 epoch 时刻也改变了
            # _base_.custom_hooks[1].switch_epoch = max_epochs - num_epochs_stage2

            val_evaluator = dict(ann_file=data_root + 'val/annotation_coco.json')
            test_evaluator = val_evaluator

            # 一些打印设置修改
            default_hooks = dict(
                checkpoint=dict(interval=5, max_keep_ckpts=2, save_best='auto'),  # 同时保存最好性能权重
                logger=dict(type='LoggerHook', interval=5))
            train_cfg = dict(max_epochs=max_epochs, val_interval=5)
            """

            with open(mmdet_config_file_path, 'w', encoding='utf-8') as f:
                f.write(config_info)

        @staticmethod
        # 生成mmdetection训练算法配置文件
        def write_config_file_of_mm_train(mmdet_config_file_path, category_name,
                                          alg_mode, alg_type):
            if alg_mode == Alg_Model_Enum.MmdetV3.value.Insseg.mask_rcnn:
                base_config_py = "mm_config/mmdet-insseg/mmdet_v3-insseg-mask_rcnn_mask.py"
            elif alg_mode == Alg_Model_Enum.MmdetV3.value.Insseg.cascade_mask_rcnn:
                base_config_py = "mm_config/mmdet-insseg/mmdet_v3-insseg-cascade_mask_rcnn_mask.py"
            elif alg_mode == Alg_Model_Enum.MmdetV3.value.Objdet.cascade_rcnn:
                base_config_py = "mm_config/mmdet-objdet/mmdet_v3-objdet-cascade_rcnn_hbb.py"
            elif alg_mode == Alg_Model_Enum.MmdetV3.value.Objdet.faster_rcnn:
                base_config_py = "mm_config/mmdet-objdet/mmdet_v3-objdet-faster_rcnn_hbb.py"
            elif alg_mode == Alg_Model_Enum.MmdetV3.value.Objdet.rtmdet:
                base_config_py = "mm_config/mmdet-objdet/mmdet_v3-objdet-rtmdet_hbb.py"
            elif alg_mode == Alg_Model_Enum.MmsegV1.value.Semseg.segformer:
                base_config_py = "mm_config/mmseg-semseg/mmseg_v1-semseg-segformer_mask.py"
            with open(base_config_py, "r") as f1:
                config_info = f1.read()
                if alg_type == Alg_Type_Enum.mmdetv3_obj_det.value:
                    dir_name = "mmdet-objdet"
                elif alg_type == Alg_Type_Enum.mmdetv3_ins_seg.value:
                    dir_name = "mmdet-insseg"
                elif alg_type == Alg_Type_Enum.mmsegv1_sem_seg.value:
                    dir_name = "mmseg-semseg"
                config_info = config_info.replace("data_root = './data/{}/airplane/'".format(dir_name),
                                                  "data_root = './data/{}/{}/'".format(dir_name, category_name))
            with open(mmdet_config_file_path, 'w', encoding='utf-8') as f2:
                f2.write(config_info)

        @staticmethod
        def download_pth(pth_download_url, base_pth_file_path):
            import requests
            r = requests.get(pth_download_url)
            with open(base_pth_file_path, 'wb', encoding='utf-8') as file:
                file.write(r.content)

    class CityScapesHelper:
        def __init__(self):
            pass

        @staticmethod
        def build_name2label(category_name):

            name2label = {}
            # a label and all meta information
            Label = namedtuple('Label', [

                'name',  # The identifier of this label, e.g. 'car', 'person', ... .
                # We use them to uniquely name a class

                'id',  # An integer ID that is associated with this label.
                # The IDs are used to represent the label in ground truth images
                # An ID of -1 means that this label does not have an ID and thus
                # is ignored when creating ground truth images (e.g. license plate).
                # Do not modify these IDs, since exactly these IDs are expected by the
                # evaluation server.

                'trainId',  # Feel free to modify these IDs as suitable for your method. Then create
                # ground truth images with train IDs, using the tools provided in the
                # 'preparation' folder. However, make sure to validate or submit results
                # to our evaluation server using the regular IDs above!
                # For trainIds, multiple labels might have the same ID. Then, these labels
                # are mapped to the same class in the ground truth images. For the inverse
                # mapping, we use the label that is defined first in the list below.
                # For example, mapping all void-type classes to the same ID in training,
                # might make sense for some approaches.
                # Max value is 255!

                'category',  # The name of the category that this label belongs to

                'categoryId',  # The ID of this category. Used to create ground truth images
                # on category level.

                'hasInstances',  # Whether this label distinguishes between single instances or not

                'ignoreInEval',  # Whether pixels having this class as ground truth label are ignored
                # during evaluations or not

                'color',  # The color of this label
            ])
            # # a label and all meta information
            # Label = namedtuple( 'Label' , [
            #
            #     'name'        , # The identifier of this label, e.g. 'car', 'person', ... .
            #                     # We use them to uniquely name a class
            #
            #     'id'          , # An integer ID that is associated with this label.
            #                     # The IDs are used to represent the label in ground truth images
            #                     # An ID of -1 means that this label does not have an ID and thus
            #                     # is ignored when creating ground truth images (e.g. license plate).
            #                     # Do not modify these IDs, since exactly these IDs are expected by the
            #                     # evaluation server.
            #
            #     'trainId'     , # Feel free to modify these IDs as suitable for your method. Then create
            #                     # ground truth images with train IDs, using the tools provided in the
            #                     # 'preparation' folder. However, make sure to validate or submit results
            #                     # to our evaluation server using the regular IDs above!
            #                     # For trainIds, multiple labels might have the same ID. Then, these labels
            #                     # are mapped to the same class in the ground truth images. For the inverse
            #                     # mapping, we use the label that is defined first in the list below.
            #                     # For example, mapping all void-type classes to the same ID in training,
            #                     # might make sense for some approaches.
            #                     # Max value is 255!
            #
            #     'category'    , # The name of the category that this label belongs to
            #
            #     'categoryId'  , # The ID of this category. Used to create ground truth images
            #                     # on category level.
            #
            #     'hasInstances', # Whether this label distinguishes between single instances or not
            #
            #     'ignoreInEval', # Whether pixels having this class as ground truth label are ignored
            #                     # during evaluations or not
            #
            #     'color'       , # The color of this label
            #     ] )
            #
            #
            # #--------------------------------------------------------------------------------
            # # A list of all labels
            # #--------------------------------------------------------------------------------
            #
            # # Please adapt the train IDs as appropriate for your approach.
            # # Note that you might want to ignore labels with ID 255 during training.
            # # Further note that the current train IDs are only a suggestion. You can use whatever you like.
            # # Make sure to provide your results using the original IDs and not the training IDs.
            # # Note that many IDs are ignored in evaluation and thus you never need to predict these!
            #
            # labels = [
            #     #       name                     id    trainId   category            catId     hasInstances   ignoreInEval   color
            #     Label(  'unlabeled'            ,  0 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
            #     Label(  'ego vehicle'          ,  1 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
            #     Label(  'rectification border' ,  2 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
            #     Label(  'out of roi'           ,  3 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
            #     Label(  'static'               ,  4 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
            #     Label(  'dynamic'              ,  5 ,      255 , 'void'            , 0       , False        , True         , (111, 74,  0) ),
            #     Label(  'ground'               ,  6 ,      255 , 'void'            , 0       , False        , True         , ( 81,  0, 81) ),
            #     Label(  'road'                 ,  7 ,        0 , 'flat'            , 1       , False        , False        , (128, 64,128) ),
            #     Label(  'sidewalk'             ,  8 ,        1 , 'flat'            , 1       , False        , False        , (244, 35,232) ),
            #     Label(  'parking'              ,  9 ,      255 , 'flat'            , 1       , False        , True         , (250,170,160) ),
            #     Label(  'rail track'           , 10 ,      255 , 'flat'            , 1       , False        , True         , (230,150,140) ),
            #     Label(  'building'             , 11 ,        2 , 'construction'    , 2       , False        , False        , ( 70, 70, 70) ),
            #     Label(  'wall'                 , 12 ,        3 , 'construction'    , 2       , False        , False        , (102,102,156) ),
            #     Label(  'fence'                , 13 ,        4 , 'construction'    , 2       , False        , False        , (190,153,153) ),
            #     Label(  'guard rail'           , 14 ,      255 , 'construction'    , 2       , False        , True         , (180,165,180) ),
            #     Label(  'bridge'               , 15 ,      255 , 'construction'    , 2       , False        , True         , (150,100,100) ),
            #     Label(  'tunnel'               , 16 ,      255 , 'construction'    , 2       , False        , True         , (150,120, 90) ),
            #     Label(  'pole'                 , 17 ,        5 , 'object'          , 3       , False        , False        , (153,153,153) ),
            #     Label(  'polegroup'            , 18 ,      255 , 'object'          , 3       , False        , True         , (153,153,153) ),
            #     Label(  'traffic light'        , 19 ,        6 , 'object'          , 3       , False        , False        , (250,170, 30) ),
            #     Label(  'traffic sign'         , 20 ,        7 , 'object'          , 3       , False        , False        , (220,220,  0) ),
            #     Label(  'vegetation'           , 21 ,        8 , 'nature'          , 4       , False        , False        , (107,142, 35) ),
            #     Label(  'terrain'              , 22 ,        9 , 'nature'          , 4       , False        , False        , (152,251,152) ),
            #     Label(  'sky'                  , 23 ,       10 , 'sky'             , 5       , False        , False        , ( 70,130,180) ),
            #     Label(  'person'               , 24 ,       11 , 'human'           , 6       , True         , False        , (220, 20, 60) ),
            #     Label(  'rider'                , 25 ,       12 , 'human'           , 6       , True         , False        , (255,  0,  0) ),
            #     Label(  'car'                  , 26 ,       13 , 'vehicle'         , 7       , True         , False        , (  0,  0,142) ),
            #     Label(  'truck'                , 27 ,       14 , 'vehicle'         , 7       , True         , False        , (  0,  0, 70) ),
            #     Label(  'bus'                  , 28 ,       15 , 'vehicle'         , 7       , True         , False        , (  0, 60,100) ),
            #     Label(  'caravan'              , 29 ,      255 , 'vehicle'         , 7       , True         , True         , (  0,  0, 90) ),
            #     Label(  'trailer'              , 30 ,      255 , 'vehicle'         , 7       , True         , True         , (  0,  0,110) ),
            #     Label(  'train'                , 31 ,       16 , 'vehicle'         , 7       , True         , False        , (  0, 80,100) ),
            #     Label(  'motorcycle'           , 32 ,       17 , 'vehicle'         , 7       , True         , False        , (  0,  0,230) ),
            #     Label(  'bicycle'              , 33 ,       18 , 'vehicle'         , 7       , True         , False        , (119, 11, 32) ),
            #     Label(  'license plate'        , -1 ,       -1 , 'vehicle'         , 7       , False        , True         , (  0,  0,142) ),
            # ]

            if category_name == "building":
                metainfo = {
                    'classes': ('backgroud', 'building'),
                    'palette': [(128, 128, 128), (129, 127, 38)],
                    'id': [0, 1],
                    'trainId': [255, 1],
                    'category': ['void', 'building'],
                    'catId': [0, 1],
                    'hasInstances': [False, False],
                    'ignoreInEval': [True, True]
                }

            elif category_name == "boat":
                metainfo = {
                    'classes': ('unlabeled', 'submarine', 'cargoship', 'warship', 'liner', 'ship'),
                    'palette': [(128, 128, 128), (129, 127, 38), (120, 69, 125), (53, 125, 34),
                                (0, 11, 123), (118, 20, 12)],
                    'id': [0, 1, 2, 3, 4, 5],
                    'trainId': [255, 1, 1, 1, 1,1],
                    'category': ['void', 'boat', 'boat', 'boat', 'boat','boat'],
                    'catId': [0, 1, 1, 1, 1,1],
                    'hasInstances': [False, False, False, False, False, False],
                    'ignoreInEval': [False, False, False, False, False, False]
                }

                # labels = [
                #     #   name     id   trainId  category  catId  hasInstances  ignoreInEval   color
                #     Label('unlabeled', 0, 255, 'void', 0, False, True, (0, 0, 0)),
                #     Label('submarine', 1, 1, 'ship', 1, False, True, (0, 0, 255)),
                #     Label('cargoship', 2, 1, 'ship', 1, False, True, (190, 153, 153)),
                #     Label('warship', 3, 1, 'ship', 1, False, True, (119, 11, 32)),
                #     Label('liner', 4, 1, 'ship', 1, False, True, (220, 20, 60)),
                #     Label('ship', 5, 1, 'ship', 1, False, True, (150, 120, 90))
                # ]
            labels = []
            for index in range(len(metainfo["classes"])):
                classname = metainfo["classes"][index]
                palette = metainfo["palette"][index]
                id = metainfo["id"][index]
                trainId = metainfo["trainId"][index]
                category = metainfo["category"][index]
                catId = metainfo["catId"][index]
                hasInstances = metainfo["hasInstances"][index]
                ignoreInEval = metainfo["ignoreInEval"][index]
                labels.append(Label(classname, id, trainId, category, catId, hasInstances, ignoreInEval, palette))
            name2label = {label.name: label for label in labels}
            return name2label

        @staticmethod
        # Convert the given annotation to a label image
        def createLabelImage(annotation, encoding, name2label, outline=None):
            # the size of the image
            size = (annotation.imgWidth, annotation.imgHeight)
            # the background
            if encoding == "ids":
                background = name2label['unlabeled'].id
            elif encoding == "trainIds":
                background = name2label['unlabeled'].trainId
            elif encoding == "color":
                background = name2label['unlabeled'].color
            else:
                print("Unknown encoding '{}'".format(encoding))
                return None

            # this is the image that we want to create
            if encoding == "color":
                labelImg = Image.new("RGB", size, background)
            else:
                labelImg = Image.new("L", size, background)

            # a drawer to draw into the image
            drawer = ImageDraw.Draw(labelImg)

            # loop over all objects
            for obj in annotation.objects:
                label = obj.label
                polygon = obj.polygon

                # If the object is deleted, skip it
                if obj.deleted:
                    continue

                # If the label is not known, but ends with a 'group' (e.g. cargroup)
                # try to remove the s and see if that works
                if (not label in name2label) and label.endswith('group'):
                    label = label[:-len('group')]

                if not label in name2label:
                    print("Label '{}' not known.".format(label))

                # If the ID is negative that polygon should not be drawn
                if name2label[label].id < 0:
                    continue

                if encoding == "ids":
                    val = name2label[label].id
                elif encoding == "trainIds":
                    val = name2label[label].trainId
                elif encoding == "color":
                    val = name2label[label].color

                try:
                    if outline:
                        drawer.polygon(polygon, fill=val, outline=outline)
                    else:
                        drawer.polygon(polygon, fill=val)
                except:
                    print("Failed to draw polygon with label {}".format(label))
                    raise

            return labelImg

        # A method that does all the work
        # inJson is the filename of the json file
        # outImg is the filename of the label image that is generated
        # encoding can be set to
        #     - "ids"      : classes are encoded using the regular label IDs
        #     - "trainIds" : classes are encoded using the training IDs
        #     - "color"    : classes are encoded using the corresponding colors

        @staticmethod
        def json2labelImg(inJson, outImg, encoding="ids"):
            annotation = Annotation()
            annotation.fromJsonFile(inJson)
            labelImg = FileFormatConverter.CityScapesHelper.createLabelImage(annotation, encoding)
            labelImg.save(outImg)

    class YoloHelper:
        def __init__(self):
            pass

        # yolo转pascalVOC
        @staticmethod
        def yolo2pascalVoc(txt_file_path, xml_file_path, pic_file_path, class_file_path):
            classes_dict = {}
            # class_file_path= "classes.names"
            with open(class_file_path, encoding='utf-8') as f:
                for idx, line in enumerate(f.readlines()):
                    class_name = line.strip()
                    classes_dict[idx] = class_name
            file_name = FileHelper.get_file_name(txt_file_path)
            xmlBuilder = Document()
            annotation = xmlBuilder.createElement("annotation")  # 创建annotation标签
            xmlBuilder.appendChild(annotation)
            txtFile = open(txt_file_path, encoding='utf-8')
            txtList = txtFile.readlines()
            img = cv2.imread(pic_file_path)
            Pheight, Pwidth, Pdepth = img.shape

            folder = xmlBuilder.createElement("folder")  # folder标签
            foldercontent = xmlBuilder.createTextNode("driving_annotation_dataset")
            folder.appendChild(foldercontent)
            annotation.appendChild(folder)  # folder标签结束

            filename = xmlBuilder.createElement("filename")  # filename标签
            filenamecontent = xmlBuilder.createTextNode(file_name)
            filename.appendChild(filenamecontent)
            annotation.appendChild(filename)  # filename标签结束

            filename = xmlBuilder.createElement("path")  # path标签
            filenamecontent = xmlBuilder.createTextNode(pic_file_path)
            filename.appendChild(filenamecontent)
            annotation.appendChild(filename)  # path标签结束

            size = xmlBuilder.createElement("size")  # size标签
            width = xmlBuilder.createElement("width")  # size子标签width
            widthcontent = xmlBuilder.createTextNode(str(Pwidth))
            width.appendChild(widthcontent)
            size.appendChild(width)  # size子标签width结束

            height = xmlBuilder.createElement("height")  # size子标签height
            heightcontent = xmlBuilder.createTextNode(str(Pheight))
            height.appendChild(heightcontent)
            size.appendChild(height)  # size子标签height结束

            depth = xmlBuilder.createElement("depth")  # size子标签depth
            depthcontent = xmlBuilder.createTextNode(str(Pdepth))
            depth.appendChild(depthcontent)
            size.appendChild(depth)  # size子标签depth结束

            annotation.appendChild(size)  # size标签结束

            for j in txtList:
                oneline = j.strip().split(" ")
                object = xmlBuilder.createElement("object")  # object 标签
                picname = xmlBuilder.createElement("name")  # name标签
                namecontent = xmlBuilder.createTextNode(classes_dict[oneline[0]])
                picname.appendChild(namecontent)
                object.appendChild(picname)  # name标签结束

                pose = xmlBuilder.createElement("pose")  # pose标签
                posecontent = xmlBuilder.createTextNode("Unspecified")
                pose.appendChild(posecontent)
                object.appendChild(pose)  # pose标签结束

                truncated = xmlBuilder.createElement("truncated")  # truncated标签
                truncatedContent = xmlBuilder.createTextNode("0")
                truncated.appendChild(truncatedContent)
                object.appendChild(truncated)  # truncated标签结束

                difficult = xmlBuilder.createElement("difficult")  # difficult标签
                difficultcontent = xmlBuilder.createTextNode("0")
                difficult.appendChild(difficultcontent)
                object.appendChild(difficult)  # difficult标签结束

                bndbox = xmlBuilder.createElement("bndbox")  # bndbox标签
                xmin = xmlBuilder.createElement("xmin")  # xmin标签
                mathData = int(((float(oneline[1])) * Pwidth + 1) - (float(oneline[3])) * 0.5 * Pwidth)
                xminContent = xmlBuilder.createTextNode(str(mathData))
                xmin.appendChild(xminContent)
                bndbox.appendChild(xmin)  # xmin标签结束

                ymin = xmlBuilder.createElement("ymin")  # ymin标签
                mathData = int(((float(oneline[2])) * Pheight + 1) - (float(oneline[4])) * 0.5 * Pheight)
                yminContent = xmlBuilder.createTextNode(str(mathData))
                ymin.appendChild(yminContent)
                bndbox.appendChild(ymin)  # ymin标签结束

                xmax = xmlBuilder.createElement("xmax")  # xmax标签
                mathData = int(((float(oneline[1])) * Pwidth + 1) + (float(oneline[3])) * 0.5 * Pwidth)
                xmaxContent = xmlBuilder.createTextNode(str(mathData))
                xmax.appendChild(xmaxContent)
                bndbox.appendChild(xmax)  # xmax标签结束

                ymax = xmlBuilder.createElement("ymax")  # ymax标签
                mathData = int(((float(oneline[2])) * Pheight + 1) + (float(oneline[4])) * 0.5 * Pheight)
                ymaxContent = xmlBuilder.createTextNode(str(mathData))
                ymax.appendChild(ymaxContent)
                bndbox.appendChild(ymax)  # ymax标签结束

                object.appendChild(bndbox)  # bndbox标签结束

                annotation.appendChild(object)  # object标签结束

            f = open(xml_file_path, 'w', encoding='utf-8')
            xmlBuilder.writexml(f, indent='\t', newl='\n', addindent='\t', encoding='utf-8')
            f.close()

        # 初始化yolov8需要的数据目录
        @staticmethod
        def init_yolov8_data_dir(dest_path, category_name):
            yolo_image_dir = os.path.join(dest_path, "datasets", category_name, "images")
            yolo_train_image_dir = os.path.join(yolo_image_dir, "train2017")
            yolo_val_image_dir = os.path.join(yolo_image_dir, "val2017")
            yolo_test_image_dir = os.path.join(yolo_image_dir, "test2017")
            yolo_label_dir = os.path.join(dest_path, "datasets", category_name, "labels")
            yolo_train_label_dir = os.path.join(yolo_label_dir, "train2017")
            yolo_val_label_dir = os.path.join(yolo_label_dir, "val2017")
            yolo_test_label_dir = os.path.join(yolo_label_dir, "test2017")
            FileHelper.mkdirs(
                [yolo_image_dir, yolo_train_image_dir, yolo_val_image_dir, yolo_test_image_dir, yolo_label_dir,
                 yolo_train_label_dir, yolo_val_label_dir, yolo_test_label_dir])

        # 生成yolov8训练需要的classes.names
        @staticmethod
        def write_class_file_of_yolov8_train(class_file_path, label_list):
            print("生成yolo的class文件")
            yolo_class_file_path = os.path.join(class_file_path)
            # 打开文件，如果文件不存在则新建一个
            file = open(yolo_class_file_path, "w", encoding='utf-8')
            for label in label_list:
                # 写入数据
                file.write(label + "\n")
            # 关闭文件
            file.close()

        # 生成yolov8训练需要的my_data.yaml
        @staticmethod
        def write_yaml_file_of_yolov8_train(yaml_file_path, label_list, train_path):
            print("生成yolo的my_data.yaml")
            # 在class里，如果不同编号代码的子类型都一样，那就按照同一类训练
            # Classes
            # names:
            #     0: boat
            #     1: boat
            # 如果不同编号代码的子类型不一样，那就按不同类训练
            # Classes
            # names:
            #     0: submarine
            #     1: warship
            # 打开文件，如果文件不存在则新建一个
            file = open(yaml_file_path, "w", encoding='utf-8')
            file.write("path: {}\n".format(train_path))
            file.write("train: images/train2017\n")
            file.write("val: images/val2017\n")
            file.write("test: images/test2017\n")
            file.write("names:\n")
            for index in range(len(label_list)):
                label = label_list[index]
                # 写入数据
                file.write("  {}: {}\n".format(index, label))
            # 关闭文件
            file.close()

    class DOTAConverter:
        def __init__(self):
            pass

        # 得到DOTA标签文件里的类型
        @staticmethod
        def get_class_name_array_in_dota_txt(txt_file_path):
            class_name_array = []
            txtFile = open(txt_file_path, encoding='utf-8')
            txtList = txtFile.readlines()
            # 前两行不读
            for j in txtList[2:]:
                oneline = j.strip().split(" ")
                class_name = oneline[8]
                if class_name not in class_name_array:
                    class_name_array.append(class_name)
            return class_name_array

        # DOTA转labelme,指定class，或者是全部类型(ALLClass)
        @staticmethod
        def DOTA2Labelme(txt_file_path, pic_file_path, json_file_path, class_name):
            txtFile = open(txt_file_path, encoding='utf-8')
            txtList = txtFile.readlines()
            shapes_array = []
            # 前两行不读
            for j in txtList[2:]:
                oneline = j.strip().split(" ")
                label = oneline[8]
                shape_dict = {}
                shape_dict["label"] = label
                if class_name == "ALLClass" or class_name == label:
                    points_array = [[float(oneline[0]), float(oneline[1])], [float(oneline[2]), float(oneline[3])],
                                    [float(oneline[4]), float(oneline[5])], [float(oneline[6]), float(oneline[7])]]
                    shape_dict["points"] = points_array
                    shape_dict["group_id"] = None
                    shape_dict["shape_type"] = "polygon"
                    shape_dict["flags"] = {}
                    shapes_array.append(shape_dict)
            if len(shapes_array) > 0:
                json_file_dict = FileFormatConverter.LablemeHelper.__build_lableme_json_dict(shapes_array,
                                                                                             pic_file_path)
                FileHelper.write_json_obj_into_file(json_file_dict, json_file_path)
            else:
                print("当前图片的标签数据为空")

    class LEVIRConverter:
        def __init__(self):
            pass

        # 得到LEVIR标签文件里的类型
        @staticmethod
        def get_class_name_array_in_levir_txt(txt_file_path):
            class_name_array = []
            txtFile = open(txt_file_path, encoding='utf-8')
            txtList = txtFile.readlines()
            for j in txtList:
                oneline = j.strip().split(" ")
                class_name = oneline[0]
                if class_name not in class_name_array:
                    class_name_array.append(class_name)
            return class_name_array

        # LEVIR转labelme,指定class，或者是全部类型(ALLClass)
        @staticmethod
        def LEVIR2Labelme(txt_file_path, pic_file_path, json_file_path, class_name):
            txtFile = open(txt_file_path, encoding='utf-8')
            txtList = txtFile.readlines()
            shapes_array = []
            for j in txtList:
                oneline = j.strip().split(" ")
                label = oneline[0]
                shape_dict = {}
                shape_dict["label"] = label
                # class left top right bottom
                if class_name == "ALLClass" or class_name == label:
                    if float(oneline[1]) > 0 and float(oneline[2]) > 0 and float(oneline[3]) > 0 and float(
                            oneline[4]) > 0:
                        points_array = [[float(oneline[1]), float(oneline[2])], [float(oneline[3]), float(oneline[2])],
                                        [float(oneline[3]), float(oneline[4])], [float(oneline[1]), float(oneline[4])]]
                        shape_dict["points"] = points_array
                        shape_dict["group_id"] = None
                        shape_dict["shape_type"] = "polygon"
                        shape_dict["flags"] = {}
                        shapes_array.append(shape_dict)
            if len(shapes_array) > 0:
                json_file_dict = FileFormatConverter.LablemeHelper.__build_lableme_json_dict(shapes_array,
                                                                                             pic_file_path)
                FileHelper.write_json_obj_into_file(json_file_dict, json_file_path)
            else:
                print("当前图片的标签数据为空")

    class UCASConverter:
        def __init__(self):
            pass

        # UCAS转labelme
        @staticmethod
        def UCAS2Labelme(txt_file_path, pic_file_path, json_file_path, label_name):
            txtFile = open(txt_file_path, encoding='utf-8')
            txtList = txtFile.readlines()
            shapes_array = []
            for j in txtList:
                oneline = j.strip().split("\t")
                shape_dict = {}
                shape_dict["label"] = label_name
                # 校正前的范围,不是矩形
                points_array = [[float(oneline[0]), float(oneline[1])], [float(oneline[2]), float(oneline[3])],
                                [float(oneline[4]), float(oneline[5])], [float(oneline[6]), float(oneline[7])]]
                # 校正后的范围
                # minx = float(oneline[9])
                # miny = float(oneline[10])
                # maxx = minx+float(oneline[11])
                # maxy = miny+float(oneline[12])
                # points_array = [[minx, miny], [maxx, miny],
                #                 [maxx, maxy], [minx, maxy]]
                shape_dict["points"] = points_array
                shape_dict["group_id"] = None
                shape_dict["shape_type"] = "polygon"
                shape_dict["flags"] = {}
                shapes_array.append(shape_dict)
            json_file_dict = FileFormatConverter.LablemeHelper.__build_lableme_json_dict(shapes_array, pic_file_path)
            FileHelper.write_json_obj_into_file(json_file_dict, json_file_path)

    class NWPUConverter:
        def __init__(self):
            pass

        # NWPU转labelme
        @staticmethod
        def NWPU2Labelme(txt_file_path, class_file_path, pic_file_path, json_file_path):
            classes_dict = {}
            # class_file_path= "classes.names"
            with open(class_file_path, encoding='utf-8') as f:
                for idx, line in enumerate(f.readlines()):
                    class_name = line.strip()
                    classes_dict[idx] = class_name
            txtFile = open(txt_file_path, encoding='utf-8')
            txtList = txtFile.readlines()
            shapes_array = []
            for j in txtList:
                oneline = j.strip().split(",")
                class_id = oneline[2]
                shape_dict = {}
                shape_dict["label"] = classes_dict[class_id]
                minx_str = StringHelper.get_number_in_str(oneline[0].split(",").replace(" ", ""))
                miny_str = StringHelper.get_number_in_str(oneline[1].split(",").replace(" ", ""))
                maxx_str = StringHelper.get_number_in_str(oneline[2].split(",").replace(" ", ""))
                maxy_str = StringHelper.get_number_in_str(oneline[3].split(",").replace(" ", ""))
                minx = float(minx_str)
                miny = float(miny_str)
                maxx = float(maxx_str)
                maxy = float(maxy_str)
                points_array = [[minx, miny], [maxx, miny],
                                [maxx, maxy], [minx, maxy]]
                shape_dict["points"] = points_array
                shape_dict["group_id"] = None
                shape_dict["shape_type"] = "polygon"
                shape_dict["flags"] = {}
                shapes_array.append(shape_dict)
            json_file_dict = FileFormatConverter.LablemeHelper.__build_lableme_json_dict(shapes_array, pic_file_path)
            FileHelper.write_json_obj_into_file(json_file_dict, json_file_path)

    class HRSCConverter:
        def __init__(self):
            pass

        # label名称需要抽出来，根据class_id
        # 1000000**
        # 01 船
        # 02,05,06,12,13,32, 航母
        # 03,07,08,09,10,11,15,16,17,19,28,  军舰
        # 04,18,20,22,24,25,26,29,30 民商船
        # 27潜艇\
        @staticmethod
        def get_label_name_by_HRSC_class_id(hrsc_class_id):
            warcraft_class_ids = [100000003, 100000007, 100000008, 100000009, 100000010, 100000011, 100000015,
                                  100000016,
                                  100000017, 100000019, 100000028]
            aircraft_carrier_ids = [100000001, 100000002, 100000005, 100000006, 100000012, 100000013, 100000032]
            merchant_ship_ids = [100000004, 100000018, 100000020, 100000022, 100000024, 100000025, 100000026,
                                 100000029,
                                 100000030]
            submarine_ids = [100000027]
            label_name = None
            if hrsc_class_id is not None:
                hrsc_class_id = int(hrsc_class_id)
                if hrsc_class_id in warcraft_class_ids:
                    label_name = "warcraft"
                elif hrsc_class_id in aircraft_carrier_ids:
                    label_name = "aircraft_carrier"
                elif hrsc_class_id in merchant_ship_ids:
                    label_name = "merchant_ship"
                elif hrsc_class_id in submarine_ids:
                    label_name = "submarine"
            return label_name

        # HRSC转为labelme
        # 图片后缀会统一变成png
        @staticmethod
        def HRSC2Labelme(xml_file_path, pic_file_path, json_file_path):
            tree = ET.parse(xml_file_path)
            shapes_array = []
            HRSC_Objects = tree.find('HRSC_Objects')
            if len(HRSC_Objects.findall('HRSC_Object')) > 0:
                for obj in HRSC_Objects.findall('HRSC_Object'):
                    shape_dict = {}
                    class_id = obj.find('Class_ID').text
                    shape_dict["label"] = FileFormatConverter.HRSCConverter.get_label_name_by_HRSC_class_id(class_id)
                    if shape_dict["label"] is None:
                        print("class id:{}没有匹配上".format(class_id))
                    minx_str = obj.find('box_xmin').text
                    miny_str = obj.find('box_ymin').text
                    maxx_str = obj.find('box_xmax').text
                    maxy_str = obj.find('box_ymax').text
                    minx = float(minx_str)
                    miny = float(miny_str)
                    maxx = float(maxx_str)
                    maxy = float(maxy_str)
                    points_array = [[minx, miny], [maxx, miny],
                                    [maxx, maxy], [minx, maxy]]
                    shape_dict["points"] = points_array
                    shape_dict["group_id"] = None
                    shape_dict["shape_type"] = "polygon"
                    shape_dict["flags"] = {}
                    shapes_array.append(shape_dict)
                json_file_dict = FileFormatConverter.LablemeHelper.__build_lableme_json_dict(shapes_array,
                                                                                             pic_file_path)
                json_file_dict["imagePath"] = os.path.splitext(FileHelper.get_file_name(pic_file_path))[0] + ".png"
                FileHelper.write_json_obj_into_file(json_file_dict, json_file_path)
            else:
                print("当前图片的标签数据为空")

    class VEDAIConverter:
        def __init__(self):
            pass

        # 得到VEDAI标签文件里的类型
        @staticmethod
        def get_class_name_array_in_VEDAI_txt(txt_file_path):
            class_name_array = []
            txtFile = open(txt_file_path, encoding='utf-8')
            txtList = txtFile.readlines()
            for j in txtList:
                oneline = j.strip().split(" ")
                class_name = oneline[3]
                if class_name not in class_name_array:
                    class_name_array.append(class_name)
            return class_name_array

        # VEDAI转换为pascalVoc
        @staticmethod
        def vedai2PascalVoc(txt_file_path, xml_file_path, pic_file_path, class_name):
            # img_data = cv2.imread(pic_file_path)
            img_data = cv2.imdecode(np.fromfile(pic_file_path, dtype=np.uint8), -1)
            txt_data = open(txt_file_path, 'r', encoding='utf-8').readlines()
            boxes_all = FileFormatConverter.VEDAIConverter.__format_vedai_label(txt_data, class_name)
            if len(boxes_all) > 0:
                FileFormatConverter.VEDAIConverter.__vedai_save_to_pascal_xml(xml_file_path, img_data.shape[0],
                                                                              img_data.shape[1], boxes_all)
            else:
                print("当前图片标签数据为空")

        # 内部函数，转换为pascalvoc
        @staticmethod
        def __vedai_save_to_pascal_xml(save_path, im_height, im_width, objects_axis):
            im_depth = 0
            object_num = len(objects_axis)
            doc = Document()

            annotation = doc.createElement('annotation')
            doc.appendChild(annotation)

            folder = doc.createElement('folder')
            folder_name = doc.createTextNode('VOC2007')
            folder.appendChild(folder_name)
            annotation.appendChild(folder)

            filename = doc.createElement('filename')
            filename_name = doc.createTextNode(save_path.split('\\')[-1])
            filename.appendChild(filename_name)
            annotation.appendChild(filename)

            source = doc.createElement('source')
            annotation.appendChild(source)

            database = doc.createElement('database')
            database.appendChild(doc.createTextNode('The VOC2007 Database'))
            source.appendChild(database)

            annotation_s = doc.createElement('annotation')
            annotation_s.appendChild(doc.createTextNode('PASCAL VOC2007'))
            source.appendChild(annotation_s)

            image = doc.createElement('image')
            image.appendChild(doc.createTextNode('flickr'))
            source.appendChild(image)

            flickrid = doc.createElement('flickrid')
            flickrid.appendChild(doc.createTextNode('322409915'))
            source.appendChild(flickrid)

            owner = doc.createElement('owner')
            annotation.appendChild(owner)

            flickrid_o = doc.createElement('flickrid')
            flickrid_o.appendChild(doc.createTextNode('knautia'))
            owner.appendChild(flickrid_o)

            name_o = doc.createElement('name')
            name_o.appendChild(doc.createTextNode('dear_jing'))
            owner.appendChild(name_o)

            size = doc.createElement('size')
            annotation.appendChild(size)
            width = doc.createElement('width')
            width.appendChild(doc.createTextNode(str(im_width)))
            height = doc.createElement('height')
            height.appendChild(doc.createTextNode(str(im_height)))
            depth = doc.createElement('depth')
            depth.appendChild(doc.createTextNode(str(im_depth)))
            size.appendChild(width)
            size.appendChild(height)
            size.appendChild(depth)
            segmented = doc.createElement('segmented')
            segmented.appendChild(doc.createTextNode('0'))
            annotation.appendChild(segmented)
            for i in range(object_num):
                objects = doc.createElement('object')
                annotation.appendChild(objects)
                object_name = doc.createElement('name')
                object_name.appendChild(doc.createTextNode(str(int(objects_axis[i][-1]))))
                objects.appendChild(object_name)
                pose = doc.createElement('pose')
                pose.appendChild(doc.createTextNode('Unspecified'))
                objects.appendChild(pose)
                truncated = doc.createElement('truncated')
                truncated.appendChild(doc.createTextNode(str(int(objects_axis[i][9]))))
                objects.appendChild(truncated)
                difficult = doc.createElement('difficult')
                difficult.appendChild(doc.createTextNode(str(int(objects_axis[i][8]))))
                objects.appendChild(difficult)
                polygon = doc.createElement('polygon')
                objects.appendChild(polygon)

                x0 = doc.createElement('x0')
                x0.appendChild(doc.createTextNode(str(int(objects_axis[i][0]))))
                polygon.appendChild(x0)
                y0 = doc.createElement('y0')
                y0.appendChild(doc.createTextNode(str(int(objects_axis[i][4]))))
                polygon.appendChild(y0)

                x1 = doc.createElement('x1')
                x1.appendChild(doc.createTextNode(str(int(objects_axis[i][1]))))
                polygon.appendChild(x1)
                y1 = doc.createElement('y1')
                y1.appendChild(doc.createTextNode(str(int(objects_axis[i][5]))))
                polygon.appendChild(y1)

                x2 = doc.createElement('x2')
                x2.appendChild(doc.createTextNode(str(int(objects_axis[i][2]))))
                polygon.appendChild(x2)
                y2 = doc.createElement('y2')
                y2.appendChild(doc.createTextNode(str(int(objects_axis[i][6]))))
                polygon.appendChild(y2)

                x3 = doc.createElement('x3')
                x3.appendChild(doc.createTextNode(str(int(objects_axis[i][3]))))
                polygon.appendChild(x3)
                y3 = doc.createElement('y3')
                y3.appendChild(doc.createTextNode(str(int(objects_axis[i][7]))))
                polygon.appendChild(y3)

            f = open(save_path, 'w', encoding='utf-8')
            f.write(doc.toprettyxml(indent=''))
            f.close()

        # 内部函数，格式化vedai
        @staticmethod
        def __format_vedai_label(txt_list, class_name):
            # class_list = ['plane', 'boat', 'camping_car', 'car', 'pick-up', 'tractor', 'truck', 'van', 'vehicle']
            class_list = {'plane': 31, 'boat': 23, 'camping_car': 5, 'car': 1, 'pick-up': 11, 'tractor': 4, 'truck': 2,
                          'van': 9,
                          'vehicle': 10, 'others': 0}
            format_data = []

            for i in txt_list:
                if len(i.split(' ')) < 14:
                    continue
                flag = False
                for k, v in class_list.items():
                    if v == int(i.split(' ')[3].split('\n')[0]):
                        if class_name == "AllClass" or i.split(' ')[3].split('\n')[0] == class_name:
                            format_data.append(
                                [float(xy) for xy in i.split(' ')[6:14]] + [int(x) for x in i.split(' ')[4:6]] + [v]
                            )
                            flag = True
                # if not flag:
                #     format_data.append(
                #         [float(xy) for xy in i.split(' ')[6:14]] + [int(x) for x in i.split(' ')[4:6]] + ['others']
                #     )

            return np.array(format_data)

    class RectHelper:
        def __init__(self):
            pass

        @staticmethod
        # 对多边形获取旋转矩形框OBB坐标
        # 多边形的坐标  polygon_coords = [(0, 0), (0, 1), (1, 1), (1, 0), (1, 2), (2, 2)]
        def oriented_bounding_box(polygon_coords):
            # 创建Polygon对象
            polygon = Polygon(polygon_coords)
            # 获取多边形的外接矩形
            obb = polygon.minimum_rotated_rectangle
            # 获取外接矩形的四个顶点
            obb_corners = list(obb.exterior.coords)
            # 如果超过4个点，需要去掉末尾多余的点
            if len(obb_corners) > 4:
                obb_corners = obb_corners[:4]
            return obb_corners

        @staticmethod
        # 内部函数，获取斜外包矩形（旋转矩形）坐标范围
        def get_rotate_rect_of_points_array(points_array):
            # 定义多边形的坐标
            # points_array = [[104.0, 263.0], [104.0, 279.0]]
            # coordinates = [(0, 0), (0, 1), (1, 1), (1, 0)]
            coordinates = []
            for point in points_array:
                tmpx = point[0]
                tmpy = point[1]
                coordinates.append((tmpx, tmpy))
            # 获取多边形的斜矩形的坐标
            rectangle_coordinates = FileFormatConverter.RectHelper.oriented_bounding_box(coordinates)
            new_points_array = []
            for index in range(len(rectangle_coordinates)):
                point = rectangle_coordinates[index]
                tmpx = point[0]
                tmpy = point[1]
                new_points_array.append([tmpx, tmpy])
            return new_points_array

        @staticmethod
        # 内部函数，获外包矩形(水平矩形框HBB)坐标范围
        # points_array = [[104.0, 263.0], [104.0, 279.0]]
        def get_horizon_rect_of_points_array(points_array):
            # 获取多边形的外包矩形的坐标
            minx, miny, maxx, maxy = FileFormatConverter.RectHelper.get_envelop_of_points_new(points_array)
            new_points_array = [[minx, miny], [minx, maxy], [maxx, maxy], [maxx, miny]]
            return new_points_array

        @staticmethod
        # 内部函数，获取水平矩形坐标范围,效率低
        def get_envelop_of_points(points_array):
            # points_array = [[104.0, 263.0], [104.0, 279.0]]
            minx = points_array[0][0]
            miny = points_array[0][1]
            maxx = points_array[0][0]
            maxy = points_array[0][1]
            for point in points_array:
                tmpx = point[0]
                tmpy = point[1]
                if tmpx < minx:
                    minx = tmpx
                if tmpy < miny:
                    miny = tmpy
                if tmpx > maxx:
                    maxx = tmpx
                if tmpy > maxy:
                    maxy = tmpy
            return minx, miny, maxx, maxy

        @staticmethod
        # 内部函数，获取水平矩形坐标范围
        def get_envelop_of_points_new(points_array):
            # points_array = [[104.0, 263.0], [104.0, 279.0]]
            # 定义多边形的坐标
            # coordinates = [(0, 0), (0, 1), (1, 1), (1, 0)]
            coordinates = []

            for point in points_array:
                tmpx = point[0]
                tmpy = point[1]
                coordinates.append((tmpx, tmpy))
            # 创建多边形对象
            polygon = Polygon(coordinates)
            # 获取多边形的斜矩形的坐标
            rectangle_coordinates = polygon.envelope.exterior.coords
            x_list = rectangle_coordinates.xy[0]
            y_list = rectangle_coordinates.xy[1]
            minx = min(x_list)
            miny = min(y_list)
            maxx = max(x_list)
            maxy = max(y_list)
            return minx, miny, maxx, maxy

    # 将mask二值图转换为shp文件
    @staticmethod
    def convert_mask_pic_to_shape_file(mask_pic_file_path, gdal_transform, shp_path):
        AIHelper.convert_mask_to_shape(mask_pic_file_path, gdal_transform, None, shp_path, None)


class ImageAugmenter:
    def __init__(self):
        pass

    augment_dir_suffix = "_Augment"
    augment_file_suffix = "_aug"

    @staticmethod
    # 利用imgaug类进行数据增广（上下翻转、左右翻转、旋转、模糊、增亮等）,包括原始图片和lableme标签数据
    # 如果一个图里有多个label类别，进行保留
    def sample_and_label_augment_by_file(image_path, json_path, image_augment_path, json_augment_path,
                                         image_file_suffix, json_data_type):

        # 读取图像和LabelMe格式的JSON标注数据
        with open(json_path, 'r', encoding='utf-8') as f:
            labelme_data = json.load(f)

        # 读取图像
        image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)

        # 提取LabelMe格式的标注信息
        shapes = labelme_data['shapes']

        # 提取标注框(bbs为水平矩形，polys为多边形或旋转矩形)
        from imgaug.augmentables.polys import Polygon
        bbs = []
        labels = []
        for shape in shapes:
            label = shape['label']
            points = shape['points']
            x, y, w, h = cv2.boundingRect(np.array(points).astype(int))
            bbs.append(BoundingBox(x1=x, y1=y, x2=x + w, y2=y + h))
            labels.append(label)

        # 创建BoundingBoxesOnImage对象
        if json_data_type == Label_Data_Type_Enum.hbb.value:
            bbs_on_image = BoundingBoxesOnImage(bbs, shape=image.shape)
        # 创建PolygonsOnImage对象
        elif json_data_type == Label_Data_Type_Enum.obb.value or json_data_type == Label_Data_Type_Enum.mask.value:
            points = [i.get('points') for i in shapes]
            points = [np.array(i, dtype=np.int32).reshape((-1, 2)) for i in points]
            polys_on_image = ia.PolygonsOnImage([Polygon(point) for point in points], shape=image.shape)

        # 定义图像增广器
        augmenter = iaa.Sequential([
            iaa.Fliplr(0.5),  # 左右翻转
            iaa.Flipud(0.5),  # 上下翻转
            iaa.Affine(rotate=(-45, 45)),  # 旋转
            iaa.GaussianBlur(sigma=(0, 0.6)),  # 高斯模糊
            iaa.Multiply((0.5, 1.5), per_channel=0.5),  # 亮度调整
        ])

        # 进行图像和标注数据增广
        if json_data_type == Label_Data_Type_Enum.hbb.value:
            augmented_image, augmented_bbs_on_image = augmenter(image=image,
                                                                bounding_boxes=bbs_on_image)
            # clip方法可能有点问题
            # augmented_bbs_on_image = augmented_bbs_on_image.clip_out_of_image()
        elif json_data_type == Label_Data_Type_Enum.obb.value or json_data_type == Label_Data_Type_Enum.mask.value:
            augmented_image, augmented_polys_on_image = augmenter(image=image,
                                                                  polygons=polys_on_image)
            # clip方法好像有点问题，比如之前只有4个多边形，裁完后反而变成了5个多边形，是不是1分2了
            # augmented_polys_on_image = augmented_polys_on_image.clip_out_of_image()

        cv2.imencode(image_file_suffix, augmented_image)[1].tofile(image_augment_path)

        augmented_shapes = []
        shape_index = 0
        if json_data_type == Label_Data_Type_Enum.hbb.value:
            for bb in augmented_bbs_on_image.bounding_boxes:
                x, y, w, h = bb.x1, bb.y1, bb.x2 - bb.x1, bb.y2 - bb.y1
                points = [[float(x), float(y)], [float(x + w), float(y)], [float(x + w), float(y + h)],
                          [float(x), float(y + h)]]
                # 增广后的box的顺序和原来的label顺序保持一致
                augmented_shapes.append({'label': labels[shape_index], 'points': points, 'shape_type': 'polygon'})
                shape_index += 1

        elif json_data_type == Label_Data_Type_Enum.obb.value or json_data_type == Label_Data_Type_Enum.mask.value:
            for pos in augmented_polys_on_image:
                points = [list(xy.astype(np.float64)) for xy in pos]
                # 增广后的box的顺序和原来的label顺序保持一致
                augmented_shapes.append({'label': labels[shape_index], 'points': points, 'shape_type': 'polygon'})
                shape_index += 1
        # 更新LabelMe格式的标注数据
        labelme_data['shapes'] = augmented_shapes
        labelme_data['imagePath'] = os.path.split(image_augment_path)[1]

        # 将增广后的标注数据保存
        with open(json_augment_path, 'w', encoding='utf-8') as f:
            json.dump(labelme_data, f, default=lambda x: x.tolist() if isinstance(x, np.ndarray) else x)

    @staticmethod
    def samples_augmentation_by_dir(input_image_folder, input_label_folder, output_image_folder,
                                    output_label_folder, image_aug_suffix, label_suffix, json_data_type):

        # 遍历原始图片文件夹
        # 对样本影像和样本标注进行增广
        fileindex = 1
        for filename in os.listdir(input_image_folder):
            file_suffix = os.path.splitext(filename)[1]
            if file_suffix.lower()[1:] in FileFormatConverter.img_suffix:
                print("{}/{}对{}图片进行增广处理".format(fileindex, len(os.listdir(input_image_folder)), filename))
                # 构建原始图片文件路径和标签文件路径
                image_path = os.path.join(input_image_folder, filename)
                json_path = os.path.join(input_label_folder, os.path.splitext(filename)[0] + "." + label_suffix)
                if os.path.exists(json_path):
                    # 保存增强后的原始图片和标签文件
                    if not os.path.exists(output_image_folder):
                        os.makedirs(output_image_folder)
                    if not os.path.exists(output_label_folder):
                        os.makedirs(output_label_folder)
                    image_aug_path = os.path.join(output_image_folder,
                                                  os.path.splitext(filename)[0] + image_aug_suffix + file_suffix)
                    json_aug_path = os.path.join(output_label_folder,
                                                 os.path.splitext(filename)[0] + image_aug_suffix + "." + label_suffix)
                    ImageAugmenter.sample_and_label_augment_by_file(image_path, json_path, image_aug_path,
                                                                    json_aug_path,
                                                                    file_suffix, json_data_type)
            fileindex += 1

        print("数据增强完成")

    # 批处理做样本数据增广
    @staticmethod
    def batch_augment_sample_datas(data_path, origin_labelme_data_type, need_labelme_data_type, sample_image_dir_name,
                                   hbb_label_json_dir_name,
                                   obb_label_json_dir_name,
                                   mask_label_json_dir_name,
                                   augment_file_suffix, label_suffix,
                                   image_suffix, alg_type):

        sample_pic_dir_path = os.path.join(data_path, sample_image_dir_name)
        augment_pic_folder = sample_pic_dir_path + ImageAugmenter.augment_dir_suffix
        need_label_json_dir_path = os.path.join(data_path,
                                                eval("{}_label_json_dir_name".format(need_labelme_data_type)))

        augment_label_folder = need_label_json_dir_path + ImageAugmenter.augment_dir_suffix
        FileHelper.init_dir(augment_pic_folder)
        FileHelper.init_dir(augment_label_folder)
        ImageAugmenter.samples_augmentation_by_dir(sample_pic_dir_path, need_label_json_dir_path, augment_pic_folder,
                                                   augment_label_folder, augment_file_suffix, label_suffix,
                                                   origin_labelme_data_type)
        # TODO: 将超出图像边界的样本删除掉

        # # 将增广后的图片和样本数据拷贝到和原样本和图片数据的目录
        print("将增广后的样本和图片复制到原来样本目录")
        FileHelper.sfile_to_dfile(augment_pic_folder, "." + image_suffix, sample_pic_dir_path)
        FileHelper.sfile_to_dfile(augment_label_folder, "." + label_suffix, need_label_json_dir_path)


class SampleHandler:
    def __init__(self):
        pass

    # 从样本中拆分出训练数据和验证数据
    @staticmethod
    def split_train_val_data_of_yolov8(all_image_path, all_label_path, dest_path, category_name, train_radio,
                                       valid_radio,
                                       test_radio):
        FileFormatConverter.YoloHelper.init_yolov8_data_dir(dest_path, category_name)
        img_list = os.listdir(all_image_path)
        train_img_list = []
        valid_img_list = []
        test_img_list = []

        # trainImage：训练集的图片
        # - Abyssinian_1.jpg
        # - Abyssinian_10.jpg
        # - Abyssinian_11.jpg
        # 原来的图片是类别名称加后缀数量
        # classes_set = set([i.split("_")[0] for i in img_list])  # 每个类别的名称
        # for cls in classes_set:
        #     cls_list = list(filter(lambda x: x.startswith(cls), img_list))
        #     train_num = int(len(cls_list) * train_radio)
        #     train_img_list += cls_list[:train_num]
        #     valid_img_list += cls_list[train_num:]

        train_num = int(len(img_list) * train_radio)
        valid_num = int(len(img_list) * valid_radio)
        test_num = int(len(img_list) * test_radio)
        train_img_list += img_list[:train_num]
        valid_img_list += img_list[train_num:train_num + valid_num]
        test_img_list += img_list[train_num + valid_num:train_num + valid_num + test_num]

        # 打乱数据
        random.shuffle(train_img_list)
        random.shuffle(valid_img_list)
        random.shuffle(test_img_list)

        print("num of train set is {} ".format(len(train_img_list)))
        print("num of valid set is {} ".format(len(valid_img_list)))
        print("num of test set is {} ".format(len(test_img_list)))
        print(f"total num of dataset is {len(train_img_list) + len(valid_img_list) + len(test_img_list)}")

        yolo_image_dir = os.path.join(dest_path, "datasets", category_name, "images")
        yolo_label_dir = os.path.join(dest_path, "datasets", category_name, "labels")
        SampleHandler.copy_data_to_dest_in_yolov8(train_img_list, "train", all_image_path, all_label_path,
                                                  yolo_image_dir,
                                                  yolo_label_dir)
        SampleHandler.copy_data_to_dest_in_yolov8(valid_img_list, "val", all_image_path, all_label_path, yolo_image_dir,
                                                  yolo_label_dir)
        SampleHandler.copy_data_to_dest_in_yolov8(test_img_list, "test", all_image_path, all_label_path, yolo_image_dir,
                                                  yolo_label_dir)

        # with open("train.txt", "a+",encoding='utf-8') as f:
        #     for img in train_img_list:
        #         if img.endswith(".jpg"):
        #             f.write("data/custom/images/" + img + "\n")
        # print("train.txt create sucessful!")
        #
        #
        # with open("valid.txt", "a+",encoding='utf-8') as f:
        #     for img in valid_img_list:
        #         if img.endswith(".jpg"):
        #             f.write("data/custom/images/" + img + "\n")
        # print("valid.txt create sucessful!")
        #
        #
        # train_img_dir = "trainImage/"
        # train_img_list = [os.path.join("data/custom/images/", i) for i in sorted(os.listdir(train_img_dir))]
        # train_img_list = list(map(lambda x: x + "\n", train_img_list))
        #
        # val_img_dir = "valImage/"
        # val_img_list = [os.path.join("data/custom/images/", i) for i in sorted(os.listdir(val_img_dir))]
        # val_img_list = list(map(lambda x: x + "\n", val_img_list))
        #
        # with open("train.txt", "w",encoding='utf-8') as f:
        #     f.writelines(train_img_list)
        #
        # with open("val.txt", "w",encoding='utf-8') as f:
        #     f.writelines(val_img_list)

    @staticmethod
    def copy_data_to_dest_in_yolov8(img_list, img_usage, all_image_path, all_label_path, yolo_image_dir,
                                    yolo_label_dir):
        # 复制数据到指定目录
        for img_name in img_list:
            img_name_prefix = FileHelper.get_file_name_prefix(img_name)
            label_txt_path = os.path.join(all_label_path, img_name_prefix + ".txt")
            img_path = os.path.join(all_image_path, img_name)
            # 复制图片
            copy_dest_image_path = os.path.join(yolo_image_dir, img_usage + "2017")
            shutil.copy(img_path, copy_dest_image_path)
            print("复制图片文件:从{}到{}".format(img_path, copy_dest_image_path))
            copy_dest_label_path = os.path.join(yolo_label_dir, img_usage + "2017")
            # 复制样本
            shutil.copy(label_txt_path, copy_dest_label_path)
            print("复制标注文件：从{}到{}".format(img_path, copy_dest_label_path))

    # 从样本中拆分出训练数据和验证数据
    @staticmethod
    def split_train_val_data_of_mm(sample_pic_dir_path, label_json_dir_path, mm_json_dir_path,
                                   mmdet_train_dir_path,
                                   category_name,
                                   train_radio, valid_radio, test_radio, alg_type, alg_model, label_suffix,
                                   image_suffix):
        all_image_path = sample_pic_dir_path
        all_label_path = label_json_dir_path
        dest_path = mmdet_train_dir_path
        FileFormatConverter.OpenmmLabHelper.init_mm_data_dir(dest_path, category_name)
        img_list = os.listdir(all_image_path)
        train_img_list = []
        valid_img_list = []
        test_img_list = []
        train_num = int(len(img_list) * train_radio)
        valid_num = int(len(img_list) * valid_radio)
        test_num = int(len(img_list) * test_radio)
        train_img_list += img_list[:train_num]
        valid_img_list += img_list[train_num:train_num + valid_num]
        test_img_list += img_list[train_num + valid_num:train_num + valid_num + test_num]

        # 打乱数据
        random.shuffle(train_img_list)
        random.shuffle(valid_img_list)
        random.shuffle(test_img_list)

        print("num of train set is {} ".format(len(train_img_list)))
        print("num of valid set is {} ".format(len(valid_img_list)))
        print("num of test set is {} ".format(len(test_img_list)))
        print(f"total num of dataset is {len(train_img_list) + len(valid_img_list) + len(test_img_list)}")

        mm_train_dir = os.path.join(dest_path, "data", category_name, "train")
        mm_val_dir = os.path.join(dest_path, "data", category_name, "val")
        mm_test_dir = os.path.join(dest_path, "data", category_name, "test")


        # 复制图片和标注到同一个目录
        SampleHandler.copy_data_to_dest_in_mm(train_img_list, all_image_path, all_label_path, mm_train_dir,
                                              mm_train_dir)
        SampleHandler.copy_data_to_dest_in_mm(valid_img_list, all_image_path, all_label_path, mm_val_dir,
                                              mm_val_dir)
        SampleHandler.copy_data_to_dest_in_mm(test_img_list, all_image_path, all_label_path, mm_test_dir,
                                              mm_test_dir)

        # 实例分割、目标检测
        if alg_type == Alg_Type_Enum.mmdetv3_obj_det.value or alg_type == Alg_Type_Enum.mmdetv3_ins_seg.value:
            # 转换labelme为coco
            FileFormatConverter.LablemeHelper.labelme2Coco2017(mm_train_dir, label_suffix, mm_train_dir, alg_type)
            FileFormatConverter.LablemeHelper.labelme2Coco2017(mm_val_dir, label_suffix, mm_val_dir, alg_type)
            FileFormatConverter.LablemeHelper.labelme2Coco2017(mm_test_dir, label_suffix, mm_test_dir, alg_type)
            # 删除拷贝的labelme json文件
            FileHelper.delete_files_by_condition(mm_train_dir, label_suffix, "annotation_coco.json")
            FileHelper.delete_files_by_condition(mm_val_dir, label_suffix, "annotation_coco.json")
            FileHelper.delete_files_by_condition(mm_test_dir, label_suffix, "annotation_coco.json")
        # 语义分割
        elif alg_type == Alg_Type_Enum.mmsegv1_sem_seg.value:
            # 图片后缀修改为jpg
            FileHelper.change_file_extension2(mm_train_dir, ".{}".format(image_suffix), ".jpg")
            FileHelper.change_file_extension2(mm_val_dir, ".{}".format(image_suffix), ".jpg")
            FileHelper.change_file_extension2(mm_test_dir, ".{}".format(image_suffix), ".jpg")
            # labelme转为cityscapes
            FileFormatConverter.LablemeHelper.labelme2Citycapes(mm_train_dir, label_suffix, mm_train_dir, alg_type,
                                                                category_name)
            FileFormatConverter.LablemeHelper.labelme2Citycapes(mm_val_dir, label_suffix, mm_val_dir, alg_type, category_name)
            FileFormatConverter.LablemeHelper.labelme2Citycapes(mm_test_dir, label_suffix, mm_test_dir, alg_type,
                                                                category_name)
            # 删除json文件
            FileHelper.delete_files_by_condition2(mm_train_dir, label_suffix, None)
            FileHelper.delete_files_by_condition2(mm_val_dir, label_suffix, None)
            FileHelper.delete_files_by_condition2(mm_test_dir, label_suffix, None)
            # 将原始图片移到images目录，标注图片移到lables目录，图片名称到splits
            mmsge_images_dir = os.path.join(dest_path, "data", category_name, "images")
            mmseg_labels_dir = os.path.join(dest_path, "data", category_name, "labels")
            mmseg_splits_dir = os.path.join(dest_path, "data", category_name, "splits")
            train_txt_path = os.path.join(mmseg_splits_dir, "train.txt")
            val_txt_path = os.path.join(mmseg_splits_dir, "val.txt")
            test_txt_path = os.path.join(mmseg_splits_dir, "test.txt")
            os.makedirs(mmsge_images_dir, exist_ok=True)
            os.makedirs(mmseg_labels_dir, exist_ok=True)
            os.makedirs(mmseg_splits_dir, exist_ok=True)
            train_name_list = FileHelper.move_files_by_condition(mm_train_dir, ".jpg", mmsge_images_dir)
            FileHelper.move_files_by_condition(mm_train_dir, ".{}".format(image_suffix), mmseg_labels_dir)
            val_name_list = FileHelper.move_files_by_condition(mm_val_dir, ".jpg", mmsge_images_dir)
            FileHelper.move_files_by_condition(mm_val_dir, ".{}".format(image_suffix), mmseg_labels_dir)
            test_name_list = FileHelper.move_files_by_condition(mm_test_dir, ".jpg", mmsge_images_dir)
            FileHelper.move_files_by_condition(mm_test_dir, ".{}".format(image_suffix), mmseg_labels_dir)
            FileHelper.write_list_to_file(train_txt_path, train_name_list)
            FileHelper.write_list_to_file(val_txt_path, val_name_list)
            FileHelper.write_list_to_file(test_txt_path, test_name_list)
            FileHelper.del_dir(mm_train_dir)
            FileHelper.del_dir(mm_val_dir)
            FileHelper.del_dir(mm_test_dir)

        # TODO:处理全景数据
        elif alg_type == Alg_Type_Enum.mmdetv3_pan_seg.value:
            pass

    @staticmethod
    def copy_data_to_dest_in_mm(img_list, all_image_path, all_label_path, mm_image_dir,
                                mm_label_dir):
        # 复制数据到指定目录
        img_index = 1
        for img_name in img_list:
            img_name_prefix = FileHelper.get_file_name_prefix(img_name)
            label_json_path = os.path.join(all_label_path, img_name_prefix + ".json")
            img_path = os.path.join(all_image_path, img_name)
            # 复制图片
            copy_dest_image_path = mm_image_dir
            shutil.copy(img_path, copy_dest_image_path)
            print("{}/{}:复制图片文件:从{}到{}".format(img_index, len(img_list), img_path, copy_dest_image_path))
            copy_dest_label_path = mm_label_dir
            # 复制样本
            shutil.copy(label_json_path, copy_dest_label_path)
            print("{}/{}:复制标注文件：从{}到{}".format(img_index, len(img_list), img_path, copy_dest_label_path))
            img_index += 1


class UnitTester:
    def __init__(self):
        pass

    @staticmethod
    # pascal\xml转labelme成单元测试方法
    def pascalVoc2Labelme_test():
        xml_file_path = "G:\\AI\\train_data\\样本\\oiltank\\Annotation\\xml\\oiltank_1.xml"
        # class_file_path = "G:\\AI\\train_data\\样本\\oiltank\\Annotation\\classes.names"
        pic_file_path = "G:\\AI\\train_data\\样本\\oiltank\\JPEGImages\\oiltank_1.jpg"
        json_file_path = "G:\\AI\\train_data\\样本\\oiltank\\Annotation\\labelme\\oiltank_1.json"
        FileFormatConverter.PascalVocConverter.pascalVoc2Labelme(xml_file_path, pic_file_path, json_file_path)

    @staticmethod
    def build_binary_image_by_lableme_test():
        input_pic_file_path = "G:\\AI\\train_data\\样本\\oiltank\\JPEGImages\\oiltank_1.jpg"
        result_pic_file_path = "G:\\AI\\train_data\\样本\\oiltank\\BianryImages\\oiltank_1.jpg"
        json_file_path = "G:\\AI\\train_data\\样本\\oiltank\\Annotation\\labelme\\oiltank_1.json"
        FileFormatConverter.LablemeHelper.build_binary_image_by_lableme(input_pic_file_path, result_pic_file_path,
                                                                        json_file_path)

    @staticmethod
    def UCAS2Labelme_test():
        txt_file_path = "G:\\AI\\train_data\\样本\\UCAS_AOD\\中科院大学高清航拍目标数据集合\\CAR\\P0001.txt"
        pic_file_path = "G:\\AI\\train_data\\样本\\UCAS_AOD\\中科院大学高清航拍目标数据集合\\CAR\\P0001.png"
        json_file_path = "G:\\AI\\train_data\\样本\\UCAS_AOD\\中科院大学高清航拍目标数据集合\\CAR\\P0001.json"
        FileFormatConverter.UCASConverter.UCAS2Labelme(txt_file_path, pic_file_path, json_file_path, "car")

    @staticmethod
    def HRSC2Labelme_test():
        xml_file_path = "G:\\AI\\train_data\\样本\\HRSC2016\\HRSC\\HRSC2016\\FullDataSet\\Annotations\\100000001.xml"
        pic_file_path = "G:\\AI\\train_data\\样本\\HRSC2016\\HRSC\\HRSC2016\\FullDataSet\\AllImages\\100000001.bmp"
        json_file_path = "G:\\AI\\train_data\\样本\\HRSC2016\\HRSC\\HRSC2016\\FullDataSet\\labelme\\100000001.json"
        FileFormatConverter.HRSCConverter.HRSC2Labelme(xml_file_path, pic_file_path, json_file_path, "boat")

    @staticmethod
    def Labelme2Yolo_test():
        json_file_path = "G:\\AI\\train_data\\样本\\send\\火电站\高矮烟囱_汇总\\LabelImages\\00004_3.json"
        class_file_path = "G:\\AI\\train_data\\样本\\send\\火电站\\高矮烟囱_汇总\\Yolo\\classes.names"
        txt_file_path = "G:\\AI\\train_data\\样本\\send\\火电站\\高矮烟囱_汇总\\Yolo\\labels\\00004_3.txt"
        FileFormatConverter.LablemeHelper.labelme2YoloHbb(json_file_path, class_file_path, txt_file_path)

    @staticmethod
    def AugmentSample_test():
        input_image_folder = "G:\\AI\\train_data\\样本\\send\\车辆\\SampleImages"
        input_mask_folder = "G:\\AI\\train_data\\样本\send\\车辆\\BianryImages"
        input_label_folder = "G:\\AI\\train_data\\样本\send\\车辆\\LabelImages"
        output_image_folder = "G:\\AI\\train_data\\样本\\send\\车辆\\SampleImages_Augment"
        output_mask_folder = "G:\\AI\\train_data\\样本\send\\车辆\\BianryImages_Augment"
        output_label_folder = "G:\\AI\\train_data\\样本\send\\车辆\\LabelImages_Augment"
        label_name = "CAR"
        image_aug_suffix = "_aug"

        ImageAugmenter.samples_augmentation_by_dir(input_image_folder, input_label_folder, output_image_folder,
                                                   label_name, output_label_folder, image_aug_suffix)


# 主入口,进行测试
if __name__ == '__main__':

    try:

        # 测试pascalvoc转换labelme
        # Tester.pascalVoc2Labelme_test()
        # 测试lablme标签生成二值图
        # Tester.build_binary_image_by_lableme_test()
        # 测试UCAS转labelme
        # Tester.UCAS2Labelme_test()
        # 测试HRSC转labelme
        # Tester.HRSC2Labelme_test()
        # 测试labelme转yolo
        # Tester.Labelme2Yolo_test()

        # 测试样本数据增广
        # Tester.AugmentSample_test()

        # 测试多边形转矩形框
        input_json_file = r"G:\AI\test_data\labelme\airplane1.json"
        output_json_file = r"G:\AI\test_data\labelme\airplane1-2.json"
        FileFormatConverter.LablemeHelper.convert_seg_points_to_obb_of_labelme(input_json_file, output_json_file)

        input_json_file = r"G:\AI\test_data\labelme\airplane1.json"
        output_json_file = r"G:\AI\test_data\labelme\airplane1-3.json"
        FileFormatConverter.LablemeHelper.convert_seg_points_to_hbb_of_labelme(input_json_file, output_json_file)




    except Exception as tm_exp:
        print("测试用例失败：{}".format(str(tm_exp)))
