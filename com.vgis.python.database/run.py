"""
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Project :pythonCodeSnippet
@File    :run.py.py
@IDE     :PyCharm
@Author  :chenxw
@Date    :2023/10/8 14:13
@Descr:
"""
import os
import shutil
import time

version = "1.0.16"
libname = "vgis_database"
username = "gisfanmachel"
password = "Root123^**"
remove_pys = ["pgTools.py", "pgUtils.py"]
temp_dir = "temp"

# 删除 build,dist,vgis_database.egg-info 文件夹
dir_names = ["build", "dist", "{}.egg-info".format(libname)]
for dir_name in dir_names:
    dir_path = os.path.join(os.getcwd(), dir_name)
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

# 临时移出不要打包的py文件
tmp_dir_path = os.path.join(os.getcwd(), "tmp")
if os.path.exists(tmp_dir_path):
    shutil.rmtree(tmp_dir_path)
os.makedirs(tmp_dir_path)
for remove_py in remove_pys:
    shutil.move(os.path.join(os.getcwd(), libname, remove_py), tmp_dir_path)

# 执行python setup.py sdist bdist_wheel
os.system("python setup.py sdist bdist_wheel")

# 执行twine upload dist/*，没有成功，认证没通过,在pycharm终端中单独执行可以通过
os.system("twine upload dist/* -u gisfanmachel -p Root123^**")
# os.system("twine upload dist/* -u {} -p {}".format(username, password))

# 将临时移出的py文件还原
for remove_py in remove_pys:
    shutil.move(os.path.join(tmp_dir_path, remove_py), os.path.join(os.getcwd(), libname))

# 延迟3秒
time.sleep(3)

# 更新python库,没有成功
# pip install vgis-database==1.0.3 -i https://pypi.python.org/simple/
os.chdir("C:/Users/Administrator")
os.system("pip install {}=={} -i https://pypi.python.org/simple/".format(libname, version))
