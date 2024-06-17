"""
=========================================================================================================
@Author: Yanmh
@date: Create in 2021/4/27 14:15
@description: 空间自相关函数， 实现两个相同影像tif之间的数据相关性计算
    y = ax + b

=========================================================================================================
"""
from vgis_code.codeGenerator import BuildCommand


print(__doc__)
# 定义tif文件地址  oneTif ; twoTif
#
# oneTiff = "E:\\遥感监测综合分析评估与辅助决策系统\\forFiles\\84\\GDP2004.TIF"
# twoTiff = "E:\\遥感监测综合分析评估与辅助决策系统\\forFiles\\84\\POP.TIF"
# outPath = "E:\\遥感监测综合分析评估与辅助决策系统\\forFiles\\84\\OUT.TIF"


from osgeo import gdal
import numpy as np
import pandas as pd
import getopt
import sys
from sklearn.metrics import r2_score
import json

# 第一个tiff文件
oneTiff = ""
# 第二个tiff文件
twoTiff = ""
# 输出文件地址
outPath = ""
# 输出文件地址
outPathGuiyi = ""
# 输出json文件地址
jsonPath = ""
# 输出csv文件地址
csvPath = ""
# 横坐标名称
xName = ""
# 纵坐标名称
yName = ""
# 构建并获取命令行的动态参数，赋值给全局变量
def build_command_params(argv):
    # 引用全局变量并赋值
    global oneTiff
    global twoTiff
    global outPath
    global outPathGuiyi
    global jsonPath
    global csvPath
    global xName
    global yName
    try:
        long_options = ["one_tif=", "two_tif=", "out_path=", "out_path_guiyi=", "json_path=", "csv_path=", "x_name=", "y_name="]
        opts, args = getopt.getopt(argv, "ho:w:p:g:j:c:x:y:", long_options)
    except getopt.GetoptError:
        print('命令行动态参数转换有问题,请按以下格式检查：acfPolyfit.py -o<one_tif> -w<two_tif> -p<out_path> -g<out_path_guiyi> -j<json_path> -c<csv_path> -x<x_name> -y<y_name>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('acfPolyfit.py -o<one_tif> -w<two_tif> -p<out_path>')
            print('one_tif: 第一个tiff文件,如\\one.tif')
            print('two_tif: 第二个tiff文件,如\\two.tif')
            print('out_path: 输出文件地址,如E:\\out.tif')
            print('out_path_guiyi: 输出文件归一化地址,如E:\\out_path_guiyi.tif')
            print('json_path: 输出文件json文件地址包含r2和函数,如E:\\json_path.json')
            print('csv_path: 输出文件csv地址,如E:\\csv_path.csv')
            print('x_name: 输出文件csv地址横坐标名称,如人口')
            print('y_name: 输出文件csv地址纵坐标名称,如建筑')
            print('调用命令样例(*****): python3 acfPolyfit.py -o \\one.tif -w \\two.tif -p E:\\out.tif -g E:\\out.tif')
            sys.exit()
        elif opt in ("-o", "--one_tif"):
            oneTiff = arg
        elif opt in ("-w", "--two_tif"):
            twoTiff = arg
        elif opt in ("-p", "--out_path"):
            outPath = arg
        elif opt in ("-g", "--out_path_guiyi"):
            outPathGuiyi = arg
        elif opt in ("-j", "--json_path"):
            jsonPath = arg
        elif opt in ("-c", "--csv_path"):
            csvPath = arg
        elif opt in ("-x", "--x_name"):
            xName = arg
        elif opt in ("-y", "--y_name"):
            yName = arg

    print('第一个tiff文件oneTiff为  {}'.format(oneTiff))
    print('第二个tiff文件twoTiff为  {}'.format(twoTiff))
    print('输出文件地址outPath为  {}'.format(outPath))
    print('输出文件地址归一化为  {}'.format(outPathGuiyi))
    print('输出文件json文件  {}'.format(jsonPath))
    print('输出文件Csv文件  {}'.format(csvPath))
    print('输出文件Csv文件横坐标  {}'.format(xName))
    print('输出文件Csv文件纵坐标  {}'.format(yName))


# 构建命令行参数
def make_build_command():
    args = {
        # py文件名称
        "py_file_name": "acfPolyfit.py",
        # 全局变量定义,用分号隔离
        "var_name_list": "oneTiff;twoTiff;outPath",
        # 全局变量注释，用分号隔离
        "var_anno_list": "第一个tiff文件;第二个tiff文件;输出文件地址",
        # 全局变量赋值，用分号隔离
        "var_value_list": "\\one.tif;\\two.tif;E:\\",
        # 长类型定义,用分号隔离
        "var_long_option_list": "one_tif;two_tif;out_path",
        # 短类型定义，用冒号隔离
        "var_short_opt_list": "o:w:p:"
    }
    code_builder = BuildCommand(args)
    code_builder.make_command_str()


# 读取tif文件
def read_tiff(filename):
    print('读取tif文件' + filename)
    dataset = gdal.Open(filename)
    if dataset == None:
        print("文件无法打开")
        return
    im_width = dataset.RasterXSize  # 栅格矩阵的列数
    im_height = dataset.RasterYSize  # 栅格矩阵的行数
    im_bands = dataset.RasterCount  # 波段数
    im_data = dataset.ReadAsArray(0, 0, im_width, im_height)  # 获取数据
    im_geotrans = dataset.GetGeoTransform()  # 获取仿射矩阵信息
    im_proj = dataset.GetProjection()  # 获取投影信息
    # im_blueBand = im_data[0, 0:im_height, 0:im_width]  # 获取蓝波段
    # im_greenBand = im_data[1, 0:im_height, 0:im_width]  # 获取绿波段
    # im_redBand = im_data[2, 0:im_height, 0:im_width]  # 获取红波段
    # im_nirBand = im_data[3, 0:im_height, 0:im_width]  # 获取近红外波段

    return {
        "im_width": im_width,
        "im_height": im_height,
        "im_bands": im_bands,
        "im_data": im_data,
        "im_geotrans": im_geotrans,
        "im_proj": im_proj,
    }


# 写tif
def write_tiff(im_data, im_width, im_height, im_bands, im_geotrans, im_proj, path):
    print(im_data.dtype.name)
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32

    if len(im_data.shape) == 3:
        im_bands, im_height, im_width = im_data.shape
    elif len(im_data.shape) == 2:
        im_data = np.array([im_data])
    else:
        im_bands, (im_height, im_width) = 1, im_data.shape
        # 创建文件
    driver = gdal.GetDriverByName("GTiff")
    dataset = driver.Create(path, im_width, im_height, im_bands, datatype)
    if (dataset != None):
        dataset.SetGeoTransform(im_geotrans)  # 写入仿射变换参数
        dataset.SetProjection(im_proj)  # 写入投影
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
    del dataset


# 自相关计算
def polyfit(one_data, two_data):
    z = np.polyfit(one_data, two_data, 1)
    p = np.poly1d(z)
    R_square = r2_score(two_data, p(one_data))
    print('R_square: {:.2f}'.format(R_square))
    return p, R_square


# 二维转一维
def toOneArr(im_data):
    arr = []
    for row_data in im_data:
        for col_data in row_data:
            if (col_data > -3.4):
                arr.append(col_data)
    return arr


# 代入计算
def compute(one_data, two_data, p):
    canchaarr = []
    guiyiarr = []
    arr = []
    arrguiyi = []
    zhengzuida = None
    fuzuida = None
    juzhen = []
    xMax =len(one_data)
    yMax = 0
    oneArr = []
    twoArr = []
    for i in range(len(one_data)):
        temp = []
        for j in range(len(one_data[i])):
            if (yMax< len(one_data[i])):
                yMax=len(one_data[i])
            col_data = one_data[i, j]
            col_dataY = two_data[i, j]
            if col_data > -3.4 and col_data!=0 and col_dataY > -3.4 and col_dataY!=0:
                oneArr.append(col_data)
                twoArr.append(col_data)
                # 方程式的值
                y = p(col_data)
                cancha = y - col_dataY
                canchaarr.append(cancha)
                if (zhengzuida == None and cancha >= 0):
                    zhengzuida = cancha
                if (fuzuida == None and cancha < 0):
                    fuzuida = abs(cancha)

                if (cancha > 0 and cancha > zhengzuida):
                    zhengzuida = cancha
                if (cancha < 0 and abs(cancha) > abs(fuzuida)):
                    fuzuida = abs(cancha)
                temp.append(cancha)
            else:
                temp.append(None)

        arr.append(temp)

    for i in range(len(one_data)):
        temp = []
        for j in range(len(one_data[i])):
            col_data = one_data[i, j]
            col_dataY = two_data[i, j]
            if col_data > -3.4 and col_data != 0 and col_dataY > -3.4 and col_dataY != 0:
                # 方程式的值
                y = p(col_data)
                cancha = y - col_dataY
                if (cancha == 0):
                    temp.append(0)
                    guiyiarr.append(0)
                    juzhen.append([i, j, 0])
                if (cancha > 0):
                    temp.append(cancha / zhengzuida)
                    guiyiarr.append(cancha / zhengzuida)
                    juzhen.append([i, j, (cancha / zhengzuida)])
                if (cancha < 0):
                    temp.append(cancha / fuzuida)
                    guiyiarr.append(cancha / fuzuida)
                    juzhen.append([i, j, (cancha / fuzuida)])

            else:
                temp.append(None)

        arrguiyi.append(temp)

    write_csv(oneArr, twoArr, canchaarr, guiyiarr)

    print(zhengzuida)
    print(fuzuida)
    # print(juzhen)

    return np.array(arr),  np.array(arrguiyi), juzhen, xMax, yMax


def write_csv(one_data, two_data, cancha, guiyi):
    arr = {str(xName): one_data, str(yName): two_data, 'cancha': cancha, 'guiyi': guiyi}
    table = pd.DataFrame(arr).to_csv(csvPath, header=True,
                             index=False, encoding="utf_8_sig")


def write_json(r2, fn, juzhen, xMax, yMax):
    dict_data = {}
    dict_data['r2'] = r2
    dict_data['fn'] = fn
    dict_data['juzhen'] = json.dumps(juzhen, ensure_ascii=False)
    dict_data['xMax'] = xMax
    dict_data['yMax'] = yMax
    # print(dict_data)
    with open(jsonPath, "w") as f:
        json.dump(dict_data, f)
        print("加载入文件完成...")


if __name__ == '__main__':
    # 读取tiff
    # make_build_command()
    build_command_params(sys.argv[1:])
    one_data = read_tiff(oneTiff)
    two_data = read_tiff(twoTiff)
    #  2维转1维
    one_arr = toOneArr(one_data["im_data"])
    two_arr = toOneArr(two_data["im_data"])
    #write_csv(one_arr, two_arr)
    # 得到函数
    p, R_square = polyfit(one_arr, two_arr)

    # 代入计算残差矩阵
    data, arrguiyi, juzhen, xMax, yMax = compute(one_data["im_data"], two_data["im_data"], p)

    write_json(R_square, str(p).replace("\n", "y = "), juzhen, xMax, yMax)
    # 写出tiff文件
    # im_data, im_width, im_height, im_bands, im_geotrans, im_proj, path
    write_tiff(data, one_data["im_width"], one_data["im_height"], one_data["im_bands"], one_data["im_geotrans"],
               one_data["im_proj"], outPath)
    write_tiff(arrguiyi, one_data["im_width"], one_data["im_height"], one_data["im_bands"], one_data["im_geotrans"],
               one_data["im_proj"], outPathGuiyi)
    print("end")
