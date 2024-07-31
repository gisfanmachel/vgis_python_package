"""
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Project :vgis_python_package
@File    :pptTools.py
@IDE     :PyCharm
@Author  :chenxw
@Date    :2024/7/31 14:47
@Descr:
"""
import os

import win32com.client
from pathlib import Path

class PptHelper:
    @staticmethod
    def ppt2pptx(input_filepath, output_filepath, keep_active=True):
        input_filepath = Path(input_filepath).resolve()
        output_filepath = Path(output_filepath).resolve()
        ppt_app = win32com.client.Dispatch("Powerpoint.Application")
        presentation = ppt_app.Presentations.Open(str(input_filepath), 0, 0, 0)
        try:
            presentation.SaveAs(str(output_filepath), FileFormat=24)
            presentation.Close()
        except:
            presentation.Close()

        if not keep_active:
            ppt_app.Quit()

    @staticmethod
    def wps2docx(wps_file_path, save_path):
        # 使用 WPS 打开文档
        wps = win32com.client.Dispatch("Kwps.Application")
        wps.Visible = False  # 可选，设置是否显示 WPS 界面
        doc = wps.Documents.Open(os.path.abspath(wps_file_path), ReadOnly=1)
        if wps_file_path == save_path:
            os.remove(wps_file_path)
        # 另存为 docx 文件
        doc.SaveAs(os.path.abspath(save_path), 12)  # 12 表示 docx 格式

        # 关闭文档和 WPS 应用
        doc.Close()
        wps.Quit()

    @staticmethod
    def doc2docx(input_filepath, output_filepath, keep_active=True):
        input_filepath = Path(input_filepath).resolve()
        output_filepath = Path(output_filepath).resolve()
        word_app = win32com.client.Dispatch("Word.Application")
        doc = word_app.Documents.Open(str(input_filepath))
        try:
            doc.SaveAs2(str(output_filepath), FileFormat=16)
            doc.Close(0)
        except:
            doc.Close(0)

        if not keep_active:
            word_app.Quit()