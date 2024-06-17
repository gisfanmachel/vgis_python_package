#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2023/6/27 14:21
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : moneyTools.py
# @Descr   : 
# @Software: PyCharm
import re

import requests

from vgis_utils.vgis_string.stringTools import StringHelper


class MoneyHelper:
    def __int__(self):
        pass

    @staticmethod
    # 获取货币的符号、数值等信息
    # 133,988,250 USD 转为 133988250 USD end
    # $1,531,180.00 转换为 1531180.00 $  head
    # 目前考虑三种货币 美元USB   $ 人民币  CNY ¥  欧元EUR  €
    def parse_currency(currency_text):
        currency_unit = None
        currency_value = None
        unit_position = None
        if currency_text is not None and str(currency_text).strip() != "":
            # 获取货币文本里的金额数值
            currency_value = currency_text.upper().replace(",", "").replace(" ", "")
            # currency_value = currency_value.lstrip("$").lstrip("$").lstrip("$")
            # currency_value = currency_value.rstrip("USD").rstrip("CNY").rstrip("EUR")
            currency_value = re.sub(r'[^0-9.]', '', currency_value)

            # 获取货币文本里的币种单位
            currency_value2 = currency_text.upper().replace(",", "").replace(" ", "").replace(".", "")
            is_head_unit = False
            is_end_unit = False
            if len(currency_value2) > 0:
                if not currency_value2[0].isdigit():
                    is_head_unit = True
                if not currency_value2[len(currency_value2) - 1].isdigit():
                    is_end_unit = True
            head_unit = None
            end_unit = None
            if is_head_unit:
                head_unit = ""
                for s in currency_value2:
                    if not s.isdigit():
                        head_unit += s
                    else:
                        break
            if is_end_unit:
                end_unit = ""
                for s in currency_value2:
                    if s.isdigit():
                        continue
                    else:
                        end_unit += s
            currency_unit = head_unit if head_unit is not None else end_unit
            unit_position = "head" if is_head_unit else "end" if is_end_unit else None
        # print(currency_value)
        # print(currency_unit)
        # print(unit_position)
        return currency_value, currency_unit, unit_position

    @staticmethod
    # 将会计财务专用格式转换为数值
    # 1,531,180.00,转为1531180.00
    def deecimal_currency(currency_value):
        # 获取货币文本里的金额数值
        currency_value = currency_value.upper().replace(",", "").replace(" ", "")
        currency_value = re.sub(r'[^0-9.]', '', currency_value)
        # print(currency_value)
        return currency_value

    @staticmethod
    # 将货币数值转换为会计财务专用表达方式
    # 1531180.00 转换为 1,531,180.00
    def thousand_sep_currency(currency_value):
        if currency_value is not None and str(currency_value) != "" and "," not in str(currency_value):
            currency_value = "{:,}".format(float(currency_value))
            # print(currency_value)
        else:
            currency_value = ""
        return currency_value

    @staticmethod
    # 将货币数值转换为会计财务专用表达方式，并增加币种单位
    # 1531180.00 转换为 1,531,180.00
    def thousand_sep_currency_add_unit(currency_value, currency_unit, unit_position):
        if currency_value is not None and str(currency_value) != "" and "," not in str(currency_value):
            currency_value = "{:,}".format(float(currency_value))
            # print(currency_value)
        else:
            currency_value = ""
        if unit_position is not None:
            if unit_position == "head":
                currency_value = currency_unit + currency_value
            if unit_position == "end":
                currency_value = currency_value + " " + currency_unit
        # print(currency_value)
        return currency_value

    @staticmethod
    # 根据币种中文获取币种英文
    def getCurrencyUnitByCname(currencyUnitCname):
        currencyUnit = "USD,$"
        for unit in ["人民币,CNY,¥", "美元,USD,$", "欧元,EUR,€"]:
            if currencyUnitCname == unit.split(",")[0]:
                currencyUnit = unit.split(",")[1] + "," + unit.split(",")[2]
        return currencyUnit

    @staticmethod
    def get_end_position_curreny_unit(current_unit):
        currencyUnit = "USB"
        if StringHelper.is_contains_chinese(current_unit):
            currencyUnit = MoneyHelper.getCurrencyUnitByCname(current_unit)[0]
        else:
            if len(current_unit) == 0:
                for unit in ["人民币,CNY,¥", "美元,USD,$", "欧元,EUR,€"]:
                    if current_unit == unit.split(",")[2]:
                        currencyUnit = unit.split(",")[1]
        return currencyUnit

    @staticmethod
    # USD 10, 714,018 这种不合规范的转换位置  为10,714,018 USD
    def changeCurrencyUnitPostion(currencyStr):
        currencyStrReturn = currencyStr
        currencyEn = StringHelper.get_en_in_str(currencyStr)
        if currencyStr.find(currencyEn) == 0:
            currencyStrReturn = currencyStr.lstrip(currencyEn) + " " + currencyEn
        return currencyStrReturn

    @staticmethod
    # 根据币种获取币种位置
    def getCurrencyUnitPositionByUnit(currencyUnit):
        if StringHelper.is_contains_chinese(currencyUnit):
            currencyUnit = MoneyHelper.getCurrencyUnitByCname(currencyUnit)[0]
        position = "head"
        if len(currencyUnit) == 3:
            position = "end"
        return position

    @staticmethod
    # 实时汇率转换(其他币种转换未美元)
    def getConvertAmount(from_currency, to_currency, amount):
        convert_amount = 0.0
        url = 'https://api.exchangerate-api.com/v4/latest/USD'
        converter = RealTimeCurrencyConverter(url)
        # (converter.convert('CNY','USD',100))
        convert_amount = converter.convert(from_currency, to_currency, amount)
        return convert_amount

    # 相对于美元的转换汇率
    @staticmethod
    def getConvertRateByBaseUSD(from_currency):
        url = 'https://api.exchangerate-api.com/v4/latest/USD'
        converter = RealTimeCurrencyConverter(url)
        convert_rate = converter.get_rate(from_currency)
        return convert_rate



    @staticmethod
    # 获取货币的符号、数值等信息
    # 133,988,250 USD 转为 133988250 USD end
    # $1,531,180.00 转换为 1531180.00 $  head
    # 目前考虑三种货币 美元USB   $ 人民币  CNY ¥  欧元EUR  €
    def parse_currency(currency_text):
        currency_unit = None
        currency_value = None
        unit_position = None
        if currency_text is not None and str(currency_text).strip() != "":
            # 获取货币文本里的金额数值
            currency_value = currency_text.upper().replace(",", "").replace(" ", "")
            # currency_value = currency_value.lstrip("$").lstrip("$").lstrip("$")
            # currency_value = currency_value.rstrip("USD").rstrip("CNY").rstrip("EUR")
            currency_value = re.sub(r'[^0-9.]', '', currency_value)

            # 获取货币文本里的币种单位
            currency_value2 = currency_text.upper().replace(",", "").replace(" ", "").replace(".", "")
            is_head_unit = False
            is_end_unit = False
            if len(currency_value2) > 0:
                if not currency_value2[0].isdigit():
                    is_head_unit = True
                if not currency_value2[len(currency_value2) - 1].isdigit():
                    is_end_unit = True
            head_unit = None
            end_unit = None
            if is_head_unit:
                head_unit = ""
                for s in currency_value2:
                    if not s.isdigit():
                        head_unit += s
                    else:
                        break
            if is_end_unit:
                end_unit = ""
                for s in currency_value2:
                    if s.isdigit():
                        continue
                    else:
                        end_unit += s
            currency_unit = head_unit if head_unit is not None else end_unit
            unit_position = "head" if is_head_unit else "end" if is_end_unit else None
        # print(currency_value)
        # print(currency_unit)
        # print(unit_position)
        return currency_value, currency_unit, unit_position

    @staticmethod
    # 将会计财务专用格式转换为数值
    # 1,531,180.00,转为1531180.00
    def deecimal_currency(currency_value):
        # 获取货币文本里的金额数值
        currency_value = currency_value.upper().replace(",", "").replace(" ", "")
        currency_value = re.sub(r'[^0-9.]', '', currency_value)
        # print(currency_value)
        return currency_value

    @staticmethod
    # 将货币数值转换为会计财务专用表达方式
    # 1531180.00 转换为 1,531,180.00
    def thousand_sep_currency(currency_value):
        if currency_value is not None and str(currency_value) != "" and "," not in str(currency_value):
            currency_value = "{:,}".format(float(currency_value))
            # print(currency_value)
        else:
            currency_value = ""
        return currency_value

    @staticmethod
    # 将货币数值转换为会计财务专用表达方式，并增加币种单位
    # 1531180.00 转换为 1,531,180.00
    def thousand_sep_currency_add_unit(currency_value, currency_unit, unit_position):
        if currency_value is not None and str(currency_value) != "" and "," not in str(currency_value):
            currency_value = "{:,}".format(float(currency_value))
            # print(currency_value)
        else:
            currency_value = ""
        if unit_position is not None:
            if unit_position == "head":
                currency_value = currency_unit + currency_value
            if unit_position == "end":
                currency_value = currency_value + " " + currency_unit
        # print(currency_value)
        return currency_value

    @staticmethod
    # 根据币种中文获取币种英文
    def getCurrencyUnitByCname(currencyUnitCname):
        currencyUnit = "USD,$"
        for unit in ["人民币,CNY,¥", "美元,USD,$", "欧元,EUR,€"]:
            if currencyUnitCname == unit.split(",")[0]:
                currencyUnit = unit.split(",")[1] + "," + unit.split(",")[2]
        return currencyUnit

    @staticmethod
    def get_end_position_curreny_unit(current_unit):
        currencyUnit = "USB"
        if StringHelper.is_contains_chinese(current_unit):
            currencyUnit = MoneyHelper.getCurrencyUnitByCname(current_unit)[0]
        else:
            if len(current_unit) == 0:
                for unit in ["人民币,CNY,¥", "美元,USD,$", "欧元,EUR,€"]:
                    if current_unit == unit.split(",")[2]:
                        currencyUnit = unit.split(",")[1]
        return currencyUnit

    @staticmethod
    # USD 10, 714,018 这种不合规范的转换位置  为10,714,018 USD
    def changeCurrencyUnitPostion(currencyStr):
        currencyStrReturn = currencyStr
        currencyEn = StringHelper.get_en_in_str(currencyStr)
        if currencyStr.find(currencyEn) == 0:
            currencyStrReturn = currencyStr.lstrip(currencyEn) + " " + currencyEn
        return currencyStrReturn

    @staticmethod
    # 根据币种获取币种位置
    def getCurrencyUnitPositionByUnit(currencyUnit):
        if StringHelper.is_contains_chinese(currencyUnit):
            currencyUnit = MoneyHelper.getCurrencyUnitByCname(currencyUnit)[0]
        position = "head"
        if len(currencyUnit) == 3:
            position = "end"
        return position

    @staticmethod
    # 实时汇率转换(其他币种转换未美元)
    def getConvertAmount(from_currency, to_currency, amount):
        convert_amount = 0.0
        url = 'https://api.exchangerate-api.com/v4/latest/USD'
        converter = RealTimeCurrencyConverter(url)
        # (converter.convert('CNY','USD',100))
        convert_amount = converter.convert(from_currency, to_currency, amount)
        return convert_amount


    # 相对于美元的转换汇率
    @staticmethod
    def getConvertRateByBaseUSD(from_currency):
        url = 'https://api.exchangerate-api.com/v4/latest/USD'
        converter = RealTimeCurrencyConverter(url)
        convert_rate = converter.get_rate(from_currency)
        return convert_rate

class RealTimeCurrencyConverter():
    def __init__(self, url):
        self.data = requests.get(url).json()
        self.currencies = self.data['rates']

    def convert(self, from_currency, to_currency, amount):
        initial_amount = amount
        if from_currency != 'USD':
            amount = amount / self.currencies[from_currency]

            # limiting the precision to 4 decimal places
        amount = round(amount * self.currencies[to_currency], 4)
        return amount

    def get_rate(self, from_currency):
        rate = 1.0
        if from_currency != 'USD':
            rate = self.currencies[from_currency]
        return rate