"""
===================================
@Author: Yanmh
@date: Create in 2020/12/6 10:06
@description:
    sklearn2 聚类分析工具类, 包含PCA主成分算法、DBSCAN密度算法、KMeansK均值算法，MeanShift密度聚类，均值漂移聚类，linkage聚类或连接聚类，mixture高斯混合聚类
    init: in_path - 输入excel文件； out_path - 输出excel文件
    SK_PCA: fileds - 分析的字段名称
    SK_DBSCAN: fields - 分析的字段名称, eps - 半径; min_samples - 最小样本量
    SK_MEANSHIFT: fields - 分析的字段名称, bandwidth - 带宽
    SK_MIXTURE: fields - 分析的字段名称, n_components - 组件数
    KS_LINKAGE： fields - 分析的字段名称, max_d - 最大的连接距离
===================================
"""
print(__doc__)
import sys
import traceback

import pandas as pd
from scipy.cluster.hierarchy import fcluster
from scipy.cluster.hierarchy import linkage
from sklearn import mixture
from sklearn.cluster import DBSCAN
from sklearn.cluster import KMeans
from sklearn.cluster import MeanShift
from sklearn.decomposition import PCA
from vgis_log.logTools import Log


# 自定义聚类算法函数
class SklearnTool:

    def __init__(_self, in_path, out_path):
        '''初始化聚类算法'''
        print("初始化线性回归聚类算法")
        try:
            _self._log_path = out_path  # 日志文件
            _self._out_path = out_path  # 输出文件地址
            _self._data = pd.read_excel(in_path, na_values=0).fillna(0)
        except Exception:
            log_error = "读取{}文件出错了: {}".format(in_path, traceback.format_exc())
            print(log_error)
            log = Log(_self._log_path, log_error)  # 生成日志
            log.make_log_file()
            sys.exit(2)

    def SK_PCA(_self, fields):
        '''执行聚类主成分分析算法'''
        print("PCA - 主成分分析")
        try:
            X = _self._data[fields.split(",")]
            # n_components表示保留的特征数默认为1。如果设置成‘mle’,那么会自动确定保留的特征数
            pca = PCA(n_components='mle').fit(X)
            _self._w_data = pd.DataFrame(pca.fit_transform(X))
            _self._ratio = pca.explained_variance_ratio_  # 方差
        except Exception:
            log_error = "SK_DBSCAN分析出错了: {}".format(traceback.format_exc())
            print(log_error)
            log = Log(_self._log_path, log_error)  # 生成日志
            log.make_log_file()
            sys.exit(2)

    def SK_DBSCAN(_self, fields, eps, min_samples):
        '''执行聚类密度算法'''
        print("DBSCAN - 具有噪声的基于密度的聚类方法")
        try:
            X = _self._data[fields.split(",")]
            # 设置半径为 eps，最小样本量为 min_samples，建模
            db = DBSCAN(eps=float(eps), min_samples=float(min_samples)).fit(X)
            _self._w_data = _self._data
            _self._w_data['label'] = db.labels_  # 聚类簇结果

            _self._mean = _self._w_data.groupby('label').mean()  # k均值结果
        except Exception:
            log_error = "SK_DBSCAN分析出错了: {}".format(traceback.format_exc())
            print(log_error)
            log = Log(_self._log_path, log_error)  # 生成日志
            log.make_log_file()
            sys.exit(2)

    def SK_KMEANS(_self, fields, num):
        '''执行K均值聚类'''
        print("SK_KMEANS - K均值聚类方法")
        try:
            X = _self._data[fields.split(",")]
            db = KMeans(n_clusters=(int)(num)).fit(X)
            _self._w_data = _self._data
            _self._w_data['label'] = db.labels_  # 聚类簇结果
        except Exception:
            log_error = "SK_KMEANS分析出错了: {}".format(traceback.format_exc())
            print(log_error)
            log = Log(_self._log_path, log_error)  # 生成日志
            log.make_log_file()
            sys.exit(2)

    def SK_MEANSHIFT(_self, fields, bandwidth):
        '''执行密度聚类，均值漂移聚类'''
        print("SK_MEANSHIFT - 密度聚类，均值漂移聚类方法")
        try:
            X = _self._data[fields.split(",")]
            # 带宽
            db = MeanShift(bandwidth=float(bandwidth)).fit(X)
            _self._w_data = _self._data
            _self._w_data['label'] = db.labels_  # 聚类簇结果
        except Exception:
            log_error = "SK_KMEANS分析出错了: {}".format(traceback.format_exc())
            print(log_error)
            log = Log(_self._log_path, log_error)  # 生成日志
            log.make_log_file()
            sys.exit(2)

    def SK_MIXTURE(_self, fields, components):
        '''执行高斯混合聚类'''
        print("SK_MIXTURE - 高斯混合聚类方法")
        try:
            X = _self._data[fields.split(",")]
            gmm = mixture.GaussianMixture(n_components=int(components)).fit(X)
            pred_gmm = gmm.predict(X)
            _self._w_data = _self._data
            _self._w_data['label'] = pred_gmm  # 聚类簇结果
        except Exception:
            log_error = "SK_KMEANS分析出错了: {}".format(traceback.format_exc())
            print(log_error)
            log = Log(_self._log_path, log_error)  # 生成日志
            log.make_log_file()
            sys.exit(2)

    def KS_LINKAGE(_self, fields, max_d):
        '''层次聚类或连接聚类'''
        print("SK_LINKAGE - 层次聚类或连接聚类方法")
        try:
            X = _self._data[fields.split(",")]
            # 带宽
            ward = linkage(X, 'ward')  # 训练
            pred_h = fcluster(ward, max_d, criterion='distance')  # 预测属于哪个类
            _self._w_data = _self._data
            _self._w_data['label'] = pred_h  # 聚类簇结果
        except Exception:
            log_error = "SK_KMEANS分析出错了: {}".format(traceback.format_exc())
            print(log_error)
            log = Log(_self._log_path, log_error)  # 生成日志
            log.make_log_file()
            sys.exit(2)

    def SK_TO_EXCEL(_self):
        '''将结果转换成excel'''
        print("聚类分析结果导出到{}".format(_self._out_path))
        try:
            _self._w_data.to_excel(_self._out_path, encoding="utf-8", index=False)
        except Exception:
            log_error = "SK_TO_EXCEL导出结果excel出错了: {}".format(traceback.format_exc())
            print(log_error)
            log = Log(_self._log_path, log_error)  # 生成日志
            log.make_log_file()
            sys.exit(2)
