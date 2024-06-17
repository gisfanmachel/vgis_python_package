#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2022/10/28 18:51
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : rsTools.py
# @Descr   : 
# @Software: PyCharm
import os

import cv2
import numpy as np
from osgeo import gdal, ogr
from osgeo import osr
from vgis_gis.shpTools import ShpFileOperator


class RsToolsOperatoer:
    # 初始化
    def __init__(self, wms_server):
        pass

    @staticmethod
    # 获取tif的地图空间范围
    def get_Env_Tif(tif_path):
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")  # 支持中文路径
        dataset = gdal.Open(tif_path)  # 打开tif
        adfGeoTransform = dataset.GetGeoTransform()  # 读取tif的六参数
        iXSize = dataset.RasterXSize  # 列数
        iYSize = dataset.RasterYSize  # 行数
        return RsToolsOperatoer.get_env_from_gdal_transfrorm(adfGeoTransform, iXSize, iYSize)

    @staticmethod
    # 获取tif的gdal几何变换参数
    def get_gdal_transfrorm_of_tif(tif_path):
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")  # 支持中文路径
        dataset = gdal.Open(tif_path)  # 打开tif
        adfGeoTransform = dataset.GetGeoTransform()  # 读取tif的六参数
        return adfGeoTransform

    @staticmethod
    # 通过gdal几何转换参数获取地图坐标范围
    def get_env_from_gdal_transfrorm(gdal_transform, pic_width, pic_height):
        # 左上角
        pic_minx = gdal_transform[0]
        pic_maxy = gdal_transform[3]
        # 右下角
        pic_maxx = gdal_transform[0] + pic_width * gdal_transform[1] + pic_height * gdal_transform[2]
        pic_miny = gdal_transform[3] + pic_width * gdal_transform[4] + pic_height * gdal_transform[5]
        return [pic_minx, pic_miny, pic_maxx, pic_maxy]

    @staticmethod
    # 得到图片同名的world文件
    def get_world_file_of_image_file(img_path):
        file_pre_path, file_name = os.path.split(img_path)
        shotname, suffix = os.path.splitext(file_name)
        world_file_path = None
        if suffix.lower() != ".tif" or suffix.lower() != ".tiff" or suffix.lower() != ".geotiff":
            if suffix == ".jpg" or suffix == ".jpeg":
                world_file_suffix = "jgw"
            elif suffix == ".png":
                world_file_suffix = "pgw"
            world_file_path = os.path.join(file_pre_path, "{}.{}".format(shotname, world_file_suffix))
        return world_file_path

    @staticmethod
    # 生成jgw/pgw --world file世界投影文件
    def build_world_file_of_image(img_path, resolution, left_x, top_y):
        file_pre_path, file_name = os.path.split(img_path)
        shotname, suffix = os.path.splitext(file_name)
        RsToolsOperatoer.get_world_file_of_image_file(img_path)
        world_file_suffix = "jgw"
        if suffix.lower() == ".jpg" or suffix.lower() == ".jpeg":
            world_file_suffix = "jgw"
        elif suffix.lower() == ".png":
            world_file_suffix = "pgw"
        file_pre_path, file_name = os.path.split(img_path)
        shotname, suffix = os.path.splitext(file_name)
        world_file_path = os.path.join(file_pre_path, "{}.{}".format(shotname, world_file_suffix))
        with open(world_file_path, 'w') as file:
            # 在X方向的比例关系;每像素对应的经度值
            file.write("{}\n".format(resolution))
            # 影像数据的旋转参数，一般忽略，记录为0
            file.write("0.0000000000\n")
            # 影像数据的旋转参数，一般忽略，记录为0
            file.write("0.0000000000\n")
            # 在Y方向的比例关系;;每像素对应的纬度值，为负值, 这是由于空间坐标系与影像图片像素坐标系在Y方向上相反
            file.write("-{}\n".format(resolution))
            # 影像图片左上角点对应的空间坐标的X坐标
            file.write(str(left_x) + "\n")
            # 影像图片左上角点对应的空间坐标的Y坐标
            file.write(str(top_y) + "\n")
        return world_file_path

    @staticmethod
    # 获取图片的地图坐标范围
    def get_env_of_pic(pic_file_path, world_file_path):
        # img = cv2.imread(pic_file_path)
        img = cv2.imdecode(np.fromfile(pic_file_path, dtype=np.uint8), -1)
        gdal_transform = RsToolsOperatoer.convert_jgw_to_gdaltransform(world_file_path)
        return RsToolsOperatoer.get_env_from_gdal_transfrorm(gdal_transform, img.shape[1], img.shape[0])

    @staticmethod
    # 栅格转矢量
    def raster_to_vector(src_file, src_transform, dst_file, output_format):
        # 在使用 GDAL 栅格转矢量时，一般默认输入的栅格数据带有地理信息，如果输入的图片不带有地理信息，则会出现矢量化结果与原图上下反转；
        if gdal.GetDriverCount() == 0:
            gdal.AllRegister()

        if ogr.GetDriverCount() == 0:
            ogr.RegisterAll()

        # 获取地理坐标时应注意的问题
        # os.environ["GDAL_DATA"] = "E:/gdal232/data"  # 设置环境变量，防止在设置、获取投影坐标时出错
        os.environ["GDAL_FILENAME_IS_UTF8"] = "NO"  # 解决中文乱码问题
        # # 为了支持中文路径，请添加下面这句代码
        # gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        # # 为了使属性表字段支持中文，请添加下面这句
        # gdal.SetConfigOption("SHAPE_ENCODING", "CP936")

        # 读取栅格数据
        src_ds = gdal.Open(src_file, gdal.GA_ReadOnly)

        if src_ds is None:
            print("输入图像数据为空！")
            return 0

        # 自定义坐标系
        # 如果输入的栅格数据没有地理信息的话，需要自定义坐标系，否则矢量化结果与原数据程垂直镜像对称
        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromEPSG(4326)  # WGS84地理坐标系

        src_ds.SetProjection(spatial_reference.ExportToWkt())

        # 坐标信
        # 左上角点坐标X
        # x方向的分辨
        # 旋转系数，如果为0，就是标准的正北向图像
        # 左上角点坐标Y
        # 旋转系数，如果为0，就是标准的正北向图像
        # Y方向的分辨率

        # padf_transform = [114.0, 0.000001, 0, 34.0, 0, -0.000001]

        src_ds.SetGeoTransform(src_transform)

        # 根据输出格式创建输出矢量文件
        driver = ogr.GetDriverByName(output_format)

        if driver is None:
            print(f"{output_format} driver not available.")
            return 0

        # 根据文件名创建输出矢量数据集
        dst_ds = driver.CreateDataSource(dst_file)

        if dst_ds is None:
            print("创建矢量文件失败！")
            return 0

        # spatial_reference = src_ds.GetSpatialRef()

        # 定义空间参考，与输入图像相同
        spatial_ref = osr.SpatialReference()
        spatial_ref.ImportFromWkt(src_ds.GetProjectionRef())

        # 创建图层
        layer = dst_ds.CreateLayer("DstLayer", spatial_ref, ogr.wkbPolygon)

        if layer is None:
            src_ds = None
            dst_ds = None
            return 0

        # 创建属性表，只有一个字段即“value”，里面保存对应栅格的像元值
        field_defn = ogr.FieldDefn("value", ogr.OFTInteger)

        if layer.CreateField(field_defn) != ogr.OGRERR_NONE:
            print("Creating Name field failed.")
            return 0

        # 获取图像的第一个波段
        src_band = src_ds.GetRasterBand(1)

        # 调用栅格矢量化
        gdal.Polygonize(src_band, None, layer, 0, [], callback=None)

        dst_ds.SyncToDisk()

        # src_ds.FlushCache()

        src_ds = None  # 关闭文件
        dst_ds = None

        del src_ds
        del dst_ds
        gdal.GDALDestroyDriverManager()

        return 1

    @staticmethod
    # jpw转换gdal几何转换参数
    def convert_jgw_to_gdaltransform(jgwFilePath: str) -> list:
        """
        将世界投影文件jpw格式转为gdal的投影六参数数组
        jpw格式为：0.0000197051\n 0.0000000000\n 0.0000000000\n -0.0000197051\n 104.595572656171356\n 38.815550616869423\n
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
                          float(y_leftupper_value),
                          float(y_rotate_value),
                          float(y_scale_value)]
        return gdal_transform

    @staticmethod
    # JGP转tif
    def convert_jpg_to_tif(input_jpg_file, out_tif_file):

        # 输入和输出文件路径
        input_file = input_jpg_file
        output_file = out_tif_file

        # 打开JPEG文件
        jpeg_dataset = gdal.Open(input_file)

        # 获取JPEG文件的宽度、高度和波段数
        width = jpeg_dataset.RasterXSize
        height = jpeg_dataset.RasterYSize
        band_count = jpeg_dataset.RasterCount

        # 创建TIFF文件
        driver = gdal.GetDriverByName('GTiff')
        tiff_dataset = driver.Create(output_file, width, height, band_count, gdal.GDT_Byte)

        # 将JPEG文件的内容复制到TIFF文件中
        for i in range(1, band_count + 1):
            band = jpeg_dataset.GetRasterBand(i)
            data = band.ReadAsArray()
            tiff_dataset.GetRasterBand(i).WriteArray(data)

        # 设置TIFF文件的投影和地理转换信息（可选）
        file_pre_path, file_name = os.path.split(input_jpg_file)
        shotname, _ = os.path.splitext(file_name)
        jgw_file_path = os.path.join(file_pre_path, "{}.jgw".format(shotname))
        src_transform = RsToolsOperatoer.convert_jgw_to_gdaltransform(jgw_file_path)

        # 自定义坐标系
        if jpeg_dataset.GetProjection() is None:
            # 如果输入的栅格数据没有地理信息的话，需要自定义坐标系，否则矢量化结果与原数据程垂直镜像对称
            spatial_reference = osr.SpatialReference()
            spatial_reference.ImportFromEPSG(4326)  # WGS84地理坐标系
            jpeg_dataset.SetProjection(spatial_reference.ExportToWkt())
        if jpeg_dataset.GetGeoTransform() is None:
            # 坐标信息
            # 左上角点坐标X
            # x方向的分辨
            # 旋转系数，如果为0，就是标准的正北向图像
            # 左上角点坐标Y
            # 旋转系数，如果为0，就是标准的正北向图像
            # Y方向的分辨率
            # padf_transform = [114.0, 0.000001, 0, 34.0, 0, -0.000001]
            jpeg_dataset.SetGeoTransform(src_transform)

        tiff_dataset.SetProjection(jpeg_dataset.GetProjection())
        tiff_dataset.SetGeoTransform(jpeg_dataset.GetGeoTransform())

        # 关闭文件
        jpeg_dataset = None
        tiff_dataset = None

    @staticmethod
    # tif转为jpg
    def convert_tif_to_jpg(input_tif_file, out_jpg_file):
        os.system(
            """
                gdal_translate -of jpeg -a_nodata 0 -b 1 -b 2 -b 3 {} {}
            """.format(
                input_tif_file,
                out_jpg_file
            )
        )

    @staticmethod
    # 用shp裁剪栅格文件
    # 需要gdal命令环境
    # 如果被裁切的影像没有坐标系，则裁切矢量也需要没有坐标系
    # 如果被裁切的影像有坐标系，则裁切矢量可以有也可以没有坐标系
    # 如果不是png或jpg,还需要生成pgw，jgw世界投影文件
    def clip_raster_by_shape(input_raster_path, clip_shp_path, out_raster_path, s_srs=None, t_srs=None):
        cmd_str = "gdalwarp -cutline {} -crop_to_cutline {} {}".format(clip_shp_path, input_raster_path,
                                                                       out_raster_path)
        if s_srs is not None:
            cmd_str+=" -s_srs {}".format(s_srs)
        if t_srs is not None:
            cmd_str+=" -t_srs {}".format(t_srs)
        print(cmd_str)
        os.system(cmd_str)

        # 针对不是tif的栅格文件，需要补充生成world投影文件
        file_pre_path, file_name = os.path.split(out_raster_path)
        shotname, suffix = os.path.splitext(file_name)
        if suffix.lower() != ".tif" or suffix.lower() != ".tiff" or suffix.lower() != ".geotiff":
            left_x, _, _, top_y = ShpFileOperator.get_layer_envlope(clip_shp_path)
            input_raster_world_file_path = RsToolsOperatoer.get_world_file_of_image_file(input_raster_path)
            with open(input_raster_world_file_path, "r") as file:
                revolution = file.readline().rstrip("\n")
            RsToolsOperatoer.build_world_file_of_image(out_raster_path, revolution, left_x, top_y)


if __name__ == '__main__':
    # image_path = 'G:\\AI\\test_data\\storagetank\\storagetank1.jpeg'
    # jgw_ptah = 'G:\\AI\\test_data\\storagetank\\storagetank1.jgw'
    # print(RsToolsOperatoer.get_env_of_pic(image_path, jgw_ptah))
    input_raster_path = "G:\\data\\ai_test\\2019human.png"
    out_raster_path = "G:\\data\\ai_test\\clip6_2019human.png"
    clip_shp_path = "G:\\data\\test\\polygon6.shp"
    RsToolsOperatoer.clip_raster_by_shape(input_raster_path, clip_shp_path, out_raster_path)
