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

    name="vgis_rs",  # Required 项目名称
    version="1.1.6",  # Required 发布版本号
    description="A libary for rs operator",  # Optional 项目简单描述
    long_description=long_description,  # Optional 详细描述
    long_description_content_type="text/markdown",  # 内容类型
    url="https://github.com/gisfanmachel/vgisRs",  # Optional github项目地址
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

    keywords="rs,setuptools,development",  # Optional 搜索关键字

    packages=find_packages(),  # Required

    python_requires=">=3.7, <4",  # python 版本要求

    install_requires=["opencv-python", "Pillow","vgis_gis"],
    # Optional 第三方依赖库

)
