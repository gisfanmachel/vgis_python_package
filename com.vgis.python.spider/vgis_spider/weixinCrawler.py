"""
===================================
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Author: chenxw
@Email : gisfanmachel@gmail.com
@File: weixinCrawler.py
@Date: Create in 2021/1/25 16:19
@Description: 对微信数据进行抓取
@ Software: PyCharm
===================================
"""

import re
import time
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class CrawerWeixinData:

    # 初始化
    def __init__(self, query_word=None, turn_page=None):
        self.query_word = query_word
        self.turn_page = turn_page

    # 获取微博综合查询结果数据
    # https://weixin.sogou.com/weixin?type=2&query=森林火灾&page=2
    def get_Sogou_Weixin_Query_Result(self):
        chrome_options = Options()  # 实例化Option对象
        chrome_options.add_argument('--headless')  # 把Chrome浏览器设置为静默模式
        chrome_options.add_argument('--disable-gpu')  # 禁止加载图片
        dr = webdriver.Chrome(options=chrome_options)  # 设置引擎为Chrome，在后台默默运行
        print("----------------------------------------------------------")
        is_not_last_page = True
        curent_page_num = 1
        crawler_data_list = []
        while is_not_last_page and curent_page_num <= self.turn_page:
            try:
                if curent_page_num == 1:
                    url = "https://weixin.sogou.com/weixin?type=2&query=" + self.query_word
                    print("目前是第1页------")
                    dr.get(url)
                else:
                    next_page_element = self.get_next_page_togger(dr)
                    dr.execute_script("arguments[0].click();", next_page_element)
                    sleep(1)
                    print("自动获取到第{}页-----".format(str(curent_page_num)))
                # print(dr.page_source)
                curent_page_num += 1
                print("获取微信搜索数据.........")
                htmlinfo = bytes(dr.page_source, encoding='utf-8')
                soup = BeautifulSoup(htmlinfo, 'html.parser')
                news_box = soup.find_all('div', attrs={'class': 'news-box'})
                if len(news_box) > 0:
                    li_item_list = news_box[0].find_all('ul', attrs={'class': 'news-list'})[0].find_all(name='li')
                    for li_item in li_item_list:
                        # 标题,提取简介里的 【】，若没有则提取前10个字符
                        try:
                            info_title = li_item.find_all('div', attrs={
                                'class': 'txt-box'})[0].text.replace("\n", "").strip()
                        except:
                            info_title = ""
                            pass
                        # 来源
                        try:
                            info_source = \
                                li_item.find_all('div', attrs={
                                    'class': 's-p'})[0].text.replace("\n", "").strip()
                        except:
                            info_source = ""
                            pass
                        # 时间
                        try:
                            info_time = \
                                li_item.find_all('span', attrs={
                                    'class': 's2'})[0].contents
                            info_time = re.findall("'(.*?)'", info_time)[0]
                            tupTime = time.localtime(int(info_time))
                            info_time = time.strftime("%Y-%m-%d %H:%M:%S", tupTime)
                        except:
                            info_time = ""
                            pass
                        # 简介
                        try:
                            info_breif = li_item.find_all('p', attrs={'class': 'txt-info'})[0].text.replace("\n", "").strip()
                        except:
                            info_breif = ""
                            pass
                        # 链接
                        try:
                            info_href = li_item.find_all('div', attrs={'class': 'txt-box'})[0].find_all(name='a')[0].attrs.get("href")
                            info_href="https://weixin.sogou.com"+info_href
                            # TODO:需要获取永久链接
                        except:
                            info_href = ""
                            pass
                        each_data_dict = {}
                        each_data_dict["标题"] = info_title
                        each_data_dict["来源"] = info_source
                        each_data_dict["时间"] = info_time
                        each_data_dict["简介"] = info_breif
                        each_data_dict["链接"] = info_href
                        crawler_data_list.append(each_data_dict)
            except Exception as exp:
                # 通过没有下一页的提示错误来分析，是否到了最后一页
                if "Cannot read property 'click' of null" in str(exp):
                    print("当前已到最后一页")
                else:
                    print("翻页错误：{}".format(exp))
                is_not_last_page = False
                pass
        dr.quit()
        return crawler_data_list
  # 获取微博综合查询结果数据
    # https://weixin.sogou.com/weixin?type=2&query=森林火灾&page=2
    def get_Sogou_Weixin_Query_Result_Json(self,now_time,taskId):
        chrome_options = Options()  # 实例化Option对象
        chrome_options.add_argument('--headless')  # 把Chrome浏览器设置为静默模式
        chrome_options.add_argument('--disable-gpu')  # 禁止加载图片
        dr = webdriver.Chrome(options=chrome_options)  # 设置引擎为Chrome，在后台默默运行
        print("----------------------------------------------------------")
        is_not_last_page = True
        curent_page_num = 1
        crawler_data_list = []
        crawler_data_list_json = []
        data = {}
        while is_not_last_page and curent_page_num <= self.turn_page:
            try:
                if curent_page_num == 1:
                    url = "https://weixin.sogou.com/weixin?type=2&query=" + self.query_word
                    print("目前是第1页------")
                    dr.get(url)
                else:
                    next_page_element = self.get_next_page_togger(dr)
                    dr.execute_script("arguments[0].click();", next_page_element)
                    sleep(1)
                    print("自动获取到第{}页-----".format(str(curent_page_num)))
                # print(dr.page_source)
                curent_page_num += 1
                print("获取微信搜索数据.........")
                htmlinfo = bytes(dr.page_source, encoding='utf-8')
                soup = BeautifulSoup(htmlinfo, 'html.parser')
                news_box = soup.find_all('div', attrs={'class': 'news-box'})
                if len(news_box) > 0:
                    li_item_list = news_box[0].find_all('ul', attrs={'class': 'news-list'})[0].find_all(name='li')
                    for li_item in li_item_list:
                        # 标题,提取简介里的 【】，若没有则提取前10个字符
                        try:
                            info_title = li_item.find_all('div', attrs={
                                'class': 'txt-box'})[0].text.replace("\n", "").strip()
                        except:
                            info_title = ""
                            pass
                        # 来源
                        try:
                            info_source = \
                                li_item.find_all('div', attrs={
                                    'class': 's-p'})[0].text.replace("\n", "").strip()
                        except:
                            info_source = ""
                            pass
                        # 时间
                        try:
                            info_time = \
                                li_item.find_all('span', attrs={
                                    'class': 's2'})[0].contents
                            info_time = re.findall("'(.*?)'", info_time)[0]
                            tupTime = time.localtime(int(info_time))
                            info_time = time.strftime("%Y-%m-%d %H:%M:%S", tupTime)
                        except:
                            info_time = ""
                            pass
                        # 简介
                        try:
                            info_breif = li_item.find_all('p', attrs={'class': 'txt-info'})[0].text.replace("\n", "").strip()
                        except:
                            info_breif = ""
                            pass
                        # 链接
                        try:
                            info_href = li_item.find_all('div', attrs={'class': 'txt-box'})[0].find_all(name='a')[0].attrs.get("href")
                            info_href="https://weixin.sogou.com"+info_href
                            # TODO:需要获取永久链接
                        except:
                            info_href = ""
                            pass
                        each_data_dict = {}
                        each_data_dict["标题"] = info_title
                        each_data_dict["来源"] = info_source
                        each_data_dict["时间"] = info_time
                        each_data_dict["简介"] = info_breif
                        each_data_dict["链接"] = info_href
                        crawler_data_list.append(each_data_dict)

                        each_data_dict_json = {}
                        each_data_dict_json["title"] = str(info_title)
                        each_data_dict_json["source"] = info_source
                        each_data_dict_json["time"] = info_time
                        each_data_dict_json["introduction"] = info_breif
                        each_data_dict_json["link"] = info_href
                        each_data_dict_json["createTm"] = now_time
                        each_data_dict_json["taskId"] = taskId
                        crawler_data_list_json.append(each_data_dict_json)

                    data["crawler_data_list_json"] = crawler_data_list_json
                    data["crawler_data_list"] = crawler_data_list
            except Exception as exp:
                # 通过没有下一页的提示错误来分析，是否到了最后一页
                if "Cannot read property 'click' of null" in str(exp):
                    print("当前已到最后一页")
                else:
                    print("翻页错误：{}".format(exp))
                is_not_last_page = False
                pass
        dr.quit()
        return data

    # 获取翻页的下一页的按钮,如果没有为None
    def get_next_page_togger(self, web_driver):
        next_page_dom_tag = ["a", "span"]
        next_page_text = ["下一页", "下页"]
        next_page_element = None
        is_not_find_next = True
        for tag in next_page_dom_tag:
            for txt in next_page_text:
                next_page_path = "//{}[contains(text(),'{}')]".format(tag, txt)
                try:
                    next_page_element = web_driver.find_element_by_xpath(next_page_path)
                    is_not_find_next = False
                    break
                except Exception as e:
                    pass
                continue
            if is_not_find_next == False:
                break
        return next_page_element
