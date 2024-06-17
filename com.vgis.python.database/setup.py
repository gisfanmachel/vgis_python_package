#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/6/27 14:35
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : setup.py
# @Descr   : 安装文档
# @Software: PyCharm


import pathlib

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README vgis_file
long_description = (here / "README.md").read_text(encoding="utf-8")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(

    name="vgis_database",  # Required 项目名称
    version="1.0.17",  # Required 发布版本号
    description="A libary for database operator",  # Optional 项目简单描述
    long_description=long_description,  # Optional 详细描述
    long_description_content_type="text/markdown",  # 内容类型
    url="https://github.com/gisfanmachel/vgisDatabase",  # Optional github项目地址
    author="gisfanmachel",  # Optional 作者
    author_email="gisfanmachel@gmail.com",  # Optional 作者邮箱
    classifiers=[  # Optional 分类器通过对项目进行分类来帮助用户找到项目, 以下除了python版本其他的 不需要改动

        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Pick your license2 as you wish
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],

    keywords="database,setuptools,development",  # Optional 搜索关键字

    packages=find_packages(),  # Required

    # # 打包要包含的文件,把编译pyd打包进去
    # package_data={
    #     'vgis_database': ["*.pyd"]
    # },

    # include_package_data=True,
    # 打包要排除的文件,不起作用，只能打包时，手工把py文件移除，打包后再移入
    # exclude_package_data={
    #     'vgis_database': ['*.py']
    # },
    python_requires=">=3.7, <4",  # python 版本要求

    install_requires=["psycopg2-binary", "vgis-utils", "loguru"],  # Optional 第三方依赖库

)
