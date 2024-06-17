"""
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Project :pythonCodeSnippet
@File    :zipTools.py
@IDE     :PyCharm
@Author  :chenxw
@Date    :2024/3/21 15:22
@Descr:  解压缩
"""

import os
import platform
import shutil
import zipfile


class ZipHelper:
    def __int__(self):
        pass

    @staticmethod
    # 解压过程中的文件夹创建
    def my_own_makedirs(filePath):
        '''
        递归创建文件夹，filePath从根目录开始判断，如果有那一层路径不存在就创建
        例如filePath为D:/报告/123.zip，那么程序会首先判断D:/是否存在，如果不存在则会创建；
        接下来会判断 D:/报告 是否存在，如果不存在则会创建；
        这个函数只会创建文件夹，而不会创建文件。
        :param filePath: 文件的路径，注意不是文件夹的路径，例如：D:/123.zip，字符串格式
        :return: None
        '''
        # print(filePath)
        dash_str = "\\"
        if platform.system() == 'Windows':
            dash_str = "\\"
        else:
            dash_str = "/"

        filePath = filePath.replace("/", dash_str)
        folderList = filePath.split(dash_str)[0:-1]
        # print(folderList)
        currenPath = folderList[0] + dash_str
        for i in range(0, len(folderList)):
            currenPath = os.path.join(currenPath, folderList[i])
            # print(currenPath)
            if os.path.isdir(currenPath):
                # print("存在")
                pass
            else:
                print(currenPath + "不存在,开始创建")
                os.mkdir(currenPath)

    # 解决解压中的中文问题
    # 改造zipfile的编码方式
    # 会将zip包的文件，直接解压到指定目录下
    @staticmethod
    def unzipFile(zipFilePath, destPath):
        if not os.path.exists(destPath):
            os.makedirs(destPath)
        '''
        解决解压zip包时的中文乱码问题
        :param zipFilePath: 压缩文件的地址
        :param destPath: 解压后存放的的目标位置
        :return: None
        '''

        with zipfile.ZipFile(file=zipFilePath, mode='r') as zf:
            # 解压到指定目录,首先创建一个解压目录
            unzip_dir_path = destPath
            if not os.path.exists(unzip_dir_path):
                os.mkdir(unzip_dir_path)

            for old_name in zf.namelist():
                # print(zf.namelist())
                # print("old_name:",old_name)
                # 获取文件大小，目的是区分文件夹还是文件，如果是空文件应该不好用。
                file_size = zf.getinfo(old_name).file_size
                # print(file_size)
                # 由于源码遇到中文是cp437方式，所以解码成gbk，windows即可正常
                new_name = old_name.encode('cp437').decode('gbk')
                # # 拼接文件的保存路径
                new_path = os.path.join(unzip_dir_path, new_name)
                # print(new_path)
                ZipHelper.my_own_makedirs(new_path)
                # 判断文件是文件夹还是文件
                if file_size > 0:
                    # 是文件，通过open创建文件，写入数据

                    with open(file=new_path, mode='wb') as f:
                        # zf.read 是读取压缩包里的文件内容
                        f.write(zf.read(old_name))
                # else:
                #     # 是文件夹，就创建
                #     os.mkdir(new_path)

    @staticmethod
    # 对整个文件夹进行压缩，生成与文件夹同名的zip文件(里面没有当前文件夹，直接是文件夹下的文件及子文件夹），并且与当前文件夹同级目录
    def zipFiles(zip_dir):
        shutil.make_archive(zip_dir, "zip", root_dir=zip_dir)


if __name__ == '__main__':
    # zip_dir="G:\\data\\test"
    # ZipHelper.zipFiles(zip_dir)
    zip_file_path = "G:\\data\\test2.zip"
    dest_dir = "G:\\data\\test2"
    ZipHelper.unzipFile(zip_file_path, dest_dir)
