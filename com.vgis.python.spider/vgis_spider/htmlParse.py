#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    : 2021/1/7 23:44
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : htmlParse.py
# @Desc    ：对网页html进行解析，提取相关信息
# @Software: PyCharm
import time
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from bs4.element import NavigableString
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from specialValue import filterValueArray
from vgis_utils.iteratorTools import IteratorHelper
from vgis_utils.vgis_string.stringTools import StringHelper

headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2;.NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; InfoPath.3; .NET4.0C; .NET4.0E)',
    'Accept': 'image/webp,image/*,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://www.baidu.com/link?url=_andhfsjjjKRgEWkj7i9cFmYYGsisrnm2A-TN3XZDQXxvGsM9k9ZZSnikW2Yds4s&amp;amp;wd=&amp;amp;eqid=c3435a7d00006bd600000003582bfd1f',
    'Connection': 'keep-alive'}


class WebDataParser:
    # 初始化
    def __init__(self, siteUrl=None):
        print("采集网址为{}".format(siteUrl))
        self.siteUrl = siteUrl
        self.is_daynamic_data = False
        self.web_driver = None

    # 设置网址
    def set_curent_page_url(self, web_url):
        self.siteUrl = web_url

    # 设置网页的html
    def set_curent_page_html(self, html_str):
        # self.htmlinfo = bytes(html_str, encoding='utf-8')
        self.htmlinfo = html_str

    # 网址html内容解析
    # TODO:切换代理，防止ip被封
    # # 每次连接等待几秒，避免出现验证码
    def get_web_page_html(self):
        r = requests.get(url=self.siteUrl, headers=headers)
        r.encoding = r.apparent_encoding
        self.htmlinfo = r.text
        # r.encoding = 'utf-8'
        # # r.encoding = 'gb2312'
        # self.htmlinfo = r.content
        if self.is_dynamic_content_by_javascrit(self.htmlinfo):
            print("是动态数据网址，切换到selenium模拟谷歌浏览器访问模式")
            self.is_daynamic_data = True
            chrome_options = Options()  # 实例化Option对象
            chrome_options.add_argument('--headless')  # 把Chrome浏览器设置为静默模式
            chrome_options.add_argument('--disable-gpu')  # 禁止加载图片
            # desired_capabilities = DesiredCapabilities.CHROME
            # desired_capabilities["pageLoadStrategy"] = "none"  # 设置非阻塞
            # driver = webdriver.Chrome(options=chrome_options,desired_capabilities=desired_capabilities)  # 设置引擎为Chrome，在后台默默运行
            driver = webdriver.Chrome(options=chrome_options)  # 设置引擎为Chrome，在后台默默运行
            self.web_driver = driver
            # driver.implicitly_wait(10)  #隐式等待
            driver.get(self.siteUrl)
            # 强制等待10秒，解决部分网站数据没有完全加载的问题
            time.sleep(10)
            tmp_htmlinfo = driver.page_source
            # tmp_htmlinfo = etree.HTML(driver.page_source)
            # self.htmlinfo = bytes(tmp_htmlinfo, encoding='utf-8')
            self.htmlinfo = bytes(tmp_htmlinfo, encoding=self.get_encode_in_html(tmp_htmlinfo))
            # driver.quit()
            # driver.close()
        # return htmlinfo

    def get_encode_in_html(self, htmlcode):
        # htmlcode = "<meta http-equiv=\"Content-Type\" content=\"text/html;charset=gb2312\"><html>"
        # htmlcode = "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=gbk\" /><html>"
        # htmlcode = "<meta charset=\"gb2312\"><html>"
        # htmlcode = "<meta charset=\"utf-8\" /><html>"
        encode = StringHelper.get_str_btw(htmlcode, "charset=", ">").replace("\"", "").replace("/", "").strip()
        return encode

    # 判断是否为动态脚本生成的网页内容
    def is_dynamic_content_by_javascrit(self, htmlinfo):
        is_dynamic = False
        soup = BeautifulSoup(htmlinfo, 'html.parser')
        div_text = ""
        for div in soup.find_all(name='div'):
            div_text += div.text.strip()
        if div_text == "" or "加载" in div_text or "Loading" in div_text or "loading" in div_text:
            is_dynamic = True
        return is_dynamic

    # 得到网址数据是否动态数据
    def get_web_page_data_type(self):
        return self.is_daynamic_data

    # 自动解析网页中的ul列表数据
    def parse_ul_in_html(self):
        self.get_web_page_html()
        soup = BeautifulSoup(self.htmlinfo, 'html.parser')
        # 所有识别结果的数据记录数组
        all_recog_data_record_list = []
        # 所有识别结果的字段信息数组（字段名，字段路径）
        all_recog_data_field_list = []
        for ul in soup.find_all(name='ul'):
            # ul里文本不能为空，或者换行符
            if ul.text.strip() != "" and ul.text.strip() != "\n":
                # ul下的li数量要超过1个
                if len(ul.find_all(name='li')) > 1:
                    # li的子元素个数大于1
                    iterator_operator = IteratorHelper(ul.find(name='li').children)
                    iterator_count = iterator_operator.get_iterator_count()
                    if iterator_count > 1:
                        # li的有效字段个数，即text内容有效值数量超过1个
                        li_valid_filed_count = 0
                        for li in ul.find_all(name='li'):
                            li_valid_filed_count = self.get_dom_field_count(li)
                            if li_valid_filed_count < 2:
                                break
                        if len(ul.text.strip().split("\n")) > 1 and li_valid_filed_count > 1:
                            is_has_filter_value = False
                            # li text判断是否有过滤词,如果有过滤词，认为不是需要采集的业务数据
                            for li in ul.find_all(name='li'):
                                is_has_filter_value = self.is_has_filter_value_in_dom_text(li)
                                if is_has_filter_value:
                                    break
                            if is_has_filter_value is False:
                                # 判断每个li下的字段个数差异是否在阈值范围内如15，这样程序才认为是规范化的列表数据
                                if self.check_each_li_field_count_diff_in_range(ul, 15):
                                    print('----------------------------')
                                    # print(str(ul.text).encode("UTF-8").decode().strip().replace('\n', '').replace('\t', ''))
                                    css_select_path_head = ul.parent.name + self.get_attrbuite_str(
                                        ul.parent.attrs) + ">"
                                    css_select_path_head += ul.name + self.get_attrbuite_str(
                                        ul.attrs) + ">"
                                    field_obj_list = self.get_dom_contain_element_css_selector_and_field_old(ul,
                                                                                                             css_select_path_head)

                                    all_recog_data_field_list.append(field_obj_list)
        # 获取每个抓取字段内容并转化成excel需要的数据对象
        all_recog_data_record_list = self.get_excel_value_from_recog_field(soup, all_recog_data_field_list)
        return all_recog_data_record_list

    # 自动解析网页中的table数据
    # 每个td的css selector路径都一样，导致每列无法定位,所以需要认为增加td1,td2之类
    def parse_table_in_html(self):
        # htmlinfo = self.get_web_page_html()
        soup = BeautifulSoup(self.htmlinfo, 'html.parser')
        # print("输出htmlinfo:"+str(self.htmlinfo, encoding = "utf-8"))
        # 所有识别结果的数据记录数组
        all_recog_data_record_list = []
        # 所有识别结果的字段信息数组（字段名，字段路径）
        all_recog_data_field_list = []
        for table in soup.find_all(name='table'):
            print("循环每个table")
            # print(table.contents)
            # print(str(table.contents[0]).encode("UTF-8").decode())
            # table里文本不能为空，或者换行符
            if table.text.strip() != "" and table.text.strip() != "\n":
                # table下的tr数量要超过1个，即有多行
                if len(table.find_all(name='tr')) > 1:
                    print("table 下面 tr超过一行")
                    # # tr的子元素个数大于1，即有多列
                    # # 有可能第一个tr里的td个数（合并单元格后）跟其他tr的td个数不同，所以从第二行开始计算td个数
                    # iterator_operator = IteratorOperate(table.find(name='tr').children)
                    # iterator_count = iterator_operator.get_iterator_count()
                    # if iterator_count > 1:
                    # 第二行开始的tr有效字段个数，即text内容有效值数量超过1个
                    tr_valid_filed_count = 0
                    tr_row = 0
                    tr_list_obj = self.remove_except_tr_in_table(soup, table.find_all(name='tr'))
                    for tr in tr_list_obj:
                        tr_row += 1
                        if tr_row > 1:
                            tr_valid_filed_count = self.get_tr_field_count(soup, tr)
                            if tr_valid_filed_count > 1:
                                break
                    # if len(table.text.strip().split("\n")) > 1 and tr_valid_filed_count > 1:
                    # 部分表格table.text返回值没有用\n分割
                    if tr_valid_filed_count > 1:
                        print("table 有效字段个数超过1")
                        is_has_filter_value = False
                        # tr text判断是否有过滤词,如果有过滤词，认为不是需要采集的业务数据
                        # for tr in table.find_all(name='tr'):
                        #     is_has_filter_value = self.is_has_filter_value_in_dom_text(tr)
                        #     if is_has_filter_value:
                        #         break
                        if is_has_filter_value is False:
                            # 判断第二行开始的tr下的字段个数是否在阈值范围内如0,即每行的列数都相同，这样程序才认为是规范化的表格数据
                            if self.check_each_tr_field_count_diff_in_range(soup, table, 0):
                                print('----------------------------')
                                # print(str(table.text).encode("UTF-8").decode().strip().replace('\n', '').replace('\t', ''))
                                # print(table.text.strip().replace('\n', '').replace('\t', ''))
                                # css_select_path_head = table.parent.name + self.get_attrbuite_str(
                                #     table.parent.attrs) + ">"
                                # css_select_path_head += table.name + self.get_attrbuite_str(
                                #     table.attrs) + ">"
                                css_select_path_head = self.get_dom_parent_css_slector_util_top(table)
                                css_select_path_head += ">"
                                # 得到tr的路径，每个td字段的path一次为 td[0],td[1],针对table数据做特殊处理，在解析时解析后再对每个td字段进行定位
                                field_obj_list = self.get_table_contain_tr_path_and_field(soup, table,
                                                                                          css_select_path_head)
                                all_recog_data_field_list.append(field_obj_list)
        # 获取每个抓取字段内容并转化成excel需要的数据对象
        all_recog_data_record_list = self.get_excel_value_from_recog_field(soup, all_recog_data_field_list)
        return all_recog_data_record_list

    # 利用pandas的方法直接读取table，但与ul和div的数据读取流程不一致
    def pares_table_in_html_by_pandas(self):
        # import pandas as pd
        # url = 'http://www.kuaidaili.com/free/'
        # df = pd.read_html(url)[0]
        pass

    # 自动解析网页中的div数据，相同class
    def parse_div_class_in_html(self):
        # htmlinfo = self.get_web_page_html()
        soup = BeautifulSoup(self.htmlinfo, 'html.parser')
        # tt = soup.select('div.key-list.imglazyload>div.item-mod>div.infos>a.lp-name>span.items-name')
        div_class_obj = {}
        for div in soup.find_all(name='div'):
            if div.attrs.get("class") != None:
                div_class_name = self.convert_dom_class_str_from_array(div.attrs.get("class"))
                # print(div.attrs.get("class"))
                if div_class_name not in div_class_obj:
                    div_class_obj[div_class_name] = 1
                else:
                    div_class_obj[div_class_name] += 1
        # 对出现频次大于5个div class进行解析
        new_div_class_obj = {key: value for key, value in div_class_obj.items() if value > 5}
        print(new_div_class_obj)
        # 所有识别结果的div存储的数组
        all_need_div_content_list = []
        # 所有识别结果的数据记录数组
        all_recog_data_record_list = []
        # 所有识别结果的字段信息数组（字段名，字段路径）
        all_recog_data_field_list = []
        # 循环筛选后的不同class的div
        for key, value in new_div_class_obj.items():
            # 获取相同class的div
            all_class_div_content = soup.find_all("div", attrs={"class": key})
            print("---class--------------------------------------------------------------->" + key)
            # 对这些相同calss div进行分割，分割原则为是否为属于相同parent
            split_div_conent_same_class = self.split_div_list_into_same_parent(all_class_div_content)
            for div_content_same_class in split_div_conent_same_class:
                # 判断相同parent的相同class div，有效字段数的差值是否在阈值范围内，如40
                if self.check_div_field_count_diff_in_range(div_content_same_class, 40):
                    need_div_content_list = []
                    for div_content in div_content_same_class:
                        if div_content.text is not None and div_content.text.strip() != "":
                            # 判断div对象是否有并列的同胞，如果没有则认为不是循环的数据
                            if div_content.find_next_sibling() is not None:
                                # 判断并列的同胞div是否具有相同的class
                                is_has_same_class = self.check_two_dom_has_same_class(div_content,
                                                                                      div_content.find_next_sibling())
                                if is_has_same_class:
                                    # 判断div的有效字段个数是否大于0，如果这些字段路径相同则暂时判断不出有效的字段个数
                                    valid_field_count = self.get_dom_field_count(div_content)
                                    if valid_field_count > 0:
                                        print("|||||||||||||||||||||||||||||||||||||||||||||||||||")
                                        # print(str(div_content.text).encode("UTF-8").decode().strip().replace('\n', '').replace('\t', ''))
                                        # print(div_content.text.strip().replace('\n', '').replace('\t', ''))
                                        need_div_content_list.append(div_content)
                    if len(need_div_content_list) > 0:
                        all_need_div_content_list.append(need_div_content_list)
        # 解析得到的不同识别结果，对每个元素获取css-selector
        # soup.select('div.key-list.imglazyload>div.item-mod>div.infos>a.lp-name>span.items-name')
        # 获取div class下的抓取字段和每个字段访问路径
        for div_class_array in all_need_div_content_list:
            each_recog_data_field_list = []
            # print(div_class_array)
            div_class = div_class_array[0]
            # print(div_class)

            css_select_path_head = div_class.parent.name + self.get_attrbuite_str(div_class.parent.attrs) + ">"
            css_select_path_head += div_class.name + self.get_attrbuite_str(div_class.attrs) + ">"
            # print(css_select_path_head)
            field_obj_list = self.get_dom_contain_element_css_selector_and_field(div_class, css_select_path_head)

            # css_xpath_head = "//{}[@class='{}']".format(div_class.name, self.get_attrbuite_str2(div_class.attrs)) + "/"
            # field_obj_list = self.get_dom_contain_element_xpath_and_field(div_class, css_xpath_head)

            all_recog_data_field_list.append(field_obj_list)
        # 获取每个抓取字段内容并转化成excel需要的数据对象
        all_recog_data_record_list = self.get_excel_value_from_recog_field(soup, all_recog_data_field_list)
        return all_recog_data_record_list

    # 对返回的dom对象class数组进行拼接还原，中间用空格
    def convert_dom_class_str_from_array(self, class_array):
        class_str = ""
        for split_class in class_array:
            class_str += split_class + " "
        class_str = class_str.rstrip(" ")
        return class_str

    # 获取识别字段的字段内容信息并转化为excel生成需要的数据对象
    def get_excel_value_from_recog_field(self, soup, all_recog_data_field_list):
        all_recog_data_record_list = []
        # 针对路径相同的字段进行字段去重
        all_recog_data_field_list = self.remain_one_field_of_same_path(all_recog_data_field_list)
        # 获取div class下的每个抓取字段的内容
        # 循环识别结果
        all_recog_field_column_value_list = []
        for i in range(len(all_recog_data_field_list)):
            # 获取每个识别结果的列（字段）
            each_recog_field_column_value_list = []
            for w in range(len(all_recog_data_field_list[i])):
                single_field_obj = all_recog_data_field_list[i][w]
                # {"字段旧名称":"字段1","字段新名称":"地址","字段路径":"div.key-list.imglazyload>div.item-mod>div.infos>a.lp-name>span.items-name"
                # {"字段旧名称":"字段1","字段新名称":"地址","字段路径":"//div[@class="search-item sv-search-company"]/div/div[3]/div[5]/div/span[2]"
                single_field_path = single_field_obj.get("字段路径")
                # 得到每个字段的所有记录，相当于数据表的一列
                if "ThisIsTable.HeadRow." not in single_field_path:
                    single_field_cloumn_value_list = soup.select(single_field_path)
                    # single_field_cloumn_value_list = etree.HTML(soup.prettify()).xpath(single_field_path)
                # 针对表格数据特别处理
                else:
                    single_field_cloumn_value_list = self.get_table_td_value_list(soup, single_field_path)
                each_recog_field_column_value_list.append(single_field_cloumn_value_list)
            all_recog_field_column_value_list.append(each_recog_field_column_value_list)
        # 赋值形成excel需要的数组对象
        # 循环识别结果
        for j in range(len(all_recog_field_column_value_list)):
            each_recog_data_record_list = []
            each_recog_field_column_value_list = all_recog_field_column_value_list[j]
            # 抓取数据至少有两个字段
            if len(each_recog_field_column_value_list) > 1:
                # 获取到字段中的最多行数
                record_rows = self.get_max_row_records(each_recog_field_column_value_list)
                # 循环每个识别结果的行
                for h in range(record_rows):
                    # 针对第一行，添加字段的路径
                    if h == 0:
                        tmp_obj = {}
                        for u in range(len(each_recog_field_column_value_list)):
                            tmp_single_field_obj = all_recog_data_field_list[j][u]
                            tmp_single_filed_new_name = tmp_single_field_obj.get("字段新名称")
                            tmp_obj[tmp_single_filed_new_name] = tmp_single_field_obj.get("字段路径")
                        each_recog_data_record_list.append(tmp_obj)
                    obj = {}
                    # 循环每个识别结果的列（字段）
                    for k in range(len(each_recog_field_column_value_list)):
                        single_field_obj = all_recog_data_field_list[j][k]
                        single_filed_new_name = single_field_obj.get("字段新名称")
                        single_field_path = single_field_obj.get("字段路径")
                        # 需要保证每个字段的记录行数都是一样的，否则会报错
                        try:
                            cell_obj = each_recog_field_column_value_list[k][h]
                            if "ThisIsTable.HeadRow." not in single_field_path:
                                obj[single_filed_new_name] = self.get_field_value_contain_tails(cell_obj)
                            else:
                                obj[single_filed_new_name] = cell_obj.get("text").lstrip("\n").lstrip(" ").rstrip(
                                    " ").rstrip("\n")
                        except Exception as e:
                            obj[single_filed_new_name] = ""
                            pass
                        continue
                    each_recog_data_record_list.append(obj)
                all_recog_data_record_list.append(each_recog_data_record_list)
        return all_recog_data_record_list

    # 获取抓取的字段值（除了text外，把前后的tail也包含捡来）
    # 如：舞钢广众<font color="red">钢铁</font>有限公司
    def get_field_value_contain_tails(self, cell_obj):
        field_value = ""
        field_value = cell_obj.text.lstrip("\n").lstrip(" ").rstrip(" ").rstrip("\n")
        if type(cell_obj.nextSibling) == NavigableString:
            field_value += cell_obj.nextSibling.lstrip("\n").lstrip(" ").rstrip(" ").rstrip("\n")
        if type(cell_obj.previousSibling) == NavigableString:
            field_value = cell_obj.previousSibling.lstrip("\n").lstrip(" ").rstrip(" ").rstrip("\n") + field_value
        return field_value

    # 获取表格td单列的值
    def get_table_td_value_list(self, soup, td_path):
        single_field_cloumn_value_list = []
        split_array = td_path.split(">")
        tr_path = ""
        for i in range(len(split_array)):
            if i < len(split_array) - 2:
                tmp_path = split_array[i] + ">"
                tr_path += tmp_path
        tr_path = tr_path.rstrip(">")
        td_index = int(split_array[len(split_array) - 2].lstrip("td[").rstrip("]"))
        head_row_num = int(split_array[len(split_array) - 1].lstrip("ThisIsTable.HeadRow."))
        tr_list = soup.select(tr_path)
        # 去除异常的tr，如tr字段数相差10倍，tr字段合并单元格等情况
        tr_list = self.remove_except_tr_in_table(soup, tr_list)
        for t in range(len(tr_list)):
            tr_obj = tr_list[t]
            if t > head_row_num:
                tr_obj_td_list = tr_obj.find_all(name='td')
                for w in range(len(tr_obj_td_list)):
                    if w == td_index:
                        field_column_value_obj = {}
                        field_column_value_obj["text"] = tr_obj_td_list[w].get_text().strip()
                        single_field_cloumn_value_list.append(field_column_value_obj)
        return single_field_cloumn_value_list

    # 获取最多的行数
    def get_max_row_records(self, each_recog_field_column_value_list):
        row_num = len(each_recog_field_column_value_list[0])
        for item in each_recog_field_column_value_list:
            if len(item) > row_num:
                row_num = len(item)
        return row_num

    # 将相同路径的字段全部去掉
    def remove_all_field_of_same_path(self, all_recog_data_field_list):
        for j in range(len(all_recog_data_field_list)):
            field_obj_list = all_recog_data_field_list[j]
            field_obj_path_array = []
            remove_index = []
            for w in range(len(field_obj_list)):
                field_obj_path = field_obj_list[w].get("字段路径")
                field_obj_path_array.append(field_obj_path)
            for k in range(len(field_obj_path_array)):
                field_obj_path = field_obj_path_array[k]
                if field_obj_path_array.count(field_obj_path) > 1:
                    remove_index.append(k)
            cnt = 0
            for index in remove_index:
                del all_recog_data_field_list[j][index - cnt]
                cnt += 1
        return all_recog_data_field_list

    # 将相同路径的字段去掉重复的，只保留一个
    def remain_one_field_of_same_path(self, all_recog_data_field_list):
        for j in range(len(all_recog_data_field_list)):
            field_obj_list = all_recog_data_field_list[j]
            field_obj_path_array = []
            remove_index = []
            for w in range(len(field_obj_list)):
                field_obj_path = field_obj_list[w].get("字段路径")
                if field_obj_path in field_obj_path_array:
                    remove_index.append(w)
                else:
                    field_obj_path_array.append(field_obj_path)
            cnt = 0
            for index in remove_index:
                del all_recog_data_field_list[j][index - cnt]
                cnt += 1
        return all_recog_data_field_list

    # 将多个attr用.连接
    def get_attrbuite_str(self, attrs):
        attr_str = ""
        attr_array = attrs.get("class")
        if attr_array is not None:
            for attr in attr_array:
                attr_str += attr + "."
            attr_str = attr_str.rstrip(".")
        if attr_str != "":
            attr_str = "." + attr_str
        return attr_str

    # 将多个attr用空格连接
    def get_attrbuite_str2(self, attrs):
        attr_str = ""
        attr_array = attrs.get("class")
        if attr_array is not None:
            for attr in attr_array:
                attr_str += attr + " "
            attr_str = attr_str.rstrip(" ")
        # if attr_str != "":
        #     attr_str = "." + attr_str
        return attr_str

    # 针对dom对象（如<table>)逐级往上获取父元素，直到顶部元素<html>
    def get_dom_parent_css_slector_util_top(self, current_dom_obj):
        is_not_top = True
        css_slector = ""
        while is_not_top:
            if current_dom_obj.name == "html":
                is_not_top = False
            else:
                css_slector = current_dom_obj.name + self.get_attrbuite_str(
                    current_dom_obj.attrs) + ">" + css_slector
                current_dom_obj = current_dom_obj.parent
        css_slector = css_slector.rstrip(">")
        return css_slector

    # 得到tr下的td元素的字段路径css-selector
    def get_table_contain_tr_path_and_field(self, soup, table_obj, css_selector_head):
        field_obj_list = []
        # tr_list = table_obj.find_all(name='tr')
        tr_list = self.remove_except_tr_in_table(soup, table_obj.find_all(name='tr'))
        is_has_th = False
        head_row_num = 0
        # 表头在tr/th
        if len(tr_list[0].find_all(name='th')) > 0:
            is_has_th = True
            head_row_num = 0
        # 表头在tr/td，如果head_row_num=-1则没有表头
        else:
            head_row_num = self.get_head_tr_of_table(soup, table_obj)
        head_tr = tr_list[head_row_num]
        body_tr = tr_list[head_row_num + 1]
        head_tr_td_list = None
        if is_has_th:
            head_tr_td_list = head_tr.find_all(name='th')
        else:
            head_tr_td_list = head_tr.find_all(name='td')
        # body_tr_td_list = body_tr.find_all(name='td')
        for i in range(len(head_tr_td_list)):
            field_obj = {}
            if head_row_num != -1:
                if head_tr_td_list[i].get_text().strip() != "":
                    field_obj["字段旧名称"] = head_tr_td_list[i].get_text().strip()
                else:
                    field_obj["字段旧名称"] = "字段" + str(i + 1)
                field_obj["字段新名称"] = field_obj["字段旧名称"]
            else:
                field_obj["字段旧名称"] = "字段" + str(i + 1)
                field_obj["字段新名称"] = "字段" + str(i + 1)
            field_obj["字段路径"] = css_selector_head + self.get_parent_css_slector_util_top_old(table_obj,
                                                                                             body_tr) + ">td[" + str(
                i) + "]>ThisIsTable.HeadRow." + str(head_row_num)
            field_obj_list.append(field_obj)
        return field_obj_list

    # 得到表格的头行，即包含字段名称的那行
    # 针对合并单元格的表格，表头不一定在第一行
    # 如果没有表头行返回-1    #
    def get_head_tr_of_table(self, soup, table_obj):
        # tr_list = table_obj.find_all(name='tr')
        tr_list = self.remove_except_tr_in_table(soup, table_obj.find_all(name='tr'))
        td_count = len(tr_list[len(tr_list) - 1].find_all(name='td'))
        head_row_num = -1
        for i in range(len(tr_list)):
            if len(tr_list[i].find_all(name='td')) == td_count:
                head_row_num = i
                # 如果表头内容过长，那有可能就是没有表头
                tr_td_list = tr_list[i].find_all(name='td')
                for w in range(len(tr_td_list)):
                    if len(tr_td_list[w].get_text().strip()) > 10:
                        head_row_num = -1
                        break
                break
        return head_row_num

    # 得到每个元素的字段路径css-selector，给ul用
    def get_dom_contain_element_css_selector_and_field_old(self, dom_obj, css_selector_head):
        field_obj_list = []
        field_index = 1
        # 获取当前元素的所有子孙节点
        descendants = dom_obj.descendants
        for descendant in descendants:
            if type(descendant) != NavigableString and type(descendant) != Comment and len(descendant.contents) == 1:
                if descendant.text.replace('\n', '').strip() != "":
                    # 找到了有效的字段内容
                    field_obj = {}
                    field_obj["字段旧名称"] = "字段" + str(field_index)
                    field_obj["字段新名称"] = "字段" + str(field_index)
                    field_obj["字段路径"] = css_selector_head + self.get_parent_css_slector_util_top_old(dom_obj,
                                                                                                     descendant)
                    field_obj_list.append(field_obj)
                    field_index += 1
        return field_obj_list

    # 得到每个元素的字段路径css-selector，给div用
    def get_dom_contain_element_css_selector_and_field(self, dom_obj, css_selector_head):
        field_obj_list = []
        field_index = 1
        # 获取当前元素的所有子孙节点
        descendants = dom_obj.descendants
        for descendant in descendants:
            if type(descendant) != NavigableString and type(descendant) != Comment and hasattr(descendant,
                                                                                               "contents") and len(
                descendant.contents) == 1:
                if descendant.text.replace('\n', '').strip() != "":
                    # 找到了有效的字段内容
                    field_obj = {}
                    field_obj["字段旧名称"] = "字段" + str(field_index)
                    field_obj["字段新名称"] = "字段" + str(field_index)
                    field_obj["字段路径"] = css_selector_head + self.get_parent_css_slector_util_top(dom_obj, descendant)
                    field_obj_list.append(field_obj)
                    field_index += 1
        return field_obj_list

    # 得到每个元素的字段路径xpath,已作废
    def get_dom_contain_element_xpath_and_field(self, dom_obj, css_xpath_head):
        field_obj_list = []
        field_index = 1
        # 获取当前元素的所有子孙节点
        descendants = dom_obj.descendants
        for descendant in descendants:
            if type(descendant) != NavigableString and type(descendant) != Comment and len(descendant.contents) == 1:
                if descendant.text.replace('\n', '').strip() != "":
                    # 找到了有效的字段内容
                    field_obj = {}
                    field_obj["字段旧名称"] = "字段" + str(field_index)
                    field_obj["字段新名称"] = "字段" + str(field_index)
                    field_obj["字段路径"] = css_xpath_head + self.get_parent_css_xpath_util_top(dom_obj, descendant)
                    field_obj_list.append(field_obj)
                    field_index += 1
        return field_obj_list

    # 逐级往上获取各个父元素的css selector，直接到顶层元素,----给table,ul用
    def get_parent_css_slector_util_top_old(self, top_dom_obj, current_dom_obj):
        is_not_top = True
        css_slector = ""
        while is_not_top:
            if current_dom_obj.name == top_dom_obj.name and current_dom_obj.attrs == top_dom_obj.attrs:
                is_not_top = False
            else:
                css_slector = current_dom_obj.name + self.get_attrbuite_str(
                    current_dom_obj.attrs) + ">" + css_slector
                # css_slector = self.find_index_of_dom_in_same_level2(current_dom_obj) + ">" + css_slector
                current_dom_obj = current_dom_obj.parent
        css_slector = css_slector.rstrip(">")
        return css_slector

    # 逐级往上获取各个父元素的css selector，直接到顶层元素,给div用
    def get_parent_css_slector_util_top(self, top_dom_obj, current_dom_obj):
        is_not_top = True
        css_slector = ""
        while is_not_top:
            if current_dom_obj.name == top_dom_obj.name and current_dom_obj.attrs == top_dom_obj.attrs:
                is_not_top = False
            else:
                # css_slector = current_dom_obj.name + self.get_attrbuite_str(
                #     current_dom_obj.attrs) + ">" + css_slector
                css_slector = self.find_index_of_dom_in_same_level2(current_dom_obj) + ">" + css_slector
                current_dom_obj = current_dom_obj.parent
        css_slector = css_slector.rstrip(">")
        return css_slector

    # 逐级往上获取各个父元素的css xpath，直接到顶层元素，已作废
    def get_parent_css_xpath_util_top(self, top_dom_obj, current_dom_obj):
        is_not_top = True
        css_xpath = ""
        while is_not_top:
            if current_dom_obj.name == top_dom_obj.name and current_dom_obj.attrs == top_dom_obj.attrs:
                is_not_top = False
            else:
                css_xpath = self.find_index_of_dom_in_same_level(current_dom_obj) + "/" + css_xpath
                current_dom_obj = current_dom_obj.parent
        css_xpath = css_xpath.rstrip("/")
        return css_xpath

    # 获取dom对象在同一级出现的索引，从1开始计算，即计算出是第几个兄弟节点标签,适用于xpath，已作废
    def find_index_of_dom_in_same_level(self, dom_obj):
        dom_tag = ""
        if dom_obj.previous_siblings is not None and self.get_count_siblings(dom_obj.previous_siblings) > 0:
            index = self.get_count_siblings(dom_obj.previous_siblings) + 1
            dom_tag = dom_obj.name + "[" + str(index) + "]"
        else:
            if (dom_obj.next_siblings is not None and self.get_count_siblings(dom_obj.next_siblings) > 0):
                dom_tag = dom_obj.name + "[1]"
            else:
                dom_tag = dom_obj.name
        return dom_tag

    # 获取dom对象在同一级出现的索引，从1开始计算，即计算出是第几个兄弟节点标签，适用于css selector，给div用
    def find_index_of_dom_in_same_level2(self, dom_obj):
        dom_tag = ""
        if dom_obj.previous_siblings is not None and self.get_count_siblings(dom_obj.previous_siblings) > 0:
            index = self.get_count_siblings(dom_obj.previous_siblings) + 1
            dom_tag = dom_obj.name + ":nth-child(" + str(index) + ")"
        else:
            if (dom_obj.next_siblings is not None and self.get_count_siblings(dom_obj.next_siblings) > 0):
                dom_tag = dom_obj.name + ":nth-child(1)"
            else:
                dom_tag = dom_obj.name
        return dom_tag

    # 获取有效siblings数组对象的个数
    def get_count_siblings(self, siblings_list):
        # 没有tag name的标签，不计算索引值，如<span>微信</span>或<span>扫一扫</span>，其中 或 不做考虑
        count = 0
        for next in siblings_list:
            if next.name is not None and next.name.strip() != "":
                count += 1
        return count

    # 基于确定的识别结果集规则进行数据采集
    def spider_data_by_confirm_rule(self, field_name_str, field_path_str):
        # self.get_web_page_html()
        soup = BeautifulSoup(self.htmlinfo, 'html.parser')
        # 根据识别结果序号，需要采集的字段及名称，进行html标签定位，并做翻页(，如下一页，>）
        field_name_list = field_name_str.split(",")
        field_path_list = field_path_str.split("&&")
        all_recog_data_field_list = []
        field_obj_list = []
        for i in range(len(field_name_list)):
            field_name = field_name_list[i]
            field_path = field_path_list[i]
            field_obj = {}
            field_obj["字段新名称"] = field_name
            field_obj["字段路径"] = field_path
            field_obj_list.append(field_obj)
        all_recog_data_field_list.append(field_obj_list)
        # 获取每个抓取字段内容并转化成excel需要的数据对象
        all_recog_data_record_list = self.get_excel_value_from_recog_field(soup, all_recog_data_field_list)
        return all_recog_data_record_list

    # 自动翻页，并获取数据，在chrome浏览器里不断点击下一页，直接没有为止,或者根据传入页数来做控制翻到多少页
    def auto_turn_next_page_and_get_data_in_page(self, all_crawler_data_record_list, website_url, fields_name_str,
                                                 fields_path_str, turn_page_num):
        # 针对静态数据网站，在获取第一页数据时没有用web_driver
        # 针对动态数据网站，在获取第一页数据时使用了web_driver
        if self.web_driver == None:
            chrome_options = Options()  # 实例化Option对象
            chrome_options.add_argument('--headless')  # 把Chrome浏览器设置为静默模式
            chrome_options.add_argument('--disable-gpu')  # 禁止加载图片
            driver = webdriver.Chrome(options=chrome_options)  # 设置引擎为Chrome，在后台默默运行
            driver.get(website_url)
            self.web_driver = driver
        # 下一页url，静态数据网站返回不同url，动态数据网站返回的url不变，因此就模拟点击下一页操作一直在浏览器中执行即可
        next_page_element = self.get_next_page_togger(self.web_driver)
        if next_page_element is not None:
            is_not_last_page = True
            curent_page_num = 1
            while is_not_last_page and curent_page_num <= turn_page_num:
                try:
                    next_page_element = self.get_next_page_togger(self.web_driver)
                    self.web_driver.execute_script("arguments[0].click();", next_page_element)
                    curent_page_num += 1
                    print("自动获取到第{}页-----".format(str(curent_page_num)))
                    if self.is_daynamic_data:
                        self.set_curent_page_html(self.web_driver.page_source)
                    # 如果是静态数据网站，页面html得用request得到，这样才能和第一次识别提取到的路径对应上
                    else:
                        next_page_url = self.web_driver.current_url
                        r = requests.get(url=next_page_url, headers=headers)
                        r.encoding = r.apparent_encoding
                        # r.encoding = 'utf-8'
                        self.set_curent_page_html(r.content.decode())
                        self.set_curent_page_html(r.text)
                    temp_data_record_list = self.spider_data_by_confirm_rule(fields_name_str, fields_path_str)
                    # 删除表格的第一行（字段路径）
                    if len(temp_data_record_list) > 0 and len(temp_data_record_list[0]) > 0:
                        del temp_data_record_list[0][0]
                        all_crawler_data_record_list += temp_data_record_list
                    else:
                        print("当前页没有抓取到数据")
                except Exception as exp:
                    # 通过没有下一页的提示错误来分析，是否到了最后一页
                    if "Cannot read property 'click' of null" in str(exp):
                        print("当前已到最后一页")
                    else:
                        print("翻页错误：{}".format(exp))
                    is_not_last_page = False

                    pass
        else:
            print("没有找到翻页按钮")
        # driver.quit()
        # driver.close()
        return all_crawler_data_record_list

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

    # 将所有数组合并成一个数组
    def convert_all_list_into_one_list(self, all_data_record_list):
        result_data_list = []
        for each_data_record_list in all_data_record_list:
            for data_field_value_obj in each_data_record_list:
                result_data_list.append(data_field_value_obj)
        return result_data_list

    # 获取元素如li,div下面有效字段的个数
    def get_dom_field_count(self, dom_obj):
        filed_count = 0
        dom_text_value_list = dom_obj.text.split("\n")
        for each_text in dom_text_value_list:
            if each_text.replace('\n', '').strip() != "":
                filed_count += 1
        return filed_count

    # 获取tr下面的th或td个数
    def get_tr_field_count(self, soup, tr_obj):
        td_list = tr_obj.find_all(name="td")
        if len(td_list) == 0:
            td_list = tr_obj.find_all(name="th")
        return len(td_list)

    # 判断元素如li,div里是否有过滤词
    def is_has_filter_value_in_dom_text(self, dom_obj):
        is_has = False
        dom_text_value_list = dom_obj.text.split("\n")
        if list(set(dom_text_value_list) & set(filterValueArray)):
            is_has = True
        return is_has

    # 判断ul下面的每个li字段数量差异，如果超过阈值，则认为这些ul数值不是要采集的数据
    def check_each_li_field_count_diff_in_range(self, ul_obj, thre_num):
        is_diff_in_range = True
        obj = {}
        li_list_obj = ul_obj.find_all(name='li')
        for i in range(len(li_list_obj)):
            field_count = self.get_dom_field_count(li_list_obj[i])
            obj[i] = field_count
        if obj is not None:
            max_value = max(obj.values())
            min_value = min(obj.values())
            if max_value - min_value > thre_num:
                is_diff_in_range = False
        return is_diff_in_range

    # 判断table下面的每个tr字段数量差异，如果超过阈值，则认为这些table数值不是要采集的数据
    def check_each_tr_field_count_diff_in_range(self, soup, table_obj, thre_num):
        is_diff_in_range = True
        obj = {}
        # tr_list_obj = table_obj.find_all(name='tr')
        tr_list_obj = self.remove_except_tr_in_table(soup, tr_list_obj=table_obj.find_all(name='tr'))
        for i in range(len(tr_list_obj)):
            if i > 0:
                field_count = self.get_tr_field_count(soup, tr_list_obj[i])
                obj[i] = field_count
        if obj is not None:
            max_value = max(obj.values())
            min_value = min(obj.values())
            if max_value - min_value > thre_num:
                is_diff_in_range = False
        return is_diff_in_range

    # tr的字段个数如果相差10倍，则认为这个tr可能是嵌套（tr外面的tr）, 则认为是异常tr,不参与计算
    # tr的字段个数，如果和别的不同，则是合并单元格，这种tr去掉
    def remove_except_tr_in_table(self, soup, tr_list_obj):
        # tr_list_obj = table_obj.find_all(name='tr')
        # 排查表格末尾是合并单元格的情况
        last_record_field_count = self.get_tr_field_count(soup, tr_list_obj[len(tr_list_obj) - 2])
        # 去除 相差10倍以上的tr，嵌套tr
        remove_index = []
        for i in range(len(tr_list_obj)):
            # if i > 0:
            field_count = self.get_tr_field_count(soup, tr_list_obj[i])
            # tr的字段个数如果相差10倍，则认为这个tr可能是嵌套（tr外面的tr）,不参与计算
            if field_count / last_record_field_count > 10:
                remove_index.append(i)
            # tr字段做了单元格合并
            if field_count < last_record_field_count:
                remove_index.append(i)
        cnt = 0
        for index in remove_index:
            del tr_list_obj[index - cnt]
            cnt += 1
        # 去除 合并单元格
        return tr_list_obj

    # 判断ul下的每个li字段数值是否相同
    def check_eqaul_each_li_field_count(self, ul_obj):
        is_equal = True
        field_count = self.get_dom_field_count(ul_obj.find(name='li'))
        for li in ul_obj.find_all(name='li'):
            pre_field_count = field_count
            field_count = self.get_dom_field_count(li)
            if field_count != pre_field_count:
                is_equal = False
                break
        return is_equal

    # 对同class的所有div下的有效字段个数进行判断，如果超过阈值6，则认为这些div数值不是要采集的数据
    def check_div_field_count_diff_in_range(self, div_obj_list, thre_num):
        is_diff_in_range = True
        obj = {}
        for i in range(len(div_obj_list)):
            field_count = self.get_dom_field_count(div_obj_list[i])
            obj[i] = field_count
        if obj is not None:
            max_value = max(obj.values())
            min_value = min(obj.values())
            if max_value - min_value > thre_num:
                is_diff_in_range = False
        return is_diff_in_range

    # 判断两个元素是否有相同class
    def check_two_dom_has_same_class(self, current_dom_obj, next_dom_obj):
        current_dom_class_name = ""
        next_dom_class_name = ""
        if current_dom_obj.attrs.get("class") != None:
            current_dom_class_name = str(current_dom_obj.attrs.get("class")).lstrip("['").rstrip("']")
        if next_dom_obj.attrs.get("class") != None:
            next_dom_class_name = str(next_dom_obj.attrs.get("class")).lstrip("['").rstrip("']")
        if current_dom_class_name == next_dom_class_name:
            return True
        else:
            return False

    # 将相同class的所有div再进行分组，分组依据为是否为相同parent,且分组后的div个数大于5个
    def split_div_list_into_same_parent(self, div_obj_list):
        div_obj_list_split_list = []
        obj = {}
        obj[div_obj_list[0].parent] = str(0)
        for i in range(1, len(div_obj_list)):
            div_obj = div_obj_list[i]
            if div_obj.parent not in obj:
                obj[div_obj.parent] = str(i)
            else:
                obj[div_obj.parent] = obj[div_obj.parent] + ";" + str(i)
        for key, value in obj.items():
            split_div_obj_list = []
            for index in value.split(";"):
                split_div_obj_list.append(div_obj_list[int(index)])
            if len(split_div_obj_list) > 5:
                div_obj_list_split_list.append(split_div_obj_list)
        return div_obj_list_split_list
