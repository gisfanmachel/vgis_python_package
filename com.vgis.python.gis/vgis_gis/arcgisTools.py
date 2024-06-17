"""
===================================
#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
@Author: chenxw
@Email : gisfanmachel@gmail.com
@File: arcgisTools.py
@Date: Create in 2021/2/5 9:37
@Description:
arcgis的Python
arcgis desktop只支持python2.7
需要安装arcgis desktop
配置pycharm的python环境，C:\Python27\ArcGIS10.5/python.exe
# D:\Program Files (x86)\ArcGIS\Desktop10.5\arcpy；
# D:\Program Files (x86)\ArcGIS\Desktop10.5\ArcToolbox\Scripts；
# D:\Program Files (x86)\ArcGIS\Desktop10.5\bin
@ Software: PyCharm
===================================
"""
# import arcpy
#
#
# # ArcGIS Pro的Arcpy原生支持Python3
#
# mypath=r"C:\Users\Administrator\Desktop\huodianchang\shanxi.mxd"
# mxd = arcpy.mapping.MapDocument(mypath)
#
# # df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
# # theShape = r"E:\zgl.shp"
# # addLayer = arcpy.mapping.Layer(theShape)
# # arcpy.mapping.AddLayer(df, addLayer, "AUTO_ARRANGE")
# # arcpy.RefreshActiveView()
# # arcpy.RefreshTOC()
# # mxd.save()
#
#
# #图层
# lyr = arcpy.mapping.ListLayers(mxd)[0]
# #数据框
# df = arcpy.mapping.ListDataFrames(mxd)[0]
# rows = arcpy.SearchCursor(lyr)
# for row in rows:
#     geo = row.shape
#     #要素名称字段
#     name = row.getValue("name")
#     #数据框范围以当前要素为中心
#     df.panToExtent(geo.extent)
#     arcpy.mapping.ExportToPNG(mxd, r"C:/Users/Administrator/Desktop/huodianchang/shanxitu/" + name + ".png", 300)


