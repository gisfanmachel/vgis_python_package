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

import requests
import requests as req
from vgis_gis.shpTools import ShpFileOperator
# from vgis_rs.tifTools import TifFileOperator
from vgis_utils.vgis_datetime.datetimeTools import DateTimeHelper
from requests.auth import HTTPBasicAuth


class GeoserverOperatoer:

    # 初始化
    def __init__(self, geoserver_http_address, username, password):
        # "http://192.168.3.77:8085/geoserver"
        self.geoserver_http_address = geoserver_http_address
        self.username = username
        self.password = password
        self.serect = username + ":" + password
        self.basic_auth = "Basic " + str(base64.b64encode(self.serect.encode("utf-8")), "utf-8")

    def get_workspace(self):
        url = '{}/rest/workspaces'.format(self.geoserver_http_address)
        response = requests.get(url, auth=HTTPBasicAuth(self.username, self.password))
        return response.text

    # 创建工作空间
    def create_workspace(self, workspace_name):
        url = '{}/rest/workspaces'.format(self.geoserver_http_address)
        payload = {'name': workspace_name}
        response = requests.post(url, json=payload, auth=HTTPBasicAuth(self.username, self.password))
        return response.status_code == 201

    # 创建数据存储
    # 栅格存储
    # /workspaces/{workspaceName}/coveragestores/{coveragestoreName}/coverages
    # 矢量存储
    # /workspaces/{workspaceName}/datastores/{datastoreName}/featuretypes,
    # WMSStores 用于从其他 Web Map Service (WMS) 服务器获取数据并将其集成到 GeoServer 中
    # /workspaces/{workspaceName}/wmsstores/{wmsstoreName}/wmslayers
    # WMTSStores 用于从其他 Web Map Tile Service (WMTS) 服务器获取瓦片数据并将其集成到 GeoServer
    # /workspaces/{workspaceName}/wmtsstores/{wmststoreName}/wmtslayers
    def create_datastore(self, workspace_name, datastore_name, file_path):
        url = '{}/rest/workspaces/{workspace_name}/datastores'.format(self.geoserver_http_address)
        headers = {'Content-Type': 'application/zip'}
        files = {'file': open(file_path, 'rb')}
        response = requests.post(url, auth=HTTPBasicAuth(self.username, self.password), headers=headers, files=files)
        return response.status_code == 201

    #


    # 删除栅格存储
    def delete_coveragestore(self, workspace_name, store_name):
        # 删除栅格存储
        # curl -v -u admin:geoserver -X DELETE http://127.0.0.1:8080/geoserver/rest/workspaces/jimu/coveragestores/uuuu?recurse=true
        cmd = "curl -v -u {} -X DELETE {}/rest/workspaces/{}/coveragestores/{}?recurse=true".format(self.serect,
                                                                                                    self.geoserver_http_address,
                                                                                                    workspace_name,
                                                                                                    store_name)
        print(cmd)
        os.system(cmd)

    # 删除栅格存储
    def delete_datastore(self, workspace_name, store_name):
        # 删除矢量存储
        # curl -v -u admin:geoserver -X DELETE http://127.0.0.1:8080/geoserver/rest/workspaces/jimu/datastores/tttt?recurse=true
        cmd = "curl -v -u {} -X DELETE {}/rest/workspaces/{}/datastores/{}?recurse=true".format(self.serect,
                                                                                                    self.geoserver_http_address,
                                                                                                    workspace_name,
                                                                                                    store_name)
        print(cmd)
        os.system(cmd)

    # 清除服务缓存
    def clear_geoserver_cache(self):
        cmd = 'curl -v -u {} -X POST {}/rest/reset -H  "accept: application/json" -H  "content-type: application/json"'.format(
            self.serect, self.geoserver_http_address)
        print(cmd)
        os.system(cmd)

    # 发布geoserver tif 图层服务-WMS
    def publish_raster_layer_service(self, tif_path, workspacename, layer_name):
        print("发布栅格图层服务{}".format(layer_name))
        url = self.geoserver_http_address + "/rest/workspaces/" + workspacename + "/coveragestores/" + layer_name + "/file.geotiff"
        # Authorization信息在postman测试用例里看
        headers = {
            'Content-type': 'image/tiff',
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

        payload = "<coverage>   \r\n    <parameters>\r\n    <entry>\r\n      <string>InputTransparentColor</string>\r\n      <string>#000000</string>\r\n    </entry>\r\n  </parameters>\r\n</coverage>\r\n"
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

    # 发布geoserver shp 图层服务--WMS
    # TODO:有问题，针对部分shp不能自动识别空间范围和srs
    def publish_shp_layer_service(self, shp_path, layer_name, workspacename, layer_style_color):
        print("发布矢量图层服务{}".format(layer_name))
        url = self.geoserver_http_address + "/rest/workspaces/" + workspacename + "/datastores/" + layer_name + "/file.shp"
        file = open(shp_path, 'rb')
        payload = file.read()
        headers = {
            'Content-type': 'application/zip',
            'Authorization': self.basic_auth
        }
        response = req.request("PUT", url, headers=headers, data=payload)
        print(response.text)

    def publish_shp_layer_service_v2(self, shp_path, layer_name, workspacename):
        print("发布矢量图层服务{}".format(layer_name))
        # windowsw文件路径
        # file://C:\data\test\jiujiang2018_landuse_newcode.shp
        # linux文件路径
        # file:///data/shapefiles/rivers/rivers.shp
        cmd = 'curl -v -u {}:{} -XPUT -H "Content-type: text/plain"   -d "file://{}"   {}/rest/workspaces/{}/datastores/{}/external.shp'.format(
            self.username, self.password, shp_path, self.geoserver_http_address, workspacename, layer_name)
        print(cmd)
        os.system(cmd)

    # 设置矢量图层的空间范围和坐标
    # 针对发布图层没有自动识别的情况
    def set_layer_coord_and_srs(self, layer_name, workspacename, minx, maxx, miny, maxy, epsg):
        cmd = ' curl -v -u {}:{} -XPUT -H "Content-type:text/xml" -d "<layer><bounds><minx>{}</minx><maxx>{}</maxx><miny>{}</miny><maxy>{}</maxy><crs>ESPG:{}</crs></bounds></layer>" {}/rest/layers/{}:{}'.format(
            self.username, self.password,
            minx, maxx, miny, maxy, epsg, self.geoserver_http_address, workspacename, layer_name)
        print(cmd)
        os.system(cmd)

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

    def get_layer_full_info(self, layer_name):
        # curl -X GET http://localhost:12686/geoserver/rest/layers/jimu:ningbo_airplane_label_google -H  "accept: application/xml" -H  "content-type: application/xml"
        url = self.geoserver_http_address + "/rest/layers/" + layer_name
        payload = {}
        headers = {
            'Authorization': self.basic_auth
        }
        response = req.request("GET", url, headers=headers, data=payload)
        print(response.text)

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
        curl_delete_layer_url = self.geoserver_http_address + "/rest/layers/" + layer_name
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
        cmd = "curl -v -u {}:{} -XDELETE {}/rest/layers/{}?recurse=true".format(self.username, self.password,
                                                                                self.geoserver_http_address,
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

    # 设置MVT为输出格式
    def set_mvt_format(self, workspace_name, layer_name):

        print("为图层{}设置MVTT输出{}".format(layer_name))
        # url = '{}/rest/workspaces/{}/layers/{}'.format(self.geoserver_http_address, workspace_name, layer_name)
        url = self.geoserver_http_address + "/rest/layers/" + workspace_name + ":" + layer_name
        payload = "<layer><tileCaching><cacheType>ALL</cacheType><gridSubdivision>0</gridSubdivision><formats><format>image/png</format><format>application/vnd.mapbox-vector-tile</format></formats></tileCaching></layer>"
        headers = {
            'Content-type': 'text/xml',
            'Authorization': self.basic_auth
        }
        response = req.request("PUT", url, headers=headers, data=payload)
        print(response.text)
        return response.status_code == 201

    # 开始切片
    def run_seed_tiles(self, workspacename, layername, bbox, srs):
        import requests

        # GeoWebCache REST API的URL
        gwc_url = '{}/gwc/rest/layer'.format(self.geoserver_http_address)

        # 需要切片的图层名称，格式为'工作区:图层名'
        layer_name = '{}:{}'.format(workspacename, layername)

        # 创建会话
        session = requests.Session()
        session.auth = (self.username, self.password)

        # 开始切片的请求
        seed_request = {
            "seed": {
                "recurse": True,
                # "bbox": "-180,-90,180,90",  # 切片的边界框，根据需要修改
                # "srs": "EPSG:4326"  # 坐标系统，根据需要修改
                "bbox": bbox,
                "srs": srs
            }
        }

        # 发送切片请求
        response = session.post(f'{gwc_url}/{layer_name}/seed', json=seed_request)

        # 检查响应
        if response.status_code == 200:
            print("切片请求已提交。")
        else:
            print("切片请求失败。", response.text)

        # 关闭会话
        session.close()


if __name__ == '__main__':
    geoserverOperatoer = GeoserverOperatoer('http://localhost:8080/geoserver', 'admin', 'geoserver')
    workspace = "jimu"

    # 发布栅格图层
    # tif_path = "c:/data/TW2015_4326.tif"
    # layer = os.path.split(tif_path)[1].split(".")[0]
    # geoserverOperatoer.publish_raster_layer_service(tif_path, workspace, layer)
    # geoserverOperatoer.clear_black_raster_layer_service(workspace, layer, layer)
    # epsg=TifFileOperator.get_epsg_of_tif(tif_path)
    # raster_tiles_url = "http://{}/gwc/service/wmts?layer={}:{}&style=&tilematrixset=EPSG:{}&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image:vnd.jpeg-png&TileMatrix=EPSG:{}:{z}&TileCol={x}&TileRow={y}".format(geoserverOperatoer.geoserver_http_address,workspace, layer, epsg, epsg)

    # 发布矢量图层
    shp_path = "c:/data/test/ningbo_airplane_label_google.shp"
    layer = os.path.split(shp_path)[1].split(".")[0]
    left, right, down, up = ShpFileOperator.get_layer_envlope(shp_path)
    import os

    os.environ[
        'PROJ_LIB'] = "C:\\Users\\63241\\miniconda3\\envs\\django422_py310\\Lib\\site-packages\\pyproj\\proj_dir\\share\\proj"
    from vgis_gis.shpTools import ShpFileOperator

    epsg = ShpFileOperator.get_epsg_of_shp_v2(shp_path)
    geoserverOperatoer.publish_shp_layer_service_v2(shp_path, layer, workspace)
    geoserverOperatoer.set_layer_coord_and_srs(layer, workspace, left, right, down, up, epsg)

    geojson_vector_tiles_url = "http://{}/gwc/service/wmts?REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&LAYER={}:{}&STYLE=&TILEMATRIX=EPSG:{}:{z}&TILEMATRIXSET=EPSG:{}&FORMAT=application/json;type=geojson&TILECOL={x}&TILEROW={y}".format(
        geoserverOperatoer.geoserver_http_address, workspace, layer, epsg, epsg)
    mvt_vector_tiles_url = "http://{}/gwc/service/wmts?REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&LAYER={}:{}&STYLE=&TILEMATRIX=EPSG:{}:{z}&TILEMATRIXSET=EPSG:{}&FORMAT=application/vnd.mapbox-vector-tile&TILECOL={x}&TILEROW={y}".format(
        geoserverOperatoer.geoserver_http_address, workspace, layer, epsg, epsg)

# WMTS服务查看页面
# http://localhost:12686/geoserver/gwc/demo/jimu:tw2015?gridSet=EPSG:4326&format=image/vnd.jpeg-png
# http://localhost:8080/geoserver/gwc/demo/jimu:ningbo_airplane_label_google?gridSet=EPSG:4326&format=application/vnd.mapbox-vector-tile

# WMTS瓦片URL
# jpeg-png 栅格瓦片
# http://{ip}:{port}/geoserver/gwc/service/wmts?layer={workspacename}:{layername}&style=&tilematrixset=EPSG:{epsg}&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image:vnd.jpeg-png&TileMatrix=EPSG:{epsg}:{z}&TileCol={x}&TileRow={y}
# geojson 矢量瓦片
# http://{ip}:{port}/geoserver/gwc/service/wmts?REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&LAYER={workspacename}:{layername}&STYLE=&TILEMATRIX=EPSG:{epsg}:{z}&TILEMATRIXSET=EPSG:{epsg}&FORMAT=application/json;type=geojson&TILECOL={x}&TILEROW={y}
# topojson 矢量瓦片
# http://{ip}:{port}/geoserver/gwc/service/wmts?REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&LAYER={workspacename}:{layername}&STYLE=&TILEMATRIX=EPSG:{epsg}:{z}&TILEMATRIXSET=EPSG:{epsg}&FORMAT=application/json;type=topojson&TILECOL={x}&TILEROW={y}
# utfgrid 矢量瓦片
# http://{ip}:{port}/geoserver/gwc/service/wmts?REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&LAYER={workspacename}:{layername}&STYLE=&TILEMATRIX=EPSG:{epsg}:{z}&TILEMATRIXSET=EPSG:{epsg}&FORMAT=application/json;type=utfgrid&TILECOL={x}&TILEROW={y}
# mvt矢量瓦片
# http://{ip}:{port}/geoserver/gwc/service/wmts?REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&LAYER={workspacename}:{layername}&STYLE=&TILEMATRIX=EPSG:{epsg}:{z}&TILEMATRIXSET=EPSG:{epsg}&FORMAT=application/vnd.mapbox-vector-tile&TILECOL={x}&TILEROW={y}

# wms瓦片
#  mvt瓦片 矢量瓦片
# http://{ip}:{port}/geoserver/{worksapcename}/wms?service=WMTS&request=GetTile&version=1.0.0&layer={layername}&style=&tilematrixset=EPSG:{epsg}&format=application/vnd.mapbox-vector-tile&tilematrix=EPSG:{epsg}:{z}&tilerow={y}&tilecol={x}
