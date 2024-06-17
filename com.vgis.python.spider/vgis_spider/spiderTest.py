#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    : 2021/2/1 10:28
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : spiderTest.py
# @Desc    ：抓取程序测试帮助类
# @Software: PyCharm

import binascii


class TestHelper:
    # 初始化
    def __init__(self):
        pass

    # 构建识别网址命令
    def build_parse_website_command(self, web_site, excel_path):
        web_site = str(binascii.b2a_hex(web_site.encode())).lstrip("b'").rstrip("'")
        command_str = "python parseWebsiteData.py -w {} -d {}".format(web_site, excel_path)
        return command_str

    # 构建抓取网址命令
    def build_crawler_website_command(self, web_site, field_name_str, field_path_str, is_turn_page, turn_page_num,
                                      excel_path):
        web_site = str(binascii.b2a_hex(web_site.encode())).lstrip("b'").rstrip("'")
        field_path_str = str(binascii.b2a_hex(field_path_str.encode())).lstrip("b'").rstrip("'")
        command_str = "python crawlerWebsiteData.py -w {} -t {} -s {} -n {} -p {} -d {}".format(web_site,
                                                                                                str(is_turn_page),
                                                                                                str(turn_page_num),
                                                                                                field_name_str,
                                                                                                field_path_str,
                                                                                                excel_path)
        return command_str
