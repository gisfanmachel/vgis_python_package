"""
===================================
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Author: chenxw
@Email : gisfanmachel@gmail.com
@File: weiboCrawler.py
@Date: Create in 2021/1/25 16:19
@Description: 对微博数据进行抓取
@ Software: PyCharm
===================================
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from time import sleep
from bs4 import BeautifulSoup
import re
from vgis_utils.vgis_datetime.datetimeTools import DateTimeHelper
from weiboSettings import Setting
import binascii


class CrawerWeiboData:

    # 初始化
    def __init__(self, query_word=None, turn_page=None):
        self.query_word = query_word
        self.turn_page = turn_page

    # 获取微博综合查询结果数据
    # https: // s.weibo.com / weibo?q = 森林火灾 & Refer = weibo_weibo & page = 2
    #  &xsort=hot  热门  &scope=ori 原创 &atten=1 关注人 &vip=1 认证用户 &category=4 媒体  &viewpoint=1观点
    # 时间范围： &timescope=custom:2021-01-04:2021-01-12
    #  含图片 &haspic=1  含视频 &hasvideo=1 含音乐 &hasmusic=1  含短链接 &haslink=1
    def get_Weibo_Compre_Query_Result(self):
        chrome_options = Options()  # 实例化Option对象
        chrome_options.add_argument('--headless')  # 把Chrome浏览器设置为静默模式
        chrome_options.add_argument('--disable-gpu')  # 禁止加载图片
        dr = webdriver.Chrome(options=chrome_options)  # 设置引擎为Chrome，在后台默默运行
        # 通过新浪邮箱登录，微博登录需要短信验证码
        URL = 'https://mail.sina.com.cn/?from=mail'
        dr.get(URL)
        sleep(1)
        # binascii.a2b_hex(auth_str).decode("utf-8")
        setting = Setting()
        auth_str = setting.get_AUTH_STR()
        decode_str = binascii.a2b_hex(auth_str).decode("utf-8")
        key_list = decode_str.split(setting.get_AUTH_SPLIT_STR())
        dr.find_element_by_xpath('//*[@id="freename"]').send_keys(key_list[0])
        dr.find_element_by_xpath('//*[@id="freepassword"]').send_keys(key_list[1])
        is_login_sina_email = True
        crawler_data_list = []
        try:
            # 自动获取登录按钮,还有问题
            # login_button_element = self.get_login_button_togger(dr)
            # dr.execute_script("arguments[0].click();", login_button_element)
            # 有广告的页面
            locator = '/html/body/div[3]/div/div[2]/div/div/div[4]/div[1]/div[1]/div[7]/div[1]/a[1]'
            if dr.find_element_by_xpath(locator) is not None:
                dr.find_element_by_xpath(locator).click()
            else:
                # 没有广告的页面
                locator = '/html/body/div[1]/div/div[2]/div/div/div[4]/div[1]/div[1]/div[7]/div[1]/a[1]'
                if dr.find_element_by_xpath(locator) is not None:
                    dr.find_element_by_xpath(locator).click()
        except:
            is_login_sina_email = False
            pass
        if is_login_sina_email:
            print("新浪邮箱登录成功，在后台浏览器打开新TAB页，进行微博免登录搜索，支持多页查询")
            # print(dr.current_url)
            # print(dr.page_source)
            print("----------------------------------------------------------")
            sleep(3)
            # 在浏览器打开 新tab，进行微博查询,利用新浪邮箱登录的身份，微博不用再登录
            dr.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
            is_not_last_page = True
            curent_page_num = 1
            while is_not_last_page and curent_page_num <= self.turn_page:
                try:
                    if curent_page_num == 1:
                        url = "https://s.weibo.com/weibo?q=" + self.query_word + "&Refer=weibo_weibo"
                        print("目前是第1页------")
                        dr.get(url)
                    else:
                        next_page_element = self.get_next_page_togger(dr)
                        dr.execute_script("arguments[0].click();", next_page_element)
                        sleep(1)
                        print("自动获取到第{}页-----".format(str(curent_page_num)))
                    # print(dr.page_source)
                    curent_page_num += 1
                    print("获取微博搜索数据.........")
                    htmlinfo = bytes(dr.page_source, encoding='utf-8')
                    soup = BeautifulSoup(htmlinfo, 'html.parser')
                    div_box = soup.find_all('div', attrs={'class': 'm-con-l'})
                    if len(div_box) > 0:
                        # card_item_list = div_box[0].find_all(name='div')[3].find_all('div',
                        #                                                              attrs={'class': 'card-wrap'})
                        card_item_list = div_box[0].find_all('div', attrs={'class': 'card-wrap'})
                        for card_item in card_item_list:
                            # 标题,提取简介里的 【】，若没有则提取前10个字符
                            try:
                                info_title_old = card_item.find_all('p', attrs={'class': 'txt'})[0].text.replace(
                                    "\n", "").strip()
                                info_title = re.findall("【(.*?)】", info_title_old)
                                if len(info_title) == 0:
                                    info_title = info_title_old[0:20]
                            except:
                                info_title = ""
                                pass
                            # 来源
                            try:
                                info_source = \
                                    card_item.find_all('div', attrs={'class': 'info'})[0].find_all(name='div')[
                                        1].text.replace("\n", "")
                            except:
                                info_source = ""
                                pass
                            # 时间
                            try:
                                info_time = \
                                    card_item.find_all('p', attrs={'class': 'from'})[0].text.replace("\n",
                                                                                                     "").strip().split(
                                        "\xa0")[0]
                                info_time = DateTimeHelper.get_standTime_By_Str(info_time)
                            except:
                                info_time = ""
                                pass
                            # 简介
                            try:
                                info_breif = card_item.find_all('p', attrs={'class': 'txt'})[0].text.replace("\n",
                                                                                                             "").strip()
                            except:
                                info_breif = ""
                                pass
                            # 链接
                            try:
                                info_href = "https:" + \
                                            card_item.find_all('p', attrs={'class': 'from'})[0].find_all(name='a')[
                                                0].attrs.get("href")
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
    # https: // s.weibo.com / weibo?q = 森林火灾 & Refer = weibo_weibo & page = 2
    #  &xsort=hot  热门  &scope=ori 原创 &atten=1 关注人 &vip=1 认证用户 &category=4 媒体  &viewpoint=1观点
    # 时间范围： &timescope=custom:2021-01-04:2021-01-12
    #  含图片 &haspic=1  含视频 &hasvideo=1 含音乐 &hasmusic=1  含短链接 &haslink=1
    def get_Weibo_Compre_Query_Result_Json(self,now_time,taskId):
        chrome_options = Options()  # 实例化Option对象
        chrome_options.add_argument('--headless')  # 把Chrome浏览器设置为静默模式
        chrome_options.add_argument('--disable-gpu')  # 禁止加载图片
        dr = webdriver.Chrome(options=chrome_options)  # 设置引擎为Chrome，在后台默默运行
        # 通过新浪邮箱登录，微博登录需要短信验证码
        URL = 'https://mail.sina.com.cn/?from=mail'
        dr.get(URL)
        sleep(1)
        # binascii.a2b_hex(auth_str).decode("utf-8")
        setting = Setting()
        auth_str = setting.get_AUTH_STR()
        decode_str = binascii.a2b_hex(auth_str).decode("utf-8")
        key_list = decode_str.split(setting.get_AUTH_SPLIT_STR())
        dr.find_element_by_xpath('//*[@id="freename"]').send_keys(key_list[0])
        dr.find_element_by_xpath('//*[@id="freepassword"]').send_keys(key_list[1])
        is_login_sina_email = True
        crawler_data_list = []
        crawler_data_list_json = []
        data = {}
        try:
            # 自动获取登录按钮,还有问题
            # login_button_element = self.get_login_button_togger(dr)
            # dr.execute_script("arguments[0].click();", login_button_element)
            # 有广告的页面
            locator = '/html/body/div[3]/div/div[2]/div/div/div[4]/div[1]/div[1]/div[7]/div[1]/a[1]'
            if dr.find_element_by_xpath(locator) is not None:
                dr.find_element_by_xpath(locator).click()
            else:
                # 没有广告的页面
                locator = '/html/body/div[1]/div/div[2]/div/div/div[4]/div[1]/div[1]/div[7]/div[1]/a[1]'
                if dr.find_element_by_xpath(locator) is not None:
                    dr.find_element_by_xpath(locator).click()
        except:
            is_login_sina_email = False
            pass
        if is_login_sina_email:
            print("新浪邮箱登录成功，在后台浏览器打开新TAB页，进行微博免登录搜索，支持多页查询")
            # print(dr.current_url)
            # print(dr.page_source)
            print("----------------------------------------------------------")
            sleep(3)
            # 在浏览器打开 新tab，进行微博查询,利用新浪邮箱登录的身份，微博不用再登录
            dr.find_element_by_tag_name('body').send_keys(Keys.CONTROL + 't')
            is_not_last_page = True
            curent_page_num = 1
            while is_not_last_page and curent_page_num <= self.turn_page:
                try:
                    if curent_page_num == 1:
                        url = "https://s.weibo.com/weibo?q=" + self.query_word + "&Refer=weibo_weibo"
                        print("目前是第1页------")
                        dr.get(url)
                    else:
                        next_page_element = self.get_next_page_togger(dr)
                        dr.execute_script("arguments[0].click();", next_page_element)
                        sleep(1)
                        print("自动获取到第{}页-----".format(str(curent_page_num)))
                    # print(dr.page_source)
                    curent_page_num += 1
                    print("获取微博搜索数据.........")
                    htmlinfo = bytes(dr.page_source, encoding='utf-8')
                    soup = BeautifulSoup(htmlinfo, 'html.parser')
                    div_box = soup.find_all('div', attrs={'class': 'm-con-l'})
                    if len(div_box) > 0:
                        # card_item_list = div_box[0].find_all(name='div')[3].find_all('div',
                        #                                                              attrs={'class': 'card-wrap'})
                        card_item_list = div_box[0].find_all('div', attrs={'class': 'card-wrap'})
                        for card_item in card_item_list:
                            # 标题,提取简介里的 【】，若没有则提取前10个字符
                            try:
                                info_title_old = card_item.find_all('p', attrs={'class': 'txt'})[0].text.replace(
                                    "\n", "").strip()
                                info_title = re.findall("【(.*?)】", info_title_old)
                                if len(info_title) == 0:
                                    info_title = info_title_old[0:20]
                            except:
                                info_title = ""
                                pass
                            # 来源
                            try:
                                info_source = \
                                    card_item.find_all('div', attrs={'class': 'info'})[0].find_all(name='div')[
                                        1].text.replace("\n", "")
                            except:
                                info_source = ""
                                pass
                            # 时间
                            try:
                                info_time = \
                                    card_item.find_all('p', attrs={'class': 'from'})[0].text.replace("\n",
                                                                                                     "").strip().split(
                                        "\xa0")[0]
                                info_time = DateTimeHelper.get_standTime_By_Str(info_time)
                            except:
                                info_time = ""
                                pass
                            # 简介
                            try:
                                info_breif = card_item.find_all('p', attrs={'class': 'txt'})[0].text.replace("\n",
                                                                                                             "").strip()
                            except:
                                info_breif = ""
                                pass
                            # 链接
                            try:
                                info_href = "https:" + \
                                            card_item.find_all('p', attrs={'class': 'from'})[0].find_all(name='a')[
                                                0].attrs.get("href")
                            except:
                                info_href = ""
                                pass
                            each_data_dict = {}
                            each_data_dict["标题"] = info_title
                            each_data_dict["来源"] = info_source
                            each_data_dict["时间"] = info_time
                            each_data_dict["简介"] = info_breif
                            each_data_dict["链接"] = info_href
                            each_data_dict_json = {}
                            each_data_dict_json["title"] = str(info_title)
                            each_data_dict_json["source"] = info_source
                            each_data_dict_json["time"] = info_time
                            each_data_dict_json["introduction"] = info_breif
                            each_data_dict_json["link"] = info_href
                            each_data_dict_json["createTm"] = now_time
                            each_data_dict_json["taskId"] = taskId
                            crawler_data_list_json.append(each_data_dict_json)
                            crawler_data_list.append(each_data_dict)
                        data["crawler_data_list"] = crawler_data_list
                        data["crawler_data_list_json"] = crawler_data_list_json

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

    # 获取登录的按钮,如果没有为None
    def get_login_button_togger(self, web_driver):
        login_button_tag = ["a", "span"]
        login_button_text = ["登录"]
        login_button_element = None
        is_not_find_login = True
        for tag in login_button_tag:
            for txt in login_button_text:
                login_button_path = "//{}[contains(text(),'{}')]".format(tag, txt)
                try:
                    login_button_element = web_driver.find_element_by_xpath(login_button_path)
                    is_not_find_login = False
                    break
                except Exception as e:
                    pass
                continue
            if is_not_find_login == False:
                break
        return login_button_element