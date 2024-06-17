# -*- coding:utf-8 -*-

import base64
import math
import os

import cv2
import numpy as np
from PIL import Image
from PIL import ImageDraw


class ImageHelper:
    def __init__(self):
        pass

    # 获取图片的base64码,有点问题
    @staticmethod
    def convert2Base64(image_path):
        icon = open(image_path, 'rb')
        iconData = icon.read()
        iconData = base64.b64encode(iconData)
        LIMIT = 60
        liIcon = []
        while True:
            sLimit = iconData[:LIMIT]
            iconData = iconData[LIMIT:]
            liIcon.append('\'%s\'' % sLimit)
            if len(sLimit) < LIMIT:
                break
        base64_img_str = os.linesep.join(liIcon)
        return base64_img_str

    # 根据指定范围生成二值图
    # 有值用白色，没值的用黑色
    # white_region_array二值图边缘线的坐标点:['x1,y1,x2,y2...xn,yn','x1,y1,x2,y2...xn,yn'...]
    @staticmethod
    def build_binary_image(input_pic_file_path, result_pic_file_path, white_region_array):
        # 生成黑色图片
        old_img = Image.open(input_pic_file_path)
        height = old_img.height
        width = old_img.width
        black_img = Image.new("RGB", (width, height))
        # 对指定区域进行白色填充
        for region in white_region_array:
            # region为x1,y1,x2,y2...xn,yn
            draw = ImageDraw.Draw(black_img)
            draw.polygon(region, fill=(255, 255, 255, 255), outline=(255, 255, 255, 255))
        black_img.save(result_pic_file_path)

    @staticmethod
    # 生成二值图轮廓
    # pixel_xy_list  二值图边缘线坐标点：[ndarray[n,2],ndarray[n,2]]
    # boudary_color: 轮廓线颜色，如 (0, 255, 0)
    # boudary_width: 轮廓线厚度，如 2
    def build_binary_image_boudary(input_pic_file_path, result_pic_file_path, pixel_xy_list, boudary_color,
                                   boudary_width):
        input_image = cv2.imread(input_pic_file_path)
        cv2.drawContours(input_image, pixel_xy_list, -1, boudary_color, boudary_width)
        cv2.imwrite(result_pic_file_path, input_image)

    # 获取目录下所有图片路径
    @staticmethod
    def get_image_list(image_dir,
                       suffix=['jpg', 'jpeg', 'JPG', 'JPEG', 'png', 'PNG', 'bmp', 'BMP', 'GIF', 'gif']):
        '''get all vgis_image path ends with suffix'''
        if not os.path.exists(image_dir):
            print("PATH:%s not exists" % image_dir)
            return []
        imglist = []
        for root, sdirs, files in os.walk(image_dir):
            if not files:
                continue
            for filename in files:
                filepath = os.path.join(root, filename)
                if filename.split('.')[-1] in suffix:
                    imglist.append(filepath)
        return imglist

    # 按照指定大小对图片大小进行重定义
    @staticmethod
    def resize_image_by_size(input_file_path, resize_width, resize_height, out_file_path):
        img = Image.open(input_file_path)
        new_img = img.resize((resize_width, resize_height), Image.BILINEAR)
        new_img.save(out_file_path)


    # 按照指定大小对图片大小进行重定义
    @staticmethod
    def resize_image_by_size2(input_file_path, resize_width, resize_height, out_file_path):
        # img_data = cv2.imread(input_file_path)[:, :, ::-1]
        img_data = cv2.imdecode(np.fromfile(input_file_path, dtype=np.uint8), -1)
        img_data = cv2.resize(img_data, (resize_width, resize_height))
        cv2.imencode(os.path.splitext(input_file_path)[1], img_data)[1].tofile(out_file_path)
        # cv2.imwrite(out_file_path, img_data)
    @staticmethod
    # 获取指定区域的图像
    def get_crop_region_of_image(input_img_file_path, out_img_file_path, crop_minx, crop_miny, crop_maxx, crop_maxy):
        img = cv2.imread(input_img_file_path)
        crop = img[crop_miny:crop_maxy, crop_minx:crop_maxx]
        cv2.imwrite(out_img_file_path, crop)

    @staticmethod
    # 将掩码范围外的区域设置为黑色
    # mask_region：[x1, y1, x2, y2]
    def fill_black_out_region_of_image(input_img_file_path, out_img_file_path, mask_region):

        # 读取图像
        image = cv2.imread(input_img_file_path)

        # 创建一个与输入图像相同大小的全黑图像
        black_image = np.zeros_like(image)

        # 创建一个掩码，这里假设要保留的区域在图像中的坐标范围是[x1, y1, x2, y2]
        mask = np.zeros_like(image)
        x1, y1, x2, y2 = mask_region[0], mask_region[1], mask_region[2], mask_region[3]  # 这里是示例坐标范围
        mask[y1:y2, x1:x2] = 255  # 将指定区域设置为白色（255）

        # 使用掩码将指定区域复制到全黑图像上
        black_image[mask > 0] = image[mask > 0]


        # # 显示结果
        # cv2.imshow('Result', black_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # 或者保存结果
        cv2.imwrite(out_img_file_path, black_image)

    # 裁剪大图到小图，按照crop_width, crop_height尺寸，按照尺寸进行外扩填充
    @staticmethod
    def seg_img_by_size_with_padding(input_img_file_path, crop_width, crop_height, crop_img_save_path, crop_file_prefix,
                                     file_ext):

        def __crop_image(img, crop_width, crop_height):
            # m是图像height，行数，y方向
            # n是图像width，列数，X方向
            m, n = img.shape[0], img.shape[1]

            # a1 是 裁剪的行数（边缘不够尺寸的也要裁剪算行数），Y方向
            a1 = (m // crop_height) + 1
            # b1 是 裁剪的列数（边缘不够尺寸的也要裁剪算列数），X方向
            b1 = (n // crop_width) + 1

            # a 是 Y 方向不够的像素
            a = a1 * crop_height - m
            # b 是 X 方向不够的像素
            b = b1 * crop_width - n

            # 将原影像填充,满足（crop_width,crop_height）的倍数，填充部分为黑色
            # 原来的Y 为13659 ，现在变成了13824，增加了a=165
            # 原来的X 为15632，现在变成了15772，增加了b=240
            img_padding = cv2.copyMakeBorder(img, 0, a, 0, b, cv2.BORDER_CONSTANT, value=(0, 0, 0))

            img_crops = []
            # Y方向
            for i in range(a1):
                # X 方向
                for j in range(b1):
                    img_c = img_padding[i * crop_height:(i + 1) * crop_height, j * crop_width:(j + 1) * crop_width]
                    img_crops.append(img_c)
            return img_crops

        # img_input = cv2.imread(input_img_file_path, 1)
        img_input = cv2.imdecode(np.fromfile(input_img_file_path, dtype=np.uint8), 1)

        img_input_segs = __crop_image(img_input, crop_width, crop_height)

        for j in range(len(img_input_segs)):
            output_file = os.path.join(crop_img_save_path, crop_file_prefix + '_' + str(j) + '.' + file_ext)
            # cv2.imwrite(output_file, img_input_segs[j])
            cv2.imencode("." + file_ext, img_input_segs[j])[1].tofile(output_file)
            print("生成裁剪文件:{}".format(output_file))

        print("裁剪{}*{}已保存".format(crop_width, crop_height))

    # 裁剪大图到小图，按照crop_width, crop_height尺寸，不足尺寸的保留大小
    @staticmethod
    def seg_img_by_size_with_remain(input_image_path: str, output_folder: str, crop_file_prefix: str, file_ext: str,
                                    crop_size: tuple,
                                    ) -> None:
        """
        按照制定尺寸裁切大图，如果小图不够尺寸，保留小图自己的尺寸

        @param input_image_path: 大图路径
        @param output_folder: 裁切小图所在目录，按照规定要求命令，比cropped_0.jpg,cropped_1.jpg,...cropped_n.jpg,其中n为裁切的序号
        @param crop_file_prefix:裁切图片名的前缀，比如cropped
        @param file_ext: 裁切图片的后缀
        @param crop_size: 裁切尺寸，格式为：(height,width)
        """
        print("进入大图裁剪")

        # 读取大图片
        # img = cv2.imread(input_image_path, 1)
        img = cv2.imdecode(np.fromfile(input_image_path, dtype=np.uint8), 1)

        # 图像height，行数，y方向
        # 图像width，列数，X方向
        height, width = img.shape[0], img.shape[1]
        crop_height = crop_size[0]
        crop_width = crop_size[1]

        if height <= crop_height and width <= crop_width:
            pass
        else:
            # 裁剪的行数（边缘不够尺寸的也要裁剪算行数），Y方向
            rows = math.ceil(float(height) / crop_height)
            # rows = (height // crop_height) + 1
            # 裁剪的列数（边缘不够尺寸的也要裁剪算列数），X方向
            cols = math.ceil(float(width) / crop_width)
            # cols = (width // crop_width) + 1

            # Y 方向填充的像素
            y_padd = rows * crop_height - height
            # X 方向填充的像素
            x_padd = cols * crop_width - width

            # 将原影像填充,满足裁切尺寸的倍数，填充部分为黑色
            # 原来的Y 为13659 ，现在变成了13824，增加了y_padd=165
            # 原来的X 为15632，现在变成了15772，增加了x_padd=240
            img_padding = cv2.copyMakeBorder(img, 0, y_padd, 0, x_padd, cv2.BORDER_CONSTANT, value=(0, 0, 0))

            img_crops = []
            # Y方向,循环行
            for i in range(rows):
                # X 方向,循环列
                for j in range(cols):
                    start_y = i * crop_height
                    end_y = (i + 1) * crop_height
                    start_x = j * crop_width
                    end_x = (j + 1) * crop_width
                    # 最下面的 需要去掉Y方向扩充
                    if i == rows - 1 and y_padd != 0:
                        end_y = i * crop_height + (crop_height - y_padd)
                    # 最右边的，需要去掉X方向扩展
                    if j == cols - 1 and x_padd != 0:
                        end_x = j * crop_width + (crop_width - x_padd)
                    img_c = img_padding[start_y:end_y, start_x:end_x]
                    img_crops.append(img_c)
                    # cv2.imwrite(os.path.join(output_folder, 'cropped_{}_{}.jpg'.format(i, j)), img_c)
            for t in range(len(img_crops)):
                output_file = output_folder + "/{}_{}.{}".format(crop_file_prefix, t, file_ext)
                # output_file = os.path.join(output_folder, '{}_{}.{}'.format(crop_file_prefix, t, file_ext))
                # cv2.imwrite(output_file, img_crops[t])
                cv2.imencode("." + file_ext, img_crops[t])[1].tofile(output_file)
                print("生成裁剪文件:{}".format(output_file))
            print("裁剪{}*{}已保存".format(crop_width, crop_height))

    # 将裁切后小图(不足尺寸的保留大小)拼接成大图
    @staticmethod
    def concatenate_seg_images_by_size_with_remain(input_folder: str, output_image_path: str, big_image_shape: tuple,
                                                   crop_file_prefix: str, file_ext: str,
                                                   crop_size: tuple, ) -> None:
        """
        将裁切后的小图拼成大图

        @param input_folder: 裁切小图所在目录，按照规定要求命令，如cropped_0.jpg,cropped_1.jpg,...cropped_n.jpg,其中n为裁切的序号
        @param output_image_path: 拼接后的图片路径
        @param big_image_shape: 原大图尺寸，格式为： (height,width,bands)
        @param crop_file_prefix: 裁切图片名的前缀,如 cropped
        @param file_ext: 裁切图片的后缀
        @param crop_size: 裁切尺寸，格式为：(height,width)
        """

        print("进入裁剪小图拼接大图")
        # 计算裁剪后的行数和列数
        crop_height = crop_size[0]
        crop_width = crop_size[1]
        height, width = big_image_shape
        # 裁剪的行数（边缘不够尺寸的也要裁剪算行数），Y方向
        rows = (height // crop_height) + 1
        # 裁剪的列数（边缘不够尺寸的也要裁剪算列数），X方向
        cols = (width // crop_width) + 1

        # Y 方向填充的像素
        y_padd = rows * crop_height - height
        # X 方向填充的像素
        x_padd = cols * crop_width - width

        # 创建大图的空白画布
        output_img = np.zeros((height, width, 3), dtype=np.uint8)

        # Y方向
        for i in range(rows):
            # X方向
            for j in range(cols):
                #  cols是裁剪的列数，cols * i + j 表示第几个裁剪的图片提取的变化二值图（将所有裁剪图片拉平）
                cropped_image_path = os.path.join(input_folder,
                                                  '{}_'.format(crop_file_prefix) + str(
                                                      cols * i + j) + '.' + file_ext)
                # cropped_image = cv2.imread(cropped_image_path, 1)
                cropped_image = cv2.imdecode(np.fromfile(cropped_image_path, dtype=np.uint8), 1)

                start_y = i * crop_height
                end_y = (i + 1) * crop_height
                start_x = j * crop_width
                end_x = (j + 1) * crop_width
                # 最下面的 需要去掉Y方向扩充
                if i == rows - 1 and y_padd != 0:
                    end_y = i * crop_height + (crop_height - y_padd)
                # 最右边的，需要去掉X方向扩展
                if j == cols - 1 and x_padd != 0:
                    end_x = j * crop_width + (crop_width - x_padd)
                output_img[start_y:end_y, start_x:end_x] = cropped_image

        # 保存拼接后的大图
        # cv2.imwrite(output_image_path, output_img)
        cv2.imencode("." + file_ext, output_img)[1].tofile(output_image_path)
        print("拼接大图完成")

    # 根据百分比缩放图片
    @staticmethod
    def resize_image_by_percent():
        pass

    # 对图像进行裁切，按照两条水平线
    @staticmethod
    def clip_image_by_line():
        pass

    # 在tif上绘制多边形
    @staticmethod
    def add_polygon_on_tif(tif_file):
        try:
            img = cv2.imread(tif_file, -1)
            # 输出图像信息
            # print(img)
            print(img.shape)
            print(img.dtype)
            print(img.min())
            print(img.max())
            # 读取数据，显示图像
            img = cv2.imread(tif_file, -1)
            # 将数据格式进行转换
            img = np.array(img)
            # 绘制多边形
            pts = np.array([[200, 100], [200, 300], [250, 300], [500, 200], [500, 40]], np.int32)  # 构建多边形的顶点
            cv2.polylines(img, [pts], True, (255, 0, 0), 3)

            # 设置图像窗口
            cv2.namedWindow(tif_file, 1)  # 第一个参数设置窗口名字，第二个参数"1"为根据电脑显示器自动调整窗口大小
            cv2.imshow(tif_file, img)  # 显示图像

            # 设置等待时间为0毫秒（参数0表示等待时间为无限）
            cv2.waitKey(0)

            # 释放窗口
            cv2.destroyAllWindows()
        except Exception as exp:
            print(exp)
            print(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            print(exp.__traceback__.tb_lineno)  # 发生异常所在的行数

    # 将png图片中的白色换成透明色
    # 循环速度太慢
    @staticmethod
    def transparent_back(filepath):
        # 打开图片
        image = Image.open(filepath)

        # 转换成NumPy数组
        image_data = np.array(image)

        # 获取图像的通道数
        num_channels = image_data.shape[2] if len(image_data.shape) == 3 else 1

        # 检查图像是否为RGBA格式，如果不是，则添加透明通道
        if num_channels == 3:
            # 添加一个全透明的通道
            alpha_channel = np.ones(image_data.shape[:2], dtype=image_data.dtype) * 255
            image_data = np.dstack((image_data, alpha_channel))

        # 找到白色像素并将其替换为透明像素
        white = [255, 255, 255, 255]  # 白色的RGBA值
        tolerance = 50  # 容忍度，用于允许稍微不完全白色的像素
        white_threshold = np.array([white[i] - tolerance for i in range(4)])
        is_white = np.all(image_data >= white_threshold, axis=2)
        image_data[is_white] = [0, 0, 0, 0]  # 替换为完全透明的像素

        # 创建一个新的Image对象
        new_image = Image.fromarray(image_data)

        # 保存结果图像
        new_image.save(filepath)


# AI样本二值图生成单元测试方法
def build_binary_image_test(image_operator):
    while_region_array = []
    while_region_array.append([11, 45, 34, 55, 67, 44, 14, 55])
    while_region_array.append([101, 450, 340, 550, 670, 440, 140, 550])
    image_operator.build_binary_image("d:\\airport.jpg", "d:\\airport_bin.jpg", while_region_array)

# # 主入口,进行测试
# if __name__ == '__main__':
#     try:
#         image_operator = ImageOperator()
#         build_binary_image_test(image_operator)
#     except Exception as tm_exp:
#         print("AI样本二值图生成失败：{}".format(str(tm_exp)))
