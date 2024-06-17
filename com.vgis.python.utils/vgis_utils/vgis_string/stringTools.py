#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/6/27 14:18
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : stringTools.py
# @Descr   : 
# @Software: PyCharm
import re

import pypinyin


class StringHelper:
    def __int__(self):
        pass

    @staticmethod
    # 得到汉字的首拼音字母
    def get_pinyin(hanzi):
        a = pypinyin.pinyin(hanzi, style=pypinyin.FIRST_LETTER)
        b = []
        for i in range(len(a)):
            b.append(str(a[i][0]).upper())
        c = ''.join(b)
        return c

    @staticmethod
    # 获取字符串里的数字
    def get_number_in_str(input_str):
        return re.findall("\d+", input_str)

    @staticmethod
    # 获取字符串里的第一个数字
    def get_first_num_in_str(input_str):
        return re.findall("\d+", input_str)[0]

    # 获取字符串里的所有数字
    @staticmethod
    def get_complete_number_in_str(input_str):
        return re.findall('-?\d+.?\d+', input_str)

    @staticmethod
    # 获取字符串里的英文
    def get_en_in_str(input_str):
        en_str = re.sub("[\u4e00-\u9fa5\0-9\,\。]", "", input_str)
        return en_str

    @staticmethod
    # 检验字符串是否含有中文字符
    def is_contains_chinese(strs):
        for _char in strs:
            if '\u4e00' <= _char <= '\u9fa5':
                return True
        return False

    @staticmethod
    # 获取字符串里的中文
    def get_cn_in_str(input_str):
        str_result = re.findall("[\u4e00-\u9fa5]", input_str)
        str_return = ""
        for one in str_result:
            str_return = str_return + one
        return str_return

    # 获取两个字符串中间的字符串
    @staticmethod
    def get_str_btw(s, f, b):
        par = s.partition(f)
        return (par[2].partition(b))[0][:]

    @staticmethod
    # 将字符串里的中文转为首写拼音
    def convert_hanzi_to_pinyin_in_str(input_str):
        str_result = re.findall("[\u4e00-\u9fa5]", input_str)
        str_return = ""
        replace_list = []
        for hanzi in str_result:
            pinyin = StringHelper.get_pinyin(hanzi)
            replace_list.append({"hanzi": hanzi, "pinyin": pinyin})
        for replace in replace_list:
            input_str = input_str.replace(replace.get("hanzi"), replace.get("pinyin"))
        if len(re.findall("[\u4e00-\u9fa5]", input_str)) == 0:
            return input_str
        else:
            StringHelper.convert_hanzi_to_pinyin_in_str(input_str)

    @staticmethod
    # 去掉字符串里的\x开头的特殊字符
    def handle_x_str(content):
        # 使用unicode-escape编码集，将unicode内存编码值直接存储
        content = content.encode('unicode_escape').decode('utf-8')
        # 利用正则匹配\x开头的特殊字符
        result = re.findall(r'\\x[a-f0-9]{2}', content)
        for x in result:
            # 替换找的的特殊字符
            content = content.replace(x, '')
        # 最后再解码
        content = content.encode('utf-8').decode('unicode_escape')
        return content

    @staticmethod
    # 首字母小写
    def decapitalize(string):
        return string[:1].lower() + string[1:]

    @staticmethod
    # 获取字符串里按照指定字符开始的指定长度的子字符串
    def get_sub_str_by_startstr_of_length(input_str, start_str, sub_length):
        return_str = input_str[input_str.index(start_str): input_str.index(start_str) + sub_length]
        return return_str

    @staticmethod
    def is_number(s):
        pattern = r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$'
        return bool(re.match(pattern, s))


if __name__ == '__main__':
    input_str = "中故宫eee中工"
    # input_str = StringHelper.convert_hanzi_to_pinyin_in_str(input_str)
    # # 纯文本
    # #     # 预期运行寿命：5年 ; ≤1.25年
    # #     # 推进剂:86kg ; ≤26kg
    # #     # 码率：高于1×10-5 ; ≤1×10-6 ; 1×10-6 ; 双通道均＞1×10-6
    # #     # 三轴指向精度<0.1(3)  ; ≥0.5°(3)
    # #     # 成像期间光轴指向精度：≤ 0.01o (三轴，3σ)
    # #     # 稳定度：≥310-2/s(3) ; ≥0.01°/S(3)
    # #     # **输出功率：3000W，≤1800W ; >2450W ; ≥320W
    # #     # 蓄电池结构块:8个 ;  ≤4个
    # #     # 蓄电池组容量：≤10Ah ; 60Ah
    # #     # 每日地面站获取图像最大能力:每日均≥450景（每日14轨） ; 任意一日＜90景
    # #     # X波段数传EIRP：≥28dBW ; ≤25dBW（主备均失效）
    # #     # 存储容量: ≥8Tbits(主+备) ; 0 bit
    # #     # 相机单轨可成像时间:≧10min ; ≤6min
    # #     # 相机全色像元数:12288像元×3片 ; ≤18432 ; 3072像元/谱段×3片 ; ≤4608
    # #     # 分辨率：2 ; ≥4
    # #     # 最大信噪比：≥ 48dB ; ≤23dB ; ≥48 ; ≤24
    # #     # SAR载荷工作模式:3种（滑动聚束、条带、宽幅） ; 失效两种或以上工作模式
    # #     # 后向散射系数:分辨率1~10m, 成像边缘优于-19dB；分辨率25~500m, 成像中心优于-25dB，边缘优于-21dB像 ; 比设计指标恶化3dB
    # #     # 后向散射系数：-23dB~-20dB ; ≥-17dB
    # #     # SAR（通道数：1536）:超过307个通道失效
    # #     # 水色水温扫描仪:≤0.20K(300K时NEΔT)
    # #     # AIS分系统:1天之内收不到报文数据 ; 在24小时内不能收到报文数据 ; 1天内收到的船舶报文总数小于25000条
    # #     # 接收机灵敏度：优于-111dBm ; ≥-103.7dBm
    # #     # 微波散射计: 1） 发射功率低于失效值  2） 内定标值低于失效值  3） 头部不能转动 上述3个条件中有一个满足，分系统失效
    # #     # 校正辐射计:2通道失效 ; 2 ; 1
    # #     # 雷达高度计:Ku或C通道失效 ; 1
    # #     # 空间环境探测器：超过288个子通道的探测精度≥100% ; ≤10% ; 长时间(大于180天)无探测或数值无变化 ; 1 nt ;  超过12个子通道的探测精度≥ 10 nt
    # #     # 风场测量雷达：≥1.0/2.0dB （刈幅远端，风速≥5m/s / 风速=3m/s）
    # #     # 气溶胶探测仪：9个通道中5个以上通道失效  头部扫描镜不能转动  上述2个条件中有一个满足，该载荷失效 4个通道中2个以上通道失效，该载荷失效
    # #     # 中能粒子载荷：输出为1 ; 输出为0 ; 2.4±0.5V ; ＜1.2V ; 0.2~0.3A
    # #     # 磁力仪：（1）VFM矢量磁力仪单元传感器无法正常加电工作；和/或 （2）VFM矢量磁力仪单元电子学箱主备份均无法正常加电和/或无法输出数据。
    # #     # (1) ASC高精度星敏感器单元3个镜头单元均无法正常加电；和/或 (2) ASC高精度星敏感器单元高精度星敏感器电子学箱无法正常加电工作
    # input_str = "2.4±0.5V"
    # input_str = StringHelper.get_complete_number_in_str(input_str)
    # print(input_str)
    # print(StringHelper.get_sub_str_by_startstr_of_length(input_str, "eee", 4))\
    # ttt = "23.34"
    # print(StringHelper.is_number(ttt))
    # ttt = "0.34"
    # print(StringHelper.is_number(ttt))
    # ttt = "0.0"
    # print(StringHelper.is_number(ttt))
    # ttt = "13"
    # print(StringHelper.is_number(ttt))
    # ttt = "中国"
    # print(StringHelper.is_number(ttt))
    # ttt = "中国4434"
    # print(StringHelper.is_number(ttt))
    tt='温工二万五eee'
    print(StringHelper.get_pinyin(tt))
