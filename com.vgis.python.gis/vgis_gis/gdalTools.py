import json
import subprocess


class GdalHelper:

    def __init__(self):
        pass


    def get_projection_by_gdalinfo(self,tif_path):
        # 执行cmd命令
        cmd = "gdalinfo -json {}".format(tif_path)
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")

        # 获取标准输出和错误信息
        stdout = result.stdout
        stderr = result.stderr

        # 打印输出结果
        # print(stdout)

        # 如果有错误信息，也打印它们
        if stderr:
            print("错误信息：" + stderr)
        info_dict = json.loads(stdout)
        proj_wkt = info_dict['coordinateSystem']['wkt']
        # 如果调用gdalinfo命令报错，
        # windows环境,在这里单元测试通过staticmethod方法会报这些错，但是普通方法不报错，如果打包好vgis-rs,在别的地方调用没问题
        # linux环境，不会出现这些问题
        # ERROR 1: PROJ: proj_create_from_database: C:\Program Files\gdal\bin\proj6\share\proj.db lacks DATABASE.LAYOUT.VERSION.MAJOR / DATABASE.LAYOUT.VERSION.MINOR metadata. It comes from another PROJ installation.
        # ERROR 1: PROJ: proj_create_from_database: C:\Program Files\gdal\bin\proj6\share\proj.db lacks DATABASE.LAYOUT.VERSION.MAJOR / DATABASE.LAYOUT.VERSION.MINOR metadata. It comes from another PROJ installation.
        # ERROR 1: PROJ: proj_get_ellipsoid: CRS has no geodetic CRS
        # ERROR 1: PROJ: proj_get_ellipsoid: Object is not a CRS or GeodeticReferenceFrame
        # 这个时候得到的projection是不完整的，开头：ENGCRS["WGS_1984_Web_Mercator_Auxiliary_Sphere",
        print(proj_wkt)
        return proj_wkt


    # 通过gdalsrsinfo命令获取完整的epsg
    def get_epsg_of_geo_file(self,geo_file_path):
        # 执行cmd命令
        cmd = "gdalsrsinfo {} -o epsg".format(geo_file_path)
        print(cmd)
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                encoding="utf-8")

        # 获取标准输出和错误信息
        stdout = result.stdout
        stderr = result.stderr

        # 打印输出结果
        # print(stdout)

        # 如果有错误信息，也打印它们
        if stderr:
            print("错误信息：" + stderr)
        epsg = stdout.replace("\n", "").lstrip("EPSG:").lstrip("epsg:")

        print(epsg)
        return epsg