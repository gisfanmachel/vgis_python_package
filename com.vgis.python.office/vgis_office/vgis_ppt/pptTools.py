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

# import win32com.client
import comtypes.client
from pathlib import Path
import pythoncom


class PptHelper:
    @staticmethod
    # windows环境下安装wps 或office;linux环境安装libreoffice
    def ppt2pptx(input_filepath, output_filepath, keep_active=True):
        pythoncom.CoInitialize()
        input_filepath = Path(input_filepath).resolve()
        output_filepath = Path(output_filepath).resolve()
        # ppt_app = win32com.client.Dispatch("Powerpoint.Application")
        ppt_app = comtypes.client.CreateObject("Powerpoint.Application")
        presentation = ppt_app.Presentations.Open(str(input_filepath), 0, 0, 0)
        try:
            presentation.SaveAs(str(output_filepath), FileFormat=24)
            presentation.Close()
        except:
            presentation.Close()

        if not keep_active:
            ppt_app.Quit()
        pythoncom.CoUninitialize()

