import datetime
import os
import time

from vgis_utils.commonTools import CommonHelper
from vgis_utils.vgis_http.httpTools import HttpHelper


class Log:
    # 初始化
    def __init__(self, data_file_path, log_info):
        self.data_file_path = data_file_path
        self.log_info = log_info

    # 删除日志文件
    def del_log_file(self):
        log_file_path = self.get_log_file_path()
        if os.path.exists(log_file_path):
            os.remove(log_file_path)

    # 生成日志文件
    def make_log_file(self):
        # print("错误日志生成")
        log_file_path = self.get_log_file_path()
        if os.path.isfile(log_file_path):
            os.remove(log_file_path)
        print("生成日志文件{}".format(log_file_path))
        if not os.path.isfile(log_file_path):
            fd = open(log_file_path, mode="w", encoding="utf-8")
            fd.write(self.log_info)
            fd.close()

    # 获取日志文件
    def get_log_file_path(self):
        (file_pre_path, temp_filename) = os.path.split(self.data_file_path)
        (shot_name, file_ext) = os.path.splitext(temp_filename)
        log_file_path = file_pre_path + CommonHelper.get_dash_in_system() + shot_name + ".log2"
        return log_file_path

    # 生成空值文本文件
    def make_txt_file_null_value(self):
        (file_pre_path, temp_filename) = os.path.split(self.data_file_path)
        (shot_name, file_ext) = os.path.splitext(temp_filename)
        txt_file_path = file_pre_path + CommonHelper.get_dash_in_system() + shot_name + ".vgis_txt"
        if os.path.isfile(txt_file_path):
            os.remove(txt_file_path)
        print("生成空值txt文件{}".format(txt_file_path))
        if not os.path.isfile(txt_file_path):
            fd = open(txt_file_path, mode="w", encoding="utf-8")
            # fd.write(self.log_info)
            fd.close()


class LoggerHelper:
    def __init__(self):
        pass

    @staticmethod
    # 日志入库
    def insert_log_info(SysLog, username, operation, method, params=None, time=None, ip=None, error_info=None):
        create_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data = {}
        data["id"] = CommonHelper.snowflakeId()
        data["username"] = username
        data["operation"] = operation
        data["method"] = method
        data["params"] = params
        data["time"] = time
        data["ip"] = ip
        data["create_date"] = create_time
        data["error_info"] = error_info
        SysLog.objects.create(**data)

    @staticmethod
    def set_start_log_info(logger):
        start = time.perf_counter()
        logger.info("开始时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return start

    @staticmethod
    def set_end_log_info(SysLog, logger, start, api_path, user, request, function_title):
        logger.info("结束时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        end = time.perf_counter()
        t = end - start
        logger.info("总共用时{}秒".format(t))
        LoggerHelper.insert_log_info(SysLog, user, function_title + "成功",
                                     api_path,
                                     HttpHelper.get_params_request(request),
                                     t, HttpHelper.get_ip_request(request), None)

    @staticmethod
    def set_end_log_info_in_exception(SysLog, logger, start, api_path, user, request, function_title, error_info, exp,
                                      **kwargs):
        FAIL = "失败"
        CODE = "代码"
        LINE = "行数"

        if "localization" in kwargs:
            local = kwargs["localization"]
            if local == "EN":
                FAIL = " is fail"
                CODE = "code"
                LINE = "lines"

        if exp is not None:
            logger.error("{}失败：{}".format(function_title, str(exp)))
            logger.error(exp)
            logger.error(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            logger.error(exp.__traceback__.tb_lineno)  # 发生异常所在的行数
            error_info = str(exp) + "\n{}：".format(CODE) + str(
                exp.__traceback__.tb_frame.f_globals["__file__"]) + "\n{}：".format(LINE) + str(
                exp.__traceback__.tb_lineno)
            res = {
                "success": False,
                "info": "{}{}:{}".format(function_title, FAIL, exp)
            }
        else:
            logger.error("{}{}：{}".format(function_title, FAIL, error_info))
            res = {
                "success": False,
                "info": error_info
            }
        logger.info("结束时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        end = time.perf_counter()
        t = end - start
        logger.info("总共用时{}秒".format(t))
        # 日志入库
        LoggerHelper.insert_log_info(SysLog, user, function_title + "失败",
                                     api_path,
                                     HttpHelper.get_params_request(request),
                                     t, HttpHelper.get_ip_request(request), error_info)
        return res


# 主入口,进行测试
if __name__ == '__main__':
    logger = Log("D:\qcndata\paserdata.xlsx", "")
    logger.make_txt_file_null_value()
