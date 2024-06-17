#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/7/18 14:54
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : mathTools.py
# @Descr   : 
# @Software: PyCharm
import re


class MathHelper:
    def __int__(self):
        pass
 # 乘除
    @staticmethod
    def __mu_di(formula):
        if "*" in formula:
            a, b = formula.split("*")
            a = float(a)
            b = float(b)
            formula = float(a) * float(b)
            return formula
        if "/" in formula:
            a, b = formula.split("/")
            a = float(a)
            b = float(b)
            formula = float(a) / float(b)
            return formula
        else:
            print("乘除函数符号错误")

    # 加减
    @staticmethod
    def __add_Sub(num):
        lst_num = re.findall("[-+]?[0-9]+\.?[0-9]*", num)
        ##匹配数字可以包含或不包含小数点后面和前面的正负数
        count = 0
        for i in lst_num:
            count += float(i)
        return count

    ##去符号
    @staticmethod
    def __degbug(num):
        num = num.replace("--", "+")
        num = num.replace("-+", "-")
        num = num.replace("++", "+")
        num = num.replace("+-", "-")
        return num

    # 计算
    @staticmethod
    def __calculate(formula):
        # formula = str(formula)
        # print(type(formula))
        while True:
            tmp = re.search("[0-9]+\.?[0-9]*[*/][+-]?[0-9]+\.?[0-9]*", formula)  ###找出第一个乘除，后面循环全部替换为浮点数
            if tmp:
                tmp = tmp.group()
                tmp2 = str(MathHelper.__mu_di(tmp))
                formula = formula.replace(tmp, tmp2)
                # tmp = re.search("[0-9]+\.?[0-9]*[*/][+-]?[0-9]+\.?[0-9]*",formula).group()
            else:
                break
        formula1 = MathHelper.__degbug(formula)
        formula2 = MathHelper.__add_Sub(formula1)
        return formula2

    # 括号内计算
    @staticmethod
    def __No_brackets(formula):
        while True:
            innum = re.search(r'\([^()]+\)', formula)
            ###匹配第一个没有内部括号的括号内函数，后面循环全部替换为浮点数
            if innum:
                tmp = innum.group()
                tmp2 = MathHelper.__calculate(tmp)
                formula = formula.replace(tmp, str(tmp2))
            else:
                break
        return formula

    # 解析自然表达式里的公式并进行计算出结果
    @staticmethod
    def exp_mian(formula):
        print("计算表达式为：{}".format(formula))
        formula = formula.replace(" ", "")
        formula_tmp1 = MathHelper.__No_brackets(formula)
        result_exp = MathHelper.__calculate(formula_tmp1)
        return result_exp

if __name__ == '__main__':
    hanshu = " 1 - 2 *  (60-30 +(-40/5) * (9-2*5/3 + 7 /3*99/4*2998 +10 * 568/14 ))"
    s1 = MathHelper.exp_mian(hanshu)
    print(s1)

    hanshu = " 1 - 0.4 * (1-0.8)+0.8*0.2"
    s1 = MathHelper.exp_mian(hanshu)
    print(s1)

    hanshu = "0.8*(1 - 0.4)+0.1*(1-0.5)+0.1*0.56"
    s1 = MathHelper.exp_mian(hanshu)
    print(s1)

    hanshu = "0.8(1 - 0.4)"
    s1 = MathHelper.exp_mian(hanshu)
    print(s1)

    hanshu = "0.8*(1 - 0.4)"
    s1 = MathHelper.exp_mian(hanshu)
    print(s1)
