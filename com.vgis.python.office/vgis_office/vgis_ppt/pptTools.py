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
import sys
# import win32com.client
if sys.platform == 'win32':
    import comtypes.client
import subprocess
from pathlib import Path
import pythoncom


class PptHelper:
    @staticmethod
    # windows环境下安装wps 或office;linux环境安装libreoffice
    def ppt2pptx(input_filepath, output_filepath, keep_active=True):
        # 需要安装libreoffice
        if sys.platform == "linux":
            # 确保使用的是完整路径
            libreoffice_path = 'libreoffice'  # 如果libreoffice不在PATH中，需要指定完整路径
            outdir = os.path.split(output_filepath)[0]
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            oldfilename = os.path.join(outdir, os.path.split(input_filepath)[1].replace('.ppt', '.pptx'))
            command = [libreoffice_path, '--invisible', '--convert-to', 'pptx', input_filepath, '--outdir', outdir]
            # 运行命令，转换文件
            subprocess.run(command, check=True)
            # 将文件重命名为想要的文件名
            os.rename(oldfilename, output_filepath)
        elif sys.platform == "win32":
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

