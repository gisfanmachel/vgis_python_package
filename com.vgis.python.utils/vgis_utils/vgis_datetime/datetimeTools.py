"""
===================================
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Author: chenxw
@Email : gisfanmachel@gmail.com
@File: datetimeTools.py
@Date: Create in 2021/1/25 16:36
@Description: 
@ Software: PyCharm
===================================
"""
import datetime
import re
import time
from datetime import timedelta

# 需要引用最顶层的


class DateTimeHelper:
    def __init__(self):
        pass

    @staticmethod
    # 解析自然语言时间字符串为标准时间（YYYY-MM-DD HH:MM:SS）
    # 如39秒前
    # 1分钟前
    # 今天09:45
    # 01月24日 12:39-->2023--1-24 12:39:00
    # 2020年12月22日 20:31 -->2020-12-22 20:31:00
    # 2023-08-31T00:00:00 -->2023-08-0-31 00:00:00
    # 2023/7/31T17:55 --> 2023-07-31 17:55:00
    # 2023/7/31T17:55:23 -->2023-07-31 17:55:23
    # 2023-8-6 17:33:00 -->2023-08-06 17:33:00
    def get_standTime_By_Str(time_str):
        info_time = time_str
        current_year = str(datetime.datetime.now().year)
        current_month = str(datetime.datetime.now().month)
        current_day = str(datetime.datetime.now().day)
        current_hour = str(datetime.datetime.now().hour)
        current_minute = str(datetime.datetime.now().minute)
        current_second = str(datetime.datetime.now().second)
        info_time = info_time.strip()
        # 39秒前
        if "秒" in info_time:
            second_num = int(re.findall("\d+", info_time)[0])
            info_time = (datetime.datetime.now() - datetime.timedelta(seconds=second_num)).strftime("%Y-%m-%d %H:%M:%S")
        # 1分钟前
        if "分" in info_time:
            minute_num = int(re.findall("\d+", info_time)[0])
            info_time = (datetime.datetime.now() - datetime.timedelta(minutes=minute_num)).strftime("%Y-%m-%d %H:%M:%S")
        # 今天09:45
        if "今天" in info_time:
            info_time = info_time.replace("今天",
                                          current_year + "-" + current_month + "-" + current_day + " ")
            if info_time.count(":") == 1:
                info_time = info_time + ":00"
        # 01月24日 12:39
        if "年" not in info_time and "月" in info_time and "日" in info_time:
            info_time = current_year + "年" + info_time
            if info_time.count(":") == 1:
                info_time = info_time + ":00"
        # 2020年12月22日 20:31
        if "年" in info_time and "月" in info_time and "日" in info_time:
            if info_time.count(":") == 1:
                info_time = info_time + ":00"
        # 2023-08-31T00:00:00 -->2023-08-31 00:00:00
        if "T" in info_time:
            info_time = info_time.replace("T", " ")
        if "/" in info_time:
            info_time = info_time.replace("/", "-")
        if info_time.count(":") == 1:
            info_time = info_time + ":00"
        return info_time

    @staticmethod
    # 将秒数转换为*时*分*秒
    def convert_seconds(seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        result = "{}秒".format(int(s))
        if m > 0:
            result = "{}分".format(int(m)) + result
        if h > 0:
            result = "{}时".format(int(m)) + result
        # print("程序总共耗时%02d:%02d:%02d" % (h, m, s))
        return result

    @staticmethod
    # 将识别字符如2月23日转换为2023-02-27,年份默认用当年
    # 2022年12月22日，需要翻译成2022-12-22
    # 05-May-23 翻译 2023-05-27
    def convert_date(recog_str):
        need_date = None
        try:
            # 先验证是否是日期类型
            if DateTimeHelper.is_date_str(recog_str):
                need_date = recog_str
            else:
                # 2月23日,增加当前年
                if "年" not in recog_str and "月" in recog_str and "日" in recog_str:
                    ret = re.findall(r'\s*(\d{1,2})\s*[\./月-]\s*(\d{1,2})\s*日?', recog_str)
                    if ret:
                        month, day = ret[0]
                        year = datetime.datetime.today().year
                        need_date = str(year) + "-" + str(month) + "-" + str(day)
                # 2022年12月22日
                if "年" in recog_str and "月" in recog_str and "日" in recog_str:
                    ret = re.findall(r'(\d{4})\s*[\./年-]\s*(\d{1,2})\s*[\./月-]\s*(\d{1,2})\s*日?', recog_str)
                    if ret:
                        year, month, day = ret[0]
                        need_date = str(year) + "-" + str(month) + "-" + str(day)
                # 05-May-23
                if DateTimeHelper.is_has_en_month(recog_str):
                    month_str = re.sub("[\u4e00-\u9fa5\0-9\,\。]", "", recog_str)
                    month_num = DateTimeHelper.convert_month_from_en_to_num(month_str)
                    need_date_split = recog_str.split("-")
                    year = need_date_split[2]
                    if len(year) == 2:
                        year = "20" + year
                    need_date = year + "-" + month_num + "-" + need_date_split[0]

        except Exception as exp:
            print(exp)
            print(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            print(exp.__traceback__.tb_lineno)  # 发生异常所在的行数
        finally:
            # print(need_date)
            return need_date

    @staticmethod
    # 判断日期里是否含有英文月份
    def is_has_en_month(date_str):
        is_find = False
        month_list = "January,Jan,JAN,February,Feb,FEB,March,Mar,MAR,April,Apr,APR,May,MAY,June,JUNE,Jun,JUN,July,Jul,JUL,August,Aug,AUG,September,Sep,SEP,October,Oct,OCT,November,Nov,NOV,December,Dec,DEC".split(
            ",")
        month_str = re.sub("[\u4e00-\u9fa5\0-9\,\。]", "", date_str)
        if month_str in month_list:
            is_find = True
        return is_find

    @staticmethod
    # 将月份从字母转为数字
    def convert_month_from_en_to_num(month_en):
        month_abbr_list = [
            'JAN',
            'FEB',
            'MAR',
            'APR',
            'MAY',
            'JUN',
            'JUL',
            'AUG',
            'SEP',
            'OCT',
            'NOV',
            'DEC']
        month_index = month_abbr_list.index(month_en.upper())
        month_num = month_index + 1
        if len(str(month_num)) == 1:
            month_num = "0" + str(month_num)
        return str(month_num)

    @staticmethod
    # 从日期中提取年月日
    # 输入2023年12月22日、12月22日、2023-12-22
    # 输出2023、12、22
    def parse_date(date_str):
        date_year = None
        date_month = None
        date_day = None
        try:
            date_str = DateTimeHelper.convert_date(date_str)
            date_year = date_str.split("-")[0]
            date_month = date_str.split("-")[1]
            date_day = date_str.split("-")[2]
        except Exception as exp:
            pass
            # logger.error(exp)
            # logger.error(exp.__traceback__.tb_frame.f_globals["__file__"])  # 发生异常所在的文件
            # logger.error(exp.__traceback__.tb_lineno)  # 发生异常所在的行数
        finally:
            # print(need_date)
            return date_year, date_month, date_day

    @staticmethod
    # 从日期字符串转换为某年某月某日
    # 输入2023-12-22
    # 输出2023年12月22日
    def parse_date2(date_str):
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        date_str = date.strftime('%Y年%m月%d日')
        return date_str

    @staticmethod
    # 判断字符串是否为日期类型
    def is_date_str(date_text):
        is_date_type = True
        try:
            datetime.datetime.strptime(date_text, '%Y-%m-%d')
            is_date_type = True
        except ValueError:
            is_date_type = False
        if is_date_type is False:
            try:
                datetime.datetime.strptime(date_text, '%Y %m %d')
                is_date_type = True
            except ValueError:
                is_date_type = False
        # print(is_date_type)

        return is_date_type

    @staticmethod
    # 根据时间戳（到毫秒）获取uuid
    def get_uuid():
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

    @staticmethod
    # 时间字符串转换为时间对象
    def string2time_stamp(str_value):

        try:
            d = datetime.datetime.strptime(str_value, "%Y-%m-%d %H:%M:%S.%f")
            t = d.timetuple()
            time_stamp = int(time.mktime(t))
            time_stamp = float(str(time_stamp) + str("%06d" % d.microsecond)) / 1000000
            return time_stamp
        except ValueError as e:
            print(e)
            d = datetime.datetime.strptime(str_value, "%Y-%m-%d %H:%M:%S")
            t = d.timetuple()
            time_stamp = int(time.mktime(t))
            time_stamp = float(str(time_stamp) + str("%06d" % d.microsecond)) / 1000000
            return time_stamp

    @staticmethod
    # 实践中字符串是否符合对应格式(YYYY-MM-DD HH:MM:SS)
    def check_time_format(time_str):
        pattern = re.compile(r'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}')
        if re.match(pattern, time_str):
            return True
        else:
            return False

    @staticmethod
    # 获取两个时间之间的相差天数
    # 时间格式为 "%Y-%m-%d %H:%M:%S"
    def compute_days_between_two_datetime(datetime_str1, datetime_str2):
        start_datetime = datetime.datetime.strptime(
            datetime_str1, "%Y-%m-%d %H:%M:%S")
        end_datetime = datetime.datetime.strptime(
            datetime_str2, "%Y-%m-%d %H:%M:%S")
        delta = abs(end_datetime - start_datetime)
        delta_days = delta.days
        return delta_days

    @staticmethod
    # 获取两个日期之间的相差天数
    # 日期格式为 "%Y-%m-%d"
    def compute_days_between_two_date(date_str1, date_str2):

        start_date = datetime.datetime.strptime(
            date_str1, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(
            date_str2, "%Y-%m-%d")
        delta = abs(end_date - start_date)
        delta_days = delta.days
        return delta_days

    @staticmethod
    # 获取指定日期的前后几天的日期
    # delta_days 负数 为前几天
    # delta_days 正数 为后几天
    # 日期格式为 "%Y-%m-%d"
    def get_date_of_delta_days(date_str1, delta_days):
        base_date = datetime.datetime.strptime(
            date_str1, "%Y-%m-%d")
        need_date = base_date + timedelta(days=delta_days)
        return need_date.strftime("%Y-%m-%d")

    @staticmethod
    # 将时间字符串补齐6位
    def get_compelete_time_six_position(time_str: str) -> str:
        """
        将时间字符串补齐6位

        :param time_str: 输入的时间字符串,格式为 2021,2021-11,2021-05-16
        :return: 补齐6位的时间字符串，格式为 2021000,20211100,20210516
        """
        get_time_str = time_str
        if len(time_str.split("-")) == 3:
            get_time_str = time_str.replace("-", "")
        if len(time_str.split("-")) == 2:
            get_time_str = time_str.replace("-", "") + "00"
        if len(time_str.split("-")) == 1:
            get_time_str = time_str.replace("-", "") + "0000"
        return get_time_str

    @staticmethod
    # 将标准时间戳转换为时间字符串
    # time_stamp=1708099200000
    # time_str = "2024-02-17 00:00:00"
    # 时间戳是指格林威治时间1970年01月01日00时00分00秒(北京时间1970年01月01日08时00分00秒)起至现在的总秒数
    def convert_time_stamp_to_time_str(timestamp):
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time

    @staticmethod
    # 将时间字符串转换为标准时间戳
    # time_str = "2024-02-17 00:00:00"
    # time_stamp=1708099200000
    # 时间戳是指格林威治时间1970年01月01日00时00分00秒(北京时间1970年01月01日08时00分00秒)起至现在的总秒数
    def convert_time_str_to_time_stamp(time_str):
        # 将时间字符串转换为时间元组
        time_tuple = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        # 将时间元组转换为时间戳（单位为秒）
        timestamp = int(time.mktime(time_tuple))
        return timestamp


if __name__ == '__main__':
    print(DateTimeHelper.compute_days_between_two_date("2023-12-1", "2023-12-6"))
    print(DateTimeHelper.compute_days_between_two_datetime("2023-12-1 0:0:0", "2023-12-6 15:34:36"))
    print(DateTimeHelper.get_date_of_delta_days("2023-12-1", 5))
    print(DateTimeHelper.get_date_of_delta_days("2023-12-1", -5))
    print(DateTimeHelper.parse_date("2023-12-1")[0])
    print(DateTimeHelper.parse_date2("2023-12-1"))
