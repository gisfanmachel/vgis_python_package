"""
===================================
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Author: chenxw
@Email : gisfanmachel@gmail.com
@File: geoserverTools.py
@Date: Create in 2021/1/28 13:14
@Description: GeoServer操作类
@ Software: PyCharm
===================================
"""
import base64
import os
import requests as req
from vgis_utils.vgis_datetime.datetimeTools import DateTimeHelper


class GeoserverOperatoer:

    # 初始化
    def __init__(self, geoserver_http_address, username, password):
        # "http://192.168.3.77:8085/geoserver"
        self.geoserver_http_address = geoserver_http_address
        self.serect = username + ":" + password
        self.basic_auth = "Basic " + str(base64.b64encode(self.serect.encode("utf-8")), "utf-8")

    # 清除服务缓存
    def clear_geoserver_cache(self):
        cmd = 'curl -v -u {} -X POST {}/rest/reset -H  "accept: application/json" -H  "content-type: application/json"'.format(
            self.serect, self.geoserver_http_address)
        print(cmd)
        os.system(cmd)

    # 发布geoserver tif 图层服务
    def publish_raster_layer_service(self, tif_path, workspacename, layer_name):
        print("发布栅格图层服务{}".format(layer_name))
        url = self.geoserver_http_address + "/rest/workspaces/" + workspacename + "/coveragestores/" + layer_name + "/vgis_file.geotiff"
        # Authorization信息在postman测试用例里看
        headers = {
            'Content-type': 'vgis_image/tiff',
            'Authorization': self.basic_auth
        }
        file = open(tif_path, 'rb')
        payload = file.read()
        response = req.request("PUT", url, headers=headers, data=payload)
        print(response.text)

    # 去除栅格图层的黑边
    def clear_black_raster_layer_service(self, workspacename, datastore_name, layer_name):

        print("去除黑边")
        url = "{}/rest/workspaces/{}/coveragestores/{}/coverages/{}".format(self.geoserver_http_address, workspacename,
                                                                            datastore_name, layer_name)

        payload = "<coverage>   \r\n    <parameters>\r\n    <entry>\r\n      <vgis_string>InputTransparentColor</vgis_string>\r\n      <vgis_string>#000000</vgis_string>\r\n    </entry>\r\n  </parameters>\r\n</coverage>\r\n"
        headers = {
            'Content-Type': 'application/xml',
            'Authorization': self.basic_auth
        }

        response = req.request("PUT", url, headers=headers, data=payload)

        print(response.text)

    # 判断是否有图层存在
    def is_has_layer(self, layer_name):
        ishas = False
        url = "{}/rest/layers/{}".format(self.geoserver_http_address, layer_name)
        payload = ""
        headers = {
            'Authorization': self.basic_auth
        }
        response = req.request("GET", url, headers=headers, data=payload)
        if "No such layer" not in response.text:
            ishas = True

        return ishas

    # 发布geoserver shp 图层服务
    # TODO:有问题，针对部分shp不能自动识别空间范围和srs
    def publish_shp_layer_service(self, shp_path, layer_name, workspacename, layer_style_color):
        print("发布矢量图层服务{}".format(layer_name))
        url = self.geoserver_http_address + "/rest/workspaces/" + workspacename + "/datastores/" + layer_name + "/vgis_file.shp"
        file = open(shp_path, 'rb')
        payload = file.read()
        headers = {
            'Content-type': 'application/zip',
            'Authorization': self.basic_auth
        }
        response = req.request("PUT", url, headers=headers, data=payload)
        print(response.text)

    # 发布postgis矢量图层
    def publish_postgis_feature_service(self, layer_name, workspace_name, pg_datastore_name):
        cmd = 'curl -v -u {} -XPOST -H "Content-type: text/xml" -d  "<featureType><name>{}</name></featureType>" {}/rest/workspaces/{}/datastores/{}/featuretypes '.format(
            self.serect, layer_name, self.geoserver_http_address, workspace_name, pg_datastore_name)
        print(cmd)
        os.system(cmd)

    # 发布geoserver图层组服务
    def publish_layer_group_service(self, layer_group_name, workspacename, layer_name_list):
        print("发布图层组服务{}".format(layer_group_name))
        base_layer_name = layer_name_list[0]
        base_layer_info = self.get_layer_info(base_layer_name)
        layergroup_url = self.geoserver_http_address + "/rest/layergroups"
        layergroup_payload = "<layerGroup><name>" + layer_group_name + "</name><mode>SINGLE</mode><title>" + layer_group_name + "</title><workspace><name>" + workspacename + "</name></workspace>"
        layergroup_payload += "<layers>"
        for i in range(len(layer_name_list)):
            if layer_name_list[i] != None and layer_name_list[i].strip() != "":
                layergroup_payload += "<layer>" + layer_name_list[i] + "</layer>"
        layergroup_payload += "</layers>"
        layergroup_payload += "<styles>"
        for w in range(len(layer_name_list)):
            if layer_name_list[i] != None and layer_name_list[i].strip() != "":
                layergroup_payload += "<style>" + self.get_layer_style(layer_name_list[w]) + "</style>"
        layergroup_payload += "</styles>"
        layergroup_payload += "<bounds><minx>" + str(base_layer_info.get("minx")) + "</minx><maxx>" + str(
            base_layer_info.get("maxx")) + "</maxx><miny>" + str(base_layer_info.get("miny")) + "</miny><maxy>" + str(
            base_layer_info.get("maxy")) + "</maxy><crs>" + base_layer_info.get("srs") + "</crs></bounds></layerGroup>"
        print(layergroup_payload)
        layergroup_headers = {
            'Content-type': 'text/xml',
            'Authorization': self.basic_auth
        }
        curl_post_layergroup_response = req.request("POST", layergroup_url, headers=layergroup_headers,
                                                    data=layergroup_payload)
        print(curl_post_layergroup_response.text)

    # 得到图层信息，包括空间范围、坐标系等
    def get_layer_info(self, layer_name):
        url = self.geoserver_http_address + "/rest/layers/" + layer_name
        payload = {}
        headers = {
            'Authorization': self.basic_auth
        }
        response = req.request("GET", url, headers=headers, data=payload)
        # print(response.text)
        response.encoding = 'utf-8'
        results = response.json()
        layer_prop_href = results.get("layer").get("resource").get("href")
        style_name = results.get("layer").get("defaultStyle").get("name")
        layer_response = req.request("GET", layer_prop_href, headers=headers)
        layer_response.encoding = 'utf-8'
        layer_results = layer_response.json()
        srs = layer_results.get("coverage").get("srs")
        minx = layer_results.get("coverage").get("nativeBoundingBox").get("minx")
        miny = layer_results.get("coverage").get("nativeBoundingBox").get("miny")
        maxx = layer_results.get("coverage").get("nativeBoundingBox").get("maxx")
        maxy = layer_results.get("coverage").get("nativeBoundingBox").get("maxy")
        obj = {}
        obj["style_name"] = style_name
        obj["srs"] = srs
        obj["minx"] = minx
        obj["miny"] = miny
        obj["maxx"] = maxx
        obj["maxy"] = maxy
        return obj

    # 获取图层的样式名称
    def get_layer_style(self, layer_name):
        url = self.geoserver_http_address + "/rest/layers/" + layer_name
        payload = {}
        headers = {
            'Authorization': self.basic_auth
        }
        response = req.request("GET", url, headers=headers, data=payload)
        # print(response.text)
        response.encoding = 'utf-8'
        results = response.json()
        style_name = results.get("layer").get("defaultStyle").get("name")
        return style_name

    # 删除geoserver图层服务
    def delete_layer_service(self, layer_name):
        print("删除图层服务{}".format(layer_name))
        curl_delete_layer_url = self.geoserver_http_address + "/rest/layers/python:" + layer_name
        curl_delete_layer_payload = {}
        curl_delete_layerg_headers = {
            'Authorization': self.basic_auth
        }
        curl_delete_layer_response = req.request("DELETE", curl_delete_layer_url,
                                                 headers=curl_delete_layerg_headers,
                                                 data=curl_delete_layer_payload)
        print(curl_delete_layer_response.text)

    # 删除GeoServer图层
    def delete_layer_service2(self, layer_name):
        cmd = "curl -v -u admin:geoserver -XDELETE {}/rest/layers/{}?recurse=true".format(self.geoserver_http_address,
                                                                                          layer_name)
        os.system(cmd)

    # 删除geoserver图层组服务
    def delete_layer_group_service(self, layer_group_name, workspacename):
        print("删除图层组服务{}".format(layer_group_name))
        if layer_group_name != None and layer_group_name.strip() != "":
            curl_delete_layergroup_url = self.geoserver_http_address + "/rest/layergroups/" + workspacename + ":" + layer_group_name
            curl_delete_layergroup_payload = {}
            curl_delete_layergroup_headers = {
                'Authorization': self.basic_auth
            }
            curl_delete_layergroup_response = req.request("DELETE", curl_delete_layergroup_url,
                                                          headers=curl_delete_layergroup_headers,
                                                          data=curl_delete_layergroup_payload)
            print(curl_delete_layergroup_response.text)

    # 动态生成geoserver样式
    def make_layer_style(self, style_color, workspacename):
        style_name = "temp_style_" + DateTimeHelper.get_uuid()
        print("创建新样式{}".format(style_name))
        url = self.geoserver_http_address + "/rest/workspaces/" + workspacename + "/styles?name=" + style_name
        payload = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><sld:StyledLayerDescriptor xmlns=\"http://www.opengis.net/sld\" xmlns:sld=\"http://www.opengis.net/sld\" xmlns:gml=\"http://www.opengis.net/gml\" xmlns:ogc=\"http://www.opengis.net/ogc\" version=\"1.0.0\">\r\n  <sld:NamedLayer>\r\n    <sld:Name>polygon fill</sld:Name>\r\n    <sld:UserStyle>\r\n      <sld:Name>polygon fill</sld:Name>\r\n      <sld:Title>polygon fill</sld:Title>\r\n      <sld:Abstract>polygon fill</sld:Abstract>\r\n      <sld:FeatureTypeStyle>\r\n        <sld:Name>polygon fill</sld:Name>\r\n        <sld:Rule>\r\n          <sld:PolygonSymbolizer>\r\n            <sld:Fill>\r\n              <sld:CssParameter name=\"fill\">#66FF66</sld:CssParameter>\r\n              <sld:CssParameter name=\"fill-opacity\">0</sld:CssParameter>\r\n            </sld:Fill>\r\n            <sld:Stroke>\r\n              <sld:CssParameter name=\"stroke\">" + style_color + "</sld:CssParameter>\r\n            </sld:Stroke>\r\n          </sld:PolygonSymbolizer>\r\n        </sld:Rule>\r\n      </sld:FeatureTypeStyle>\r\n    </sld:UserStyle>\r\n  </sld:NamedLayer>\r\n</sld:StyledLayerDescriptor>\r\n"
        headers = {
            'accept': 'application/json',
            'content-type': 'application/vnd.ogc.sld+xml',
            'Authorization': self.basic_auth
        }
        response = req.request("POST", url, headers=headers, data=payload)
        print(response.text)
        return style_name

    # 删除geoerver样式
    def delete_layer_style(self, style_name, workspacename):
        print("删除样式{}".format(style_name))
        if style_name != None and style_name.strip() != "":
            url = self.geoserver_http_address + "/rest/styles/" + workspacename + ":" + style_name
            payload = {}
            headers = {
                'Authorization': self.basic_auth
            }
            response = req.request("DELETE", url, headers=headers, data=payload)
            print(response.text)

    # 给图层设置样式
    def set_style_to_layer(self, layer_name, style_name):
        print("为图层{}设置样式{}".format(layer_name, style_name))
        url = self.geoserver_http_address + "/rest/layers/" + layer_name
        payload = "<layer>\r\n    <defaultStyle>\r\n        <name>" + style_name + "</name>\r\n    </defaultStyle>\r\n    <enabled>true</enabled>\r\n</layer>"
        headers = {
            'Content-type': 'text/xml',
            'Authorization': self.basic_auth
        }
        response = req.request("PUT", url, headers=headers, data=payload)
        print(response.text)

    # 给图层设置样式
    def set_style_to_layer2(self, workspace_name, layer_name, style_name):
        cmd = 'curl -v -u {} -X PUT {}/rest/workspaces/{}/layers/{} -H "accept: application/json" -H "content-type: application/xml"  -d "<layer><defaultStyle><name>{}</name></defaultStyle></layer>"'.format(
            self.serect, workspace_name, layer_name, style_name)
        print(cmd)
        os.system(cmd)

    # 获取gwc切片方案信息
    def get_grid_set_info(self, grid_set_name):
        url = "{}/gwc/rest/gridsets/{}".format(self.geoserver_http_address, grid_set_name)
        payload = {}
        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'Authorization': self.basic_auth
        }
        response = req.request("GET", url, headers=headers, data=payload)
        print(response.text)
        return response.text
