"""
#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
@Project :pythonCodeSnippet
@File    :encrptionTools.py
@IDE     :PyCharm
@Author  :chenxw
@Date    :2023/8/14 15:13
@Descr:   加解密
"""

import base64
import binascii
import logging
import re
import traceback

from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
from cryptography.fernet import Fernet




# Fernet加解密
class FernetEncryption:
    def __init__(self, fernet_key):
        # self.fernet_key== Fernet.generate_key()
        # self.fernet_key = b'uNl-LfGm6NKDQ1Uz9azZIEEzYnaLz68gz0UzaQvYFIY='
        self.fernet_key = fernet_key

    def encrypt(self, txt):
        try:

            # convert integer etc to string first
            txt = str(txt)
            # get the key from settings
            cipher_suite = Fernet(self.fernet_key)  # key should be byte
            #    　　 # #input should be byte, so convert the text to byte
            encrypted_text = cipher_suite.encrypt(txt.encode('utf-8'))
            # encode to urlsafe base64 format
            encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode("utf-8")
            return encrypted_text
        except Exception as e:
            # log the error if any
            logging.getLogger("error_logger").error(traceback.format_exc())
            return None

    def decrypt(self, txt):
        try:
            # base64 decode
            txt = base64.urlsafe_b64decode(txt)
            cipher_suite = Fernet(self.fernet_key)
            decoded_text = cipher_suite.decrypt(txt).decode("utf-8")
            return decoded_text
        except Exception as e:
            # log the error
            logging.getLogger("error_logger").error(traceback.format_exc())
            return None


# AES加解密
class AESEncryption:

    def __init__(self, aes_key):
        # self.aes_iv = '1234567887654321'
        # self.aes_key = 'miyaovgis0704gis'
        self.aes_key = aes_key

    # 创建AES加密对象
    # 用创建好的加密对象，对明文进行加密
    # 把加密好的密文用base64编码
    # 把字符串解码成字符串
    # 将明文用AES加密
    def AES_en(self, data):
        # 将长度不足16字节的字符串补齐
        # if len(data) < 16:
        #     data = pad(data)
        data = pad(data.encode("utf-8"), 16, style='pkcs7')
        # 创建加密对象
        # AES_obj = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
        AES_obj = AES.new(self.aes_key.encode("utf-8"), AES.MODE_ECB)
        # 完成加密
        AES_en_str = AES_obj.encrypt(data)
        # 用base64编码一下
        AES_en_str = base64.b64encode(AES_en_str)
        # 最后将密文转化成字符串
        AES_en_str = AES_en_str.decode("utf-8")
        return AES_en_str

    # 解密是加密的逆过程，按着加密代码的逆序很容易就能写出#
    # 将密文字符串重新编码成bytes类型
    # 将base64编码解开
    # 创建AES解密对象
    # 用解密对象对密文解密
    # 将补齐的空格用strip（）函数除去
    # 将明文解码成字符串
    def AES_de(self, data):
        # 解密过程逆着加密过程写
        # 将密文字符串重新编码成二进制形式
        data = data.encode("utf-8")
        # 将base64的编码解开
        data = base64.b64decode(data)
        # 创建解密对象
        # AES_de_obj = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
        AES_de_obj = AES.new(self.aes_key.encode("utf-8"), AES.MODE_ECB)
        # 完成解密
        AES_de_str = AES_de_obj.decrypt(data)
        # 去掉字符串开头的\x
        AES_de_str = self.handle_x_str(AES_de_str.decode("utf-8"))
        # 去掉字符串末尾的\r
        AES_de_str = AES_de_str.rstrip("\r")
        return AES_de_str

    # 去掉字符串里的\x开头的特殊字符
    def handle_x_str(self, content):
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


# RSA加解密
class RSAEncryption:
    def __init__(self, private_key, public_key):
        self.private_key = private_key
        self.public_key = public_key

    # 在原来字符的基础上要增加前后缀
    def read_public_key(self):
        public_key = "-----BEGIN PUBLIC KEY-----\n{}\n-----END PUBLIC KEY-----".format(self.public_key)
        return public_key.encode('utf-8')

    # 在原来字符的基础上要增加前后缀
    def read_private_key(self):
        private_key = "-----BEGIN RSA PRIVATE KEY-----\n{}\n-----END RSA PRIVATE KEY-----".format(self.private_key)
        return private_key.encode('utf-8')

    # ------------------------加密------------------------
    def encryption(self, text: str):
        public_key_bytes = self.read_public_key()
        # 字符串指定编码（转为bytes）
        text = text.encode('utf-8')
        # 构建公钥对象
        cipher_public = PKCS1_v1_5.new(RSA.importKey(public_key_bytes))
        # 加密（bytes）
        # 加密时支持的最大字节数与证书有一定关系。加密时支持的最大字节数：证书位数/8 -11（比如：2048位的证书，支持的最大加密字节数：2048/8 - 11 = 245）
        # # 1024位的证书，加密时最大支持117个字节，解密时为128；
        # 2048位的证书，加密时最大支持245个字节，解密时为256。
        # # 如果需要加密的字节数超出证书能加密的最大字节数，此时就需要进行分段加密。
        text_encrypted = cipher_public.encrypt(text)
        # base64编码，并转为字符串
        text_encrypted_base64 = base64.b64encode(text_encrypted).decode()
        return text_encrypted_base64

    # ------------------------解密------------------------
    def decryption(self, text_encrypted_base64: str):
        private_key_bytes = self.read_private_key()
        # 字符串指定编码（转为bytes）
        text_encrypted_base64 = text_encrypted_base64.encode('utf-8')
        # base64解码
        text_encrypted = base64.b64decode(text_encrypted_base64)
        # 构建私钥对象
        cipher_private = PKCS1_v1_5.new(RSA.importKey(private_key_bytes))
        # 解密（bytes）
        text_decrypted = cipher_private.decrypt(text_encrypted, 0)
        # 解码为字符串
        text_decrypted = text_decrypted.decode()
        return text_decrypted


# 字符串和十六进制互转
class StringHexMutualConvertion:
    def __init__(self):
        pass

    # 字符串转十六进制
    @staticmethod
    def convert_str_to_hex(content):
        encode_str = str(binascii.b2a_hex(content.encode())).lstrip("b'").rstrip("'")
        return encode_str

    # 十六进制转字符串
    @staticmethod
    def convert_hex_to_str(content):
        decode_str = binascii.a2b_hex(content).decode("utf-8")
        return decode_str


if __name__ == "__main__":
    # 测试Fernet加解密
    print("测试Fernet加解密")
    fernet_key = b'uNl-LfGm6NKDQ1Uz9azZIEEzYnaLz68gz0UzaQvYFIY='
    fernetEncryption = FernetEncryption(fernet_key)
    txt = "{\"username\":\"dongf\",\"password\":\"admin\",\"verifcation\":\"2418H1\"}"
    print("原始字符串:{}".format(txt))
    eny_txt = fernetEncryption.encrypt(txt)
    print("加密后字符串:{}".format(eny_txt))
    dey_txt = fernetEncryption.decrypt(eny_txt)
    print("解密后字符串:{}".format(dey_txt))

    print(
        "---------------------------------------------------------------------------------------------------------------------")
    # 测试AES加解密
    print("测试AES加解密")
    aes_key = 'miyaovgis0704gis'
    aESEncryption = AESEncryption(aes_key)
    data = "{\"custom_name\":\"乐强\",\"pre_insurance_policy_number\":\"TYII2019110200000040094221257901526433ee237eee\",\"sub_insurance_policy_number\":\"23CRU-AP-OP-RB-054299904712579r15265ee3ee7e3ee\",\"insured_name\":\"CHINAOIL (HONG KONG) CORPORATION LIMITED\",\"invoice_contract_nos\":\"CR-P-225043-1\",\"subject_matter\":\"Banoco Arab Medium\",\"packing_quanlity\":\"500,000 BBL ± 5 %\",\"insured_amount\":\"44,453,750 USD\",\"pre_insurance_date\":\"2023-02-28\",\"per_conveyance\":\"油轮\",\"from_port\":\"RAS TANURA, SAUDI ARABIA\",\"to_port\":\"MADE ISLAND, MYANMAR\",\"sailing_date\":\"03/01/2023 - 03/05/2023\",\"insured_date\":\"2023-02-27\",\"applicant_tel\":\"\",\"insurer_name\":\"人保\",\"insurer_tel\":\"65053839\",\"insure_date\":\"2023-02-28\",\"insurance_target_type\":\"联油\",\"vessel_age\":\"2022\",\"vessel_name\":\"HELLAS FOS\",\"vessel_registry\":\"GREECE\",\"at_port\":\"无\",\"claim_payable_at\":\"北京\",\"insured_conditions\":\"ICCA\",\"insured_additional\":\"INSTITUTE STRIKE CLAUSES (CARGO) AND INSTITUTE WAR CLAUSES (CARGO)\"}"
    print("原始字符串:{}".format(data))
    data = aESEncryption.AES_en(data)
    print("加密后字符串:{}".format(data))
    data = aESEncryption.AES_de(data)
    print("解密后字符串:{}".format(data))

    print(
        "---------------------------------------------------------------------------------------------------------------------")
    # 测试RSA加解密
    print("测试RSA加解密")
    public_key = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCqK8UhcyWz1W7/vxDl+2CX32+cM/iGwW4qabjoYBarizlY0Fiv/bGLAePhStAO4UYoG6P15KluAoFaghTMeWLfu4Ev4ryqNLjW1jL56MuUZGWEPJzbFoVZdTVq5Q3E2u4+lRHWrnOm4AvBuufN6j8+jsQyf96uWLrx5opVVWo6KQIDAQAB"
    private_key = "MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAKorxSFzJbPVbv+/EOX7YJffb5wz+IbBbippuOhgFquLOVjQWK/9sYsB4+FK0A7hRigbo/XkqW4CgVqCFMx5Yt+7gS/ivKo0uNbWMvnoy5RkZYQ8nNsWhVl1NWrlDcTa7j6VEdauc6bgC8G6583qPz6OxDJ/3q5YuvHmilVVajopAgMBAAECgYAF3u61IbjaRHHI5vmZRZvmgXHjTLO1SnUXh4A2nCIMFwiKdN2qbLE0X4NSIXeeG82E0rdMY3Ao+HMoATbgewubJ/FR97pqD4Q1VBXKh8Q8Bz36fAH6rGgkqjxcQNroJ7hjjoI1l5VE1HCIcFs3j/UU9maOvDtHco5IaYaDFI3gFQJBAOTqrkHiEx+tT9Yg8B4uQVLc9GXi9RM7qZYmBmSlEAfB2awCI09Uc2D2zQL39Go7zeU5zDxEVoy3zYfL3v1Q7TMCQQC+TdOY4oout2tXIFkZOAMUBguYLIR7qnxPtyKxpLbKu7RnySaLS4nOaTVhz+35UR75FBCTw5fJjUd9xqi4ryMzAkEAxPW3ITCnS6YO/yov74fU5Lr//Xoda4L2Ex58ebQb6tC7vOfKAcOj0lYHZvp47b6vFP953pDd9w1eZezf3Az5SQJAeNoNvTJoVICQvzTAwF4svkOUi2ACBlLfPPRtKOkUWCzZxWsdeipPanCvwNz+IG1ewQj3+g6lTw7UTtChBx/ZtwJBALz9OTLv5VGJGwWc/T9KozfkJRRLj/hP3nKe+qjwyzOvRJET/f2NqQMNu4t1O7A4xSkA/3WHKiaREKVhpeAJyGU="
    rSAEncryption = RSAEncryption(private_key, public_key)
    text = "{\"username\":\"dongf\",\"password\":\"admin\",\"verifcation\":\"2418H1\"}"
    print("原始字符串:" + text)
    text_encrypted_base64 = rSAEncryption.encryption(text)
    print('加密后字符串:' + text_encrypted_base64)
    text_decrypted = rSAEncryption.decryption(text_encrypted_base64)
    print('解密后字符串:' + text_decrypted)
