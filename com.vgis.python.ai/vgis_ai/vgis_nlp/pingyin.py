# -*- coding: utf-8 -*-
"""
===================================
#!/usr/bin/python3.9
@Author: chenxw
@Email : gisfanmachel@gmail.com
@File: pingyin.py
@Date: Create in 2021/8/30 18:40
@Description:提取中文的拼音
@ Software: PyCharm
===================================
"""
import os.path


class PinYinConvert(object):
    def __init__(self):
        self.word_dict = {}

    def load_word(self, dict_file):
        self.dict_file = dict_file
        if not os.path.exists(self.dict_file):
            raise IOError("NotFoundFile")

        with open(self.dict_file) as f_obj:
            for f_line in f_obj.readlines():
                try:
                    line = f_line.split('    ')
                    self.word_dict[line[0]] = line[1]
                except:
                    line = f_line.split('   ')
                    self.word_dict[line[0]] = line[1]

    def hanzi2pinyin(self, string="", firstcode=False):
        result = []
        # if not isinstance(vgis_string, unicode):
        #     vgis_string = vgis_string.decode("utf-8")

        for char in string:
            key = '%X' % ord(char)
            value = self.word_dict.get(key, char)
            outpinyin = str(value).split()[0][:-1].lower()
            if not outpinyin:
                outpinyin = char
            if firstcode:
                result.append(outpinyin[0])
            else:
                result.append(outpinyin)

        return result

    def hanzi2pinyin_split(self, string="", split="", firstcode=False):
        """提取中文的拼音
        @param string:要提取的中文
        @param split:分隔符
        @param firstcode: 提取的是全拼还是首字母？如果为true表示提取首字母，默认为False提取全拼
        """
        result = self.hanzi2pinyin(string=string, firstcode=firstcode)
        return split.join(result)


if __name__ == "__main__":
    test = PinYinConvert()
    test.load_word('vgis_word.data')
    string = "Java程序性能优化-让你的Java程序更快更稳定"
    print("in: %s" % string)
    print("out: %s" % str(test.hanzi2pinyin(string=string)))
    print("out: %s" % test.hanzi2pinyin_split(string=string, split="", firstcode=True))
    print("out: %s" % test.hanzi2pinyin_split(string=string, split="", firstcode=False))