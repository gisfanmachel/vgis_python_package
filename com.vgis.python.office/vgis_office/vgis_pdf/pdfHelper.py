#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/3/23 19:03
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : pdfHelper.py
# @Descr   : pdf操作
# @Software: PyCharm
import os

import comtypes.client
import fitz


# 将pdf转换为img
@staticmethod
def convert_pdf_to_img(pdf_file):
    doc = fitz.open(pdf_file)
    (file_pre_path, temp_filename) = os.path.split(pdf_file)
    (shot_name, file_ext) = os.path.splitext(temp_filename)
    img_path_list = []
    for pg in range(doc.pageCount):
        page = doc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为3，这将为我们生成分辨率提高6倍的图像。
        zoom_x, zoom_y = 3, 3
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pm = page.getPixmap(matrix=trans, alpha=False)
        img_path = os.path.join(file_pre_path, shot_name + "_" + str(pg) + ".png")
        img_path_list.append(img_path)
        pm.writePNG(img_path)
    return "&&&".join(img_path_list)


# 将word转pdf
@staticmethod
def convert_doc_to_pdf(word_path, pdf_path):
    (file_pre_path, temp_filename) = os.path.split(word_path)
    (shot_name, file_ext) = os.path.splitext(temp_filename)
    # pdf_path = os.path.join(file_pre_path, shot_name + '.pdf')
    comtypes.CoInitialize()
    word = comtypes.client.CreateObject("Word.Application")
    word.Visiable = 0  # 设置可见性，不可见
    newpdf = word.Documents.Open(word_path)
    newpdf.SaveAS(pdf_path, FileFormat=17)  # 17表示PDF格式
    newpdf.Close()
    return pdf_path


