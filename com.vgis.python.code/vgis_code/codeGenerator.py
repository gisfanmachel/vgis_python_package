#!/usr/bin/python3.9
# -*- coding: utf-8 -*-
# @Time    :  2022/12/18 20:31
# @Author  : chenxw
# @Email   : gisfanmachel@gmail.com
# @File    : codeGenerator.py
# @Descr   : 代码生成器
# 生成django开发需要的代码
# 生成单文件调用传参
# @Software: PyCharm

# 生成并打印命令行参数
import json

from vgis_database.pgTools import PgHelper
# from vgis_database import PgHelper
from vgis_encrption.encrptionTools import AESEncryption, StringHexMutualConvertion


class BuildCommand:
    # 初始化
    def __init__(self, args=None):
        self.args = args

    # 生成并打印命令行参数
    # linux系统对特殊字符在命令行执行的问题，对传递的字符串做了格式转换成十六进制，在接收端需要还原
    def make_command_str(self):
        command_str = ""
        tab_str = "\t"
        line_break_str = "\r\n"
        var_name_array = self.args.get("var_name_list").split(";")
        var_anno_array = self.args.get("var_anno_list").split(";")
        var_value_array = self.args.get("var_value_list").split(";")
        var_long_option_array = self.args.get("var_long_option_list").split(";")
        var_short_opt_array = self.args.get("var_short_opt_list").split(":")
        command_str += "import getopt"
        command_str += line_break_str
        command_str += "import sys"
        command_str += line_break_str
        command_str += line_break_str
        for i in range(len(var_name_array)):
            command_str += "# {}".format(var_anno_array[i])
            command_str += line_break_str
            command_str += "{} = \"\"".format(var_name_array[i])
            command_str += line_break_str
        command_str += line_break_str
        command_str += "# 构建并获取命令行的动态参数，赋值给全局变量"
        command_str += line_break_str
        command_str += "def build_command_params(argv):"
        command_str += line_break_str
        command_str += tab_str + "# 引用全局变量并赋值"
        command_str += line_break_str
        for i in range(len(var_name_array)):
            command_str += "{}global {}".format(tab_str, var_name_array[i])
            command_str += line_break_str
        command_str += "{}try:".format(tab_str)
        command_str += line_break_str
        command_str += "{}{}long_options = [".format(tab_str, tab_str)
        for w in range(len(var_long_option_array)):
            command_str += "\"{}=\"".format(var_long_option_array[w])
            if w < len(var_long_option_array) - 1:
                command_str += ", "
        command_str += "]"
        command_str += line_break_str
        command_str += "{}{}opts, args = getopt.getopt(argv, \"h{}\", long_options)".format(tab_str, tab_str,
                                                                                            self.args.get(
                                                                                                "var_short_opt_list"))
        command_str += line_break_str
        command_str += "{}except getopt.GetoptError:".format(tab_str)
        command_str += line_break_str
        command_str += "{}{}print('命令行动态参数转换有问题,请按以下格式检查：{}".format(tab_str, tab_str,
                                                                                        self.args.get("py_file_name"))
        for t in range(len(var_name_array)):
            command_str += " -{}<{}>".format(var_short_opt_array[t], var_long_option_array[t])
        command_str += "')"
        command_str += line_break_str
        command_str += "{}{}sys.exit(2)".format(tab_str, tab_str)
        command_str += line_break_str
        command_str += "{}for opt, arg in opts:".format(tab_str)
        command_str += line_break_str
        command_str += "{}{}if opt == '-h':".format(tab_str, tab_str)
        command_str += line_break_str
        command_str += "{}{}{}print('{}".format(tab_str, tab_str, tab_str, self.args.get("py_file_name"))
        for j in range(len(var_name_array)):
            command_str += " -{}<{}>".format(var_short_opt_array[j], var_long_option_array[j])
        command_str += "')"
        command_str += line_break_str
        for k in range(len(var_long_option_array)):
            command_str += "{}{}{}print('{}: {},如{}')".format(tab_str, tab_str, tab_str, var_long_option_array[k],
                                                               var_anno_array[k], var_value_array[k])
            command_str += line_break_str
        command_str += " {}{}{}print('调用命令样例(*****): python3 {}".format(tab_str, tab_str, tab_str,
                                                                              self.args.get("py_file_name"))
        for j in range(len(var_name_array)):
            command_str += " -{} {}".format(var_short_opt_array[j], var_value_array[j])
        command_str += "')"
        command_str += line_break_str
        command_str += "{}{}{}sys.exit()".format(tab_str, tab_str, tab_str)
        command_str += line_break_str
        for j in range(len(var_name_array)):
            command_str += "{}{}elif opt in (".format(tab_str, tab_str)
            command_str += "\"-{}\", \"--{}\"):".format(var_short_opt_array[j], var_long_option_array[j])
            command_str += line_break_str
            command_str += "{}{}{}{} = arg".format(tab_str, tab_str, tab_str, var_name_array[j])
            command_str += line_break_str
        command_str += line_break_str
        for j in range(len(var_name_array)):
            command_str += "{}print('{}{}为  {}'.format({}))".format(tab_str, var_anno_array[j], var_name_array[j],
                                                                     "{}",
                                                                     var_name_array[j])
            command_str += line_break_str
        print(command_str)


# 根据数据表模型，自动生成django相关的类
class BuildDjango:
    def __init__(self, modelFile=None, connection=None, tokenKey=None, postmanFile=None, postmanEncrptFile=None,
                 aesKey=None):
        self.modelFile = modelFile
        self.connection = connection
        self.tokenKey = tokenKey
        self.postmanFile = postmanFile
        self.postmanEncrptFile = postmanEncrptFile
        self.aesKey = aesKey

    # 生成序列器
    def generate_serializer(self):
        row = 0
        for line in open(self.modelFile, encoding="UTF-8"):
            if row % 3 == 0:
                line = line.strip('\n')
                print("#" + self.get_line_by_rowindex_in_modelFile(row + 2) + "序列器")
                print("class {}Serializer(serializers.ModelSerializer):".format(line))
                print("    class Meta:")
                print("        model = {}".format(line))
                print("        fields = \"__all__\"")
            row = row + 1

    # 生成calss
    def generate_classes(self):
        model_list = ""
        serrializer_list = ""
        viewset_list = ""
        row = 0
        for line in open(self.modelFile, encoding="UTF-8"):
            if row % 3 == 0:
                line = line.strip('\n')
                model_list = model_list + line + ","
                serrializer_list = serrializer_list + line + "Serializer" + ","
                viewset_list = viewset_list + line + "ViewSet" + ","
            row = row + 1
        model_list = model_list.rstrip(",")
        serrializer_list = serrializer_list.rstrip(",")
        viewset_list = viewset_list.rstrip(",")
        print(model_list)
        print(serrializer_list)
        print(viewset_list)

    # 生成viewer
    def generate_viewer(self):
        row = 0
        for line in open(self.modelFile, encoding="UTF-8"):
            if row % 3 == 0:
                line = line.strip('\n')
                print("#" + self.get_line_by_rowindex_in_modelFile(row + 2) + "viewer类")
                print("class {}ViewSet(viewsets.ModelViewSet):".format(line))
                print("    queryset = {}.objects.all().order_by('id')".format(line))
                print("    serializer_class = {}Serializer".format(line))
                print("    permission_classes = (IsAuthenticated,)")
                # print("    authentication_classes = (TokenAuthentication,)")
                print("    authentication_classes = (ExpiringTokenAuthentication,)")
            row = row + 1

    # 首字母小写
    def decapitalize(self, string):
        return string[:1].lower() + string[1:]

    # 生成url
    def generate_urls(self):
        row = 0
        for line in open(self.modelFile, encoding="UTF-8"):
            if row % 3 == 0:
                line = line.strip('\n')
                line2 = self.decapitalize(line)
                print("#" + self.get_line_by_rowindex_in_modelFile(row + 2) + "路由器")
                print("router.register(r'{}', {}ViewSet, basename='{}')".format(line2, line, line2))
            row = row + 1

    # 生成postman测试用例
    # 基于已有的基础用例添加业务用例
    def generate_postman(self):
        # postman_json = {}
        #
        # # 读取json文件
        # with open(self.postmanFile, 'r', encoding="UTF-8") as f:
        #     postman_json = json.load(f)

        # info_json ={}
        # info_json["_postman_id"] = "e7bd85f4-a798-427c-9f79-b8c9f50ef307"
        # info_json["name"] = "数据库操作通用项目"
        # info_json["schema"] = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        # info_json["_exporter_id"] = "9849475"
        # postman_json["info"] = info_json

        items_list = []
        item = {}
        item["name"] = "业务操作"
        sub_item_list = []
        row = 0

        with open(self.modelFile, 'r', encoding="UTF-8") as file:
            line = file.readline().strip('\n')
            count_index = 0
            table_index = 0
            while line:
                # 判断是否为表的开始
                if int(count_index / 3) == table_index:
                    # 指定表的第一行，表类名
                    # TtInsuranceProjectMilestone
                    if count_index % 3 == 0:
                        tableClass = line
                    # 指定表的第二行，表英文名
                    # tt_insurance_project_milestone
                    if count_index % 3 == 1:
                        tableEname = line
                    # 指定表的第三行，表中文名
                    # 保险项目里程碑
                    if count_index % 3 == 2:
                        tableCname = line
                        table_index += 1
                        sub_item_obj = {}
                        sub_item_obj["name"] = tableCname
                        single_item_list = []

                        # 列表接口
                        single_item_obj = {}
                        single_item_obj["name"] = "获取{}列表".format(tableCname)
                        single_item_obj["event"] = [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        " var data = JSON.parse(responseBody);\r",
                                        "\r",
                                        "if (data.token) {\r",
                                        "tests[\"Body has token\"] = true;\r",
                                        "postman.setEnvironmentVariable(\"token\", \"Token \"+data.token);\r",
                                        "}\r",
                                        "else {\r",
                                        "tests[\"Body has token\"] = false;\r",
                                        "}"
                                    ],
                                    "type": "text/javascript"
                                }
                            }
                        ]
                        single_item_obj["protocolProfileBehavior"] = {"disableBodyPruning": True}
                        single_item_obj["request"] = {
                            "method": "GET",
                            "header": [
                                {
                                    "key": self.tokenKey,
                                    "value": "{{token}}",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": "",
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            },
                            "url": {
                                "raw": "{{service_host}}/{}".format(self.decapitalize(tableClass)),
                                "host": [
                                    "{{service_host}}"
                                ],
                                "path": [
                                    "{}".format(self.decapitalize(tableClass))
                                ]
                            }
                        }
                        single_item_obj["response"] = []
                        single_item_list.append(single_item_obj)

                        # 新增接口
                        single_item_obj = {}
                        single_item_obj["name"] = "新增{}".format(tableCname)
                        single_item_obj["event"] = [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        " var data = JSON.parse(responseBody);\r",
                                        "\r",
                                        "if (data.token) {\r",
                                        "tests[\"Body has token\"] = true;\r",
                                        "postman.setEnvironmentVariable(\"token\", \"Token \"+data.token);\r",
                                        "}\r",
                                        "else {\r",
                                        "tests[\"Body has token\"] = false;\r",
                                        "}"
                                    ],
                                    "type": "text/javascript"
                                }
                            }
                        ]
                        single_item_obj["request"] = {
                            "method": "POST",
                            "header": [
                                {
                                    "key": self.tokenKey,
                                    "value": "{{token}}",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": self.get_create_or_update_body_content(tableEname),
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            },
                            "url": {
                                "raw": "{{service_host}}/{}/".format(self.decapitalize(tableClass)),
                                "host": [
                                    "{{service_host}}"
                                ],
                                "path": [
                                    "{}".format(self.decapitalize(tableClass)),
                                    ""
                                ]
                            }
                        }
                        single_item_obj["response"] = []
                        single_item_list.append(single_item_obj)

                        # 更新接口
                        single_item_obj = {}
                        single_item_obj["name"] = "更新{}通过编号".format(tableCname)
                        single_item_obj["event"] = [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        " var data = JSON.parse(responseBody);\r",
                                        "\r",
                                        "if (data.token) {\r",
                                        "tests[\"Body has token\"] = true;\r",
                                        "postman.setEnvironmentVariable(\"token\", \"Token \"+data.token);\r",
                                        "}\r",
                                        "else {\r",
                                        "tests[\"Body has token\"] = false;\r",
                                        "}"
                                    ],
                                    "type": "text/javascript"
                                }
                            }
                        ]
                        single_item_obj["request"] = {
                            "method": "PUT",
                            "header": [
                                {
                                    "key": self.tokenKey,
                                    "value": "{{token}}",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": self.get_create_or_update_body_content(tableEname),
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            },
                            "url": {
                                "raw": "{{service_host}}/{}/17/".format(self.decapitalize(tableClass)),
                                "host": [
                                    "{{service_host}}"
                                ],
                                "path": [
                                    "{}".format(self.decapitalize(tableClass)),
                                    "17",
                                    ""
                                ]
                            }
                        }
                        single_item_obj["response"] = []
                        single_item_list.append(single_item_obj)

                        # 获取详情通过编号
                        single_item_obj = {}
                        single_item_obj["name"] = "获取{}详情通过编号".format(tableCname)
                        single_item_obj["event"] = [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        " var data = JSON.parse(responseBody);\r",
                                        "\r",
                                        "if (data.token) {\r",
                                        "tests[\"Body has token\"] = true;\r",
                                        "postman.setEnvironmentVariable(\"token\", \"Token \"+data.token);\r",
                                        "}\r",
                                        "else {\r",
                                        "tests[\"Body has token\"] = false;\r",
                                        "}"
                                    ],
                                    "type": "text/javascript"
                                }
                            }
                        ]
                        single_item_obj["protocolProfileBehavior"] = {"disableBodyPruning": True}
                        single_item_obj["request"] = {
                            "method": "GET",
                            "header": [
                                {
                                    "key": self.tokenKey,
                                    "value": "{{token}}",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": "",
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            },
                            "url": {
                                "raw": "{{service_host}}/{}/17/".format(self.decapitalize(tableClass)),
                                "host": [
                                    "{{service_host}}"
                                ],
                                "path": [
                                    "{}".format(self.decapitalize(tableClass)),
                                    "17",
                                    ""
                                ]
                            }
                        }
                        single_item_obj["response"] = []
                        single_item_list.append(single_item_obj)

                        # 删除通过编号
                        single_item_obj = {}
                        single_item_obj["name"] = "删除{}通过编号".format(tableCname)
                        single_item_obj["event"] = [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        " var data = JSON.parse(responseBody);\r",
                                        "\r",
                                        "if (data.token) {\r",
                                        "tests[\"Body has token\"] = true;\r",
                                        "postman.setEnvironmentVariable(\"token\", \"Token \"+data.token);\r",
                                        "}\r",
                                        "else {\r",
                                        "tests[\"Body has token\"] = false;\r",
                                        "}"
                                    ],
                                    "type": "text/javascript"
                                }
                            }
                        ]
                        single_item_obj["request"] = {
                            "method": "DELETE",
                            "header": [
                                {
                                    "key": self.tokenKey,
                                    "value": "{{token}}",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": "",
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            },
                            "url": {
                                "raw": "{{service_host}}/{}/26/".format(self.decapitalize(tableClass)),
                                "host": [
                                    "{{service_host}}"
                                ],
                                "path": [
                                    "{}".format(self.decapitalize(tableClass)),
                                    "26",
                                    ""
                                ]
                            }
                        }
                        single_item_obj["response"] = []
                        single_item_list.append(single_item_obj)

                        sub_item_obj["item"] = single_item_list
                        sub_item_list.append(sub_item_obj)
                line = file.readline().strip('\n')
                count_index += 1
        item["item"] = sub_item_list

        self.append_json(self.postmanFile, item)
        # items_list.append(item)
        # postman_json["item"].append(item)
        # file = open(self.postmanFile, "w", encoding='utf-8')
        # json.dump(postman_json, file, ensure_ascii=False)
        # file.close()

    # 生成postman测试用例
    # 加密参数
    # 基于已有的基础用例添加业务用例
    def generate_postman_encrpyt(self):
        # postman_json = {}
        #
        # # 读取json文件
        # with open(self.postmanFile, 'r', encoding="UTF-8") as f:
        #     postman_json = json.load(f)

        # info_json ={}
        # info_json["_postman_id"] = "e7bd85f4-a798-427c-9f79-b8c9f50ef307"
        # info_json["name"] = "数据库操作通用项目"
        # info_json["schema"] = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        # info_json["_exporter_id"] = "9849475"
        # postman_json["info"] = info_json

        items_list = []
        item = {}
        item["name"] = "业务操作"
        sub_item_list = []
        row = 0

        with open(self.modelFile, 'r', encoding="UTF-8") as file:
            line = file.readline().strip('\n')
            count_index = 0
            table_index = 0
            while line:
                # 判断是否为表的开始
                if int(count_index / 3) == table_index:
                    # 指定表的第一行，表类名
                    # TtInsuranceProjectMilestone
                    if count_index % 3 == 0:
                        tableClass = line
                    # 指定表的第二行，表英文名
                    # tt_insurance_project_milestone
                    if count_index % 3 == 1:
                        tableEname = line
                    # 指定表的第三行，表中文名
                    # 保险项目里程碑
                    if count_index % 3 == 2:
                        tableCname = line
                        table_index += 1
                        sub_item_obj = {}
                        sub_item_obj["name"] = tableCname
                        single_item_list = []

                        # 列表接口
                        single_item_obj = {}
                        single_item_obj["name"] = "获取{}列表".format(tableCname)
                        single_item_obj["event"] = [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var response_data = JSON.parse(responseBody);\r",
                                        "\r",
                                        "console.log(\"返回结果:\",response_data)\r",
                                        "\r",
                                        "var AES_key= \"" + self.aesKey + "\" //秘钥\r",
                                        "var ECBOptions = {mode: CryptoJS.mode.ECB,padding: CryptoJS.pad.Pkcs7};\r",
                                        "var AesSecert = CryptoJS.enc.Utf8.parse(AES_key);\r",
                                        "var data_dec = CryptoJS.AES.decrypt(response_data.data, AesSecert, ECBOptions)\r",
                                        "var data_dec_str = data_dec.toString(CryptoJS.enc.Utf8)\r",
                                        "console.log(\"解密之后的结果:\",data_dec_str)\r",
                                        ""
                                    ],
                                    "type": "text/javascript"
                                }
                            }
                        ]
                        single_item_obj["protocolProfileBehavior"] = {"disableBodyPruning": True}
                        single_item_obj["request"] = {
                            "method": "GET",
                            "header": [
                                {
                                    "key": self.tokenKey,
                                    "value": "{{token}}",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": "",
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            },
                            "url": {
                                "raw": "{{service_host}}/{}".format(self.decapitalize(tableClass)),
                                "host": [
                                    "{{service_host}}"
                                ],
                                "path": [
                                    "{}".format(self.decapitalize(tableClass))
                                ]
                            }
                        }
                        single_item_obj["response"] = []
                        single_item_list.append(single_item_obj)

                        # 新增接口
                        single_item_obj = {}
                        single_item_obj["name"] = "新增{}".format(tableCname)
                        single_item_obj["event"] = [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var response_data = JSON.parse(responseBody);\r",
                                        "\r",
                                        "console.log(\"返回结果:\",response_data)\r",
                                        "\r",
                                        "var AES_key= \"" + self.aesKey + "\" //秘钥\r",
                                        "var ECBOptions = {mode: CryptoJS.mode.ECB,padding: CryptoJS.pad.Pkcs7};\r",
                                        "var AesSecert = CryptoJS.enc.Utf8.parse(AES_key);\r",
                                        "var data_dec = CryptoJS.AES.decrypt(response_data.data, AesSecert, ECBOptions)\r",
                                        "var data_dec_str = data_dec.toString(CryptoJS.enc.Utf8)\r",
                                        "console.log(\"解密之后的结果:\",data_dec_str)\r",
                                        ""
                                    ],
                                    "type": "text/javascript"
                                }
                            }
                        ]
                        single_item_obj["request"] = {
                            "method": "POST",
                            "header": [
                                {
                                    "key": self.tokenKey,
                                    "value": "{{token}}",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": self.get_create_or_update_body_content_by_encrpt(tableEname),
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            },
                            "url": {
                                "raw": "{{service_host}}/{}/".format(self.decapitalize(tableClass)),
                                "host": [
                                    "{{service_host}}"
                                ],
                                "path": [
                                    "{}".format(self.decapitalize(tableClass)),
                                    ""
                                ]
                            }
                        }
                        single_item_obj["response"] = []
                        single_item_list.append(single_item_obj)

                        # 更新接口
                        single_item_obj = {}
                        single_item_obj["name"] = "更新{}通过编号".format(tableCname)
                        single_item_obj["event"] = [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var response_data = JSON.parse(responseBody);\r",
                                        "\r",
                                        "console.log(\"返回结果:\",response_data)\r",
                                        "\r",
                                        "var AES_key= \"" + self.aesKey + "\" //秘钥\r",
                                        "var ECBOptions = {mode: CryptoJS.mode.ECB,padding: CryptoJS.pad.Pkcs7};\r",
                                        "var AesSecert = CryptoJS.enc.Utf8.parse(AES_key);\r",
                                        "var data_dec = CryptoJS.AES.decrypt(response_data.data, AesSecert, ECBOptions)\r",
                                        "var data_dec_str = data_dec.toString(CryptoJS.enc.Utf8)\r",
                                        "console.log(\"解密之后的结果:\",data_dec_str)\r",
                                        ""
                                    ],
                                    "type": "text/javascript"
                                }
                            }
                        ]
                        single_item_obj["request"] = {
                            "method": "PUT",
                            "header": [
                                {
                                    "key": self.tokenKey,
                                    "value": "{{token}}",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": self.get_create_or_update_body_content_by_encrpt(tableEname),
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            },
                            "url": {
                                "raw": "{{service_host}}/{}/17/".format(self.decapitalize(tableClass)),
                                "host": [
                                    "{{service_host}}"
                                ],
                                "path": [
                                    "{}".format(self.decapitalize(tableClass)),
                                    "17",
                                    ""
                                ]
                            }
                        }
                        single_item_obj["response"] = []
                        single_item_list.append(single_item_obj)

                        # 获取详情通过编号
                        single_item_obj = {}
                        single_item_obj["name"] = "获取{}详情通过编号".format(tableCname)
                        single_item_obj["event"] = [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var response_data = JSON.parse(responseBody);\r",
                                        "\r",
                                        "console.log(\"返回结果:\",response_data)\r",
                                        "\r",
                                        "var AES_key= \"" + self.aesKey + "\" //秘钥\r",
                                        "var ECBOptions = {mode: CryptoJS.mode.ECB,padding: CryptoJS.pad.Pkcs7};\r",
                                        "var AesSecert = CryptoJS.enc.Utf8.parse(AES_key);\r",
                                        "var data_dec = CryptoJS.AES.decrypt(response_data.data, AesSecert, ECBOptions)\r",
                                        "var data_dec_str = data_dec.toString(CryptoJS.enc.Utf8)\r",
                                        "console.log(\"解密之后的结果:\",data_dec_str)\r",
                                        ""
                                    ],
                                    "type": "text/javascript"
                                }
                            }
                        ]
                        single_item_obj["protocolProfileBehavior"] = {"disableBodyPruning": True}
                        single_item_obj["request"] = {
                            "method": "GET",
                            "header": [
                                {
                                    "key": self.tokenKey,
                                    "value": "{{token}}",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": "",
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            },
                            "url": {
                                "raw": "{{service_host}}/{}/17/".format(self.decapitalize(tableClass)),
                                "host": [
                                    "{{service_host}}"
                                ],
                                "path": [
                                    "{}".format(self.decapitalize(tableClass)),
                                    "17",
                                    ""
                                ]
                            }
                        }
                        single_item_obj["response"] = []
                        single_item_list.append(single_item_obj)

                        # 删除通过编号
                        single_item_obj = {}
                        single_item_obj["name"] = "删除{}通过编号".format(tableCname)
                        single_item_obj["event"] = [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var response_data = JSON.parse(responseBody);\r",
                                        "\r",
                                        "console.log(\"返回结果:\",response_data)\r",
                                        "\r",
                                        "var AES_key= \"" + self.aesKey + "\" //秘钥\r",
                                        "var ECBOptions = {mode: CryptoJS.mode.ECB,padding: CryptoJS.pad.Pkcs7};\r",
                                        "var AesSecert = CryptoJS.enc.Utf8.parse(AES_key);\r",
                                        "var data_dec = CryptoJS.AES.decrypt(response_data.data, AesSecert, ECBOptions)\r",
                                        "var data_dec_str = data_dec.toString(CryptoJS.enc.Utf8)\r",
                                        "console.log(\"解密之后的结果:\",data_dec_str)\r",
                                        ""
                                    ],
                                    "type": "text/javascript"
                                }
                            }
                        ]
                        single_item_obj["request"] = {
                            "method": "DELETE",
                            "header": [
                                {
                                    "key": self.tokenKey,
                                    "value": "{{token}}",
                                    "type": "text"
                                }
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": "",
                                "options": {
                                    "raw": {
                                        "language": "json"
                                    }
                                }
                            },
                            "url": {
                                "raw": "{{service_host}}/{}/26/".format(self.decapitalize(tableClass)),
                                "host": [
                                    "{{service_host}}"
                                ],
                                "path": [
                                    "{}".format(self.decapitalize(tableClass)),
                                    "26",
                                    ""
                                ]
                            }
                        }
                        single_item_obj["response"] = []
                        single_item_list.append(single_item_obj)

                        sub_item_obj["item"] = single_item_list
                        sub_item_list.append(sub_item_obj)
                line = file.readline().strip('\n')
                count_index += 1
        item["item"] = sub_item_list

        self.append_json(self.postmanEncrptFile, item)
        # items_list.append(item)
        # postman_json["item"].append(item)
        # file = open(self.postmanFile, "w", encoding='utf-8')
        # json.dump(postman_json, file, ensure_ascii=False)
        # file.close()

    # 读取JSON文件
    def read_json_file(self, file_path):
        with open(file_path, 'r', encoding='UTF-8') as file:
            data = json.load(file)
        return data

    # 获取文件里指定行数的内容
    def get_line_by_rowindex_in_modelFile(self, row_index):
        row = 0
        line = ""
        for line in open(self.modelFile, encoding="UTF-8"):
            if row == row_index:
                line = line.strip('\n')
                break
            row += 1
        return line

    # 写入JSON文件
    def write_json_file(self, file_path, data):
        with open(file_path, 'w', encoding='UTF-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    # 追加JSON内容
    def append_json(self, file_path, new_data):
        # 读取原有的JSON内容
        data = self.read_json_file(file_path)
        # 将新数据追加到原有数据中
        data["item"].append(new_data)
        # 写入更新后的JSON内容
        self.write_json_file(file_path, data)

    def get_create_or_update_body_content(self, tablename):
        return_value = ""
        sql = "select a.attnum,a.attname,concat_ws('',t.typname,SUBSTRING(format_type(a.atttypid,a.atttypmod) from '\(.*\)')) as type,d.description from pg_class c, pg_attribute a , pg_type t, pg_description d where  c.relname = '{}' and a.attnum>0 and a.attrelid = c.oid and a.atttypid = t.oid and  d.objoid=a.attrelid and d.objsubid=a.attnum".format(
            tablename)
        cursor = self.connection.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()
        field_list = []
        field_num = 0
        for record in records:
            obj = {}
            if record[1] != "id":
                obj['attname'] = record[1]
                field_list.append(obj['attname'])
                field_num += 1
        fields_str = ",".join(field_list)
        sql = "select count(*) from pg_class where relname = '{}';".format(tablename)
        cursor.execute(sql)
        record = cursor.fetchone()
        if record[0] == 1:
            sql = "select {} from {} order by id limit 1".format(fields_str, tablename)
            cursor.execute(sql)
            record = cursor.fetchone()
            return_value = "{"
            for index in range(field_num):
                field_name = field_list[index]
                if record is not None:
                    field_value = record[index]
                else:
                    field_value = ""
                field_content = "\r\n    \"{}\": \"{}\",".format(field_name, field_value)
                return_value = return_value + field_content
            return_value = return_value.rstrip(",")
            return_value = return_value + "\r\n}"
        return return_value

    def get_create_or_update_body_content_by_encrpt(self, tablename):
        return_value = ""
        sql = "select a.attnum,a.attname,concat_ws('',t.typname,SUBSTRING(format_type(a.atttypid,a.atttypmod) from '\(.*\)')) as type,d.description from pg_class c, pg_attribute a , pg_type t, pg_description d where  c.relname = '{}' and a.attnum>0 and a.attrelid = c.oid and a.atttypid = t.oid and  d.objoid=a.attrelid and d.objsubid=a.attnum".format(
            tablename)
        cursor = self.connection.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()
        field_list = []
        field_num = 0
        for record in records:
            obj = {}
            if record[1] != "id":
                obj['attname'] = record[1]
                field_list.append(obj['attname'])
                field_num += 1
        fields_str = ",".join(field_list)
        sql = "select count(*) from pg_class where relname = '{}';".format(tablename)
        cursor.execute(sql)
        record = cursor.fetchone()
        if record[0] == 1:
            sql = "select {} from {} order by id limit 1".format(fields_str, tablename)
            cursor.execute(sql)
            record = cursor.fetchone()
            return_value = "{"
            for index in range(field_num):
                field_name = field_list[index]
                if record is not None:
                    field_value = record[index]
                else:
                    field_value = ""
                field_content = "\"{}\": \"{}\",".format(field_name, field_value)
                return_value = return_value + field_content
            return_value = return_value.rstrip(",")
            return_value = return_value + "}"
        aESEncryption = AESEncryption(self.aesKey)
        return_value = aESEncryption.AES_en(return_value)
        return_value = StringHexMutualConvertion.convert_str_to_hex(return_value)
        # "{\r\n    \"data\": \"75705951776675496763713672756b6c55623832574e4e565672797a2f666b5853445a493662707a2b536a63482b5159414c5038717055636156625a32347376616862642f567a454b4773415a52375a786230444b62564637706f545736366c6c6f6766724c4e42703442773134747145466d70316e31427561794c51714f77646b524e793246795558655069317a495843457642773d3d\"\r\n}",
        return "{\r\n    \"data\":\"" + return_value + "\"\r\n}"

    # 生成viewer里增删改查的重载方法模板代码
    def generate_cude_code_in_viewer(self, api_path, table_cname, table_class, not_same_field_cn_list,
                                     not_same_field_en_list):
        tab_str = "\t"
        line_break_str = "\r\n"

        # create方法重载
        create_code_str = "{}# 新增方法重载{}".format(tab_str, line_break_str)
        create_code_str += "{}def create(self, request, *args, **kwargs):{}".format(tab_str, line_break_str)
        create_code_str += "{}{}api_path = \"{}\"{}".format(tab_str, tab_str, api_path, line_break_str)
        create_code_str += "{}{}try:{}".format(tab_str, tab_str, line_break_str)
        create_code_str += "{}{}{}function_title = \"新增{}\"{}".format(tab_str, tab_str, tab_str, table_cname,
                                                                        line_break_str)
        create_code_str += "{}{}{}start = LoggerHelper.set_start_log_info(logger){}".format(tab_str, tab_str, tab_str,

                                                                                            line_break_str)
        tab_str_5s = "\t\t\t\t\t"
        tab_str_4s = "\t\t\t\t"
        tab_str_3s = "\t\t\t"
        need_tab_strs = ""
        if not_same_field_cn_list is not None:
            need_tab_strs = tab_str_4s
            info = ""
            for index in range(len(not_same_field_cn_list)):
                not_same_field_cn = not_same_field_cn_list[index]
                not_same_field_en = not_same_field_en_list[index]
                info += "{} {}".format(not_same_field_cn, not_same_field_en) + ","
            info += " 不能重名"
            create_code_str += "{}{}{}#{}{}".format(tab_str, tab_str, tab_str, info, line_break_str)

            for index in range(len(not_same_field_en_list)):
                not_same_field_en = not_same_field_en_list[index]
                info = "{} = request.data[\"{}\"] if \"{}\" in request.data else None".format(not_same_field_en,
                                                                                              not_same_field_en,
                                                                                              not_same_field_en)
                create_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str, info, line_break_str)

            for index in range(len(not_same_field_en_list)):
                not_same_field_en = not_same_field_en_list[index]
                not_same_field_cn = not_same_field_cn_list[index]
                info = "if {} is not None and len({}.objects.filter({}={})) > 0:".format(not_same_field_en, table_class,
                                                                                         not_same_field_en,
                                                                                         not_same_field_en)
                create_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str, info, line_break_str)
                info = "error_info = \"新增{}里的{}:{{}}已存在，请换个{}\".format({})".format(table_cname,
                                                                                             not_same_field_cn,
                                                                                             not_same_field_cn,
                                                                                             not_same_field_en)
                create_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info, line_break_str)
                info = "res = LoggerHelper.set_end_log_info_in_exception(SysLog,logger, start, api_path,request.auth.user, request,function_title, error_info, None)"
                create_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info, line_break_str)
                create_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, "return Response(res)",
                                                         line_break_str)

            create_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str, "else:", line_break_str)
        else:
            need_tab_strs = tab_str_3s

        create_code_str += "{}{}{}".format(need_tab_strs,
                                           "request.data[\"create_user_id\"] = request.auth.user_id",
                                           line_break_str)
        create_code_str += "{}{}{}".format(need_tab_strs,
                                           "request.data[\"create_time\"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
                                           line_break_str)
        create_code_str += "{}{}{}".format(need_tab_strs,
                                           "request.data[\"modify_user_id\"] = request.auth.user_id",
                                           line_break_str)
        create_code_str += "{}{}{}".format(need_tab_strs,
                                           "request.data[\"modify_time\"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
                                           line_break_str)
        create_code_str += "{}{}{}".format(need_tab_strs,
                                           "super().create(request)",
                                           line_break_str)
        create_code_str += "{}{}{}".format(need_tab_strs,
                                           "LoggerHelper.set_end_log_info(logger, start, api_path, request.auth.user,request,function_title)",
                                           line_break_str)
        create_code_str += "{}{}{}".format(need_tab_strs,
                                           "res = {'success': True,'info': \"{}成功\".format(function_title)}",
                                           line_break_str)
        create_code_str += "{}{}{}".format(need_tab_strs,
                                           "return Response(res)", line_break_str)
        create_code_str += "{}{}{}{}".format(tab_str, tab_str,
                                             "except Exception as exp:", line_break_str)
        create_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str,
                                               "res = LoggerHelper.set_end_log_info_in_exception(SysLog,logger, start, api_path,request.auth.user, request,function_title, None, exp)",
                                               line_break_str)
        create_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str,
                                               "return Response(res)", line_break_str)

        print(create_code_str)

        # update方法重载
        update_code_str = "{}# 更新方法重载{}".format(tab_str, line_break_str)
        update_code_str += "{}def update(self, request, *args, **kwargs):{}".format(tab_str, line_break_str)
        update_code_str += "{}{}api_path = \"{}\"{}".format(tab_str, tab_str, api_path, line_break_str)
        update_code_str += "{}{}try:{}".format(tab_str, tab_str, line_break_str)
        update_code_str += "{}{}{}function_title = \"更新{}\"{}".format(tab_str, tab_str, tab_str, table_cname,
                                                                        line_break_str)
        update_code_str += "{}{}{}start = LoggerHelper.set_start_log_info(logger){}".format(tab_str, tab_str, tab_str,
                                                                                            line_break_str)
        update_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str, "id = kwargs[\"pk\"]", line_break_str)
        if not_same_field_cn_list is not None:
            info = ""
            for index in range(len(not_same_field_cn_list)):
                not_same_field_cn = not_same_field_cn_list[index]
                not_same_field_en = not_same_field_en_list[index]
                info += "{} {}".format(not_same_field_cn, not_same_field_en) + ","
            info += " 不能重名"
            update_code_str += "{}{}{}#{}{}".format(tab_str, tab_str, tab_str, info, line_break_str)

        info = "if len({}.objects.filter(id=id)) > 0:".format(table_class)
        update_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str, info, line_break_str)

        if not_same_field_cn_list is not None:
            for index in range(len(not_same_field_en_list)):
                not_same_field_en = not_same_field_en_list[index]
                info = "old_{} = {}.objects.filter(id=id)[0].{}".format(not_same_field_en, table_class,
                                                                        not_same_field_en)
                update_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info, line_break_str)

        info = "request.data[\"create_user_id\"] = {}.objects.filter(id=id)[0].create_user_id".format(table_class)
        update_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info, line_break_str)
        info = "request.data[\"create_time\"] = {}.objects.filter(id=id)[0].create_time".format(table_class)
        update_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info, line_break_str)
        info = "request.data[\"modify_user_id\"] = request.auth.user_id"
        update_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info, line_break_str)
        info = "request.data[\"modify_time\"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')"
        update_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info, line_break_str)

        if not_same_field_cn_list is not None:
            for index in range(len(not_same_field_en_list)):
                not_same_field_en = not_same_field_en_list[index]
                info = "new_{} = request.data[\"{}\"] if \"{}\" in request.data else None".format(not_same_field_en,
                                                                                                  not_same_field_en,
                                                                                                  not_same_field_en)
                update_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info, line_break_str)

        if not_same_field_cn_list is not None:
            need_tab_strs = tab_str_5s
            for index in range(len(not_same_field_en_list)):
                not_same_field_en = not_same_field_en_list[index]
                not_same_field_cn = not_same_field_cn_list[index]
                info = "if new_{} is not None and old_{} != new_{} and len({}.objects.filter({}=new_{})) > 0:".format(
                    not_same_field_en, not_same_field_en, not_same_field_en, table_class,
                    not_same_field_en,
                    not_same_field_en)
                update_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info, line_break_str)
                info = "error_info = \"更新{}里的{}:{{}}已存在，请换个{}\".format({})".format(table_cname,
                                                                                             not_same_field_cn,
                                                                                             not_same_field_cn,
                                                                                             "new_" + not_same_field_en)
                update_code_str += "{}{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, tab_str, info,
                                                           line_break_str)
                info = "res = LoggerHelper.set_end_log_info_in_exception(SysLog,logger, start, api_path,request.auth.user, request,function_title, error_info, None)"
                update_code_str += "{}{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, tab_str, info,
                                                           line_break_str)
                update_code_str += "{}{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, tab_str,
                                                           "return Response(res)",
                                                           line_break_str)

            update_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, "else:", line_break_str)
        else:
            need_tab_strs = tab_str_4s
        update_code_str += "{}{}{}".format(need_tab_strs,
                                           "super().update(request, *args, **kwargs)",
                                           line_break_str)
        update_code_str += "{}{}{}".format(need_tab_strs,
                                           "LoggerHelper.set_end_log_info(logger, start, api_path, request.auth.user,request,function_title)",
                                           line_break_str)
        update_code_str += "{}{}{}".format(need_tab_strs,
                                           "res = {'success': True,'info': \"{}成功\".format(function_title)}",
                                           line_break_str)
        update_code_str += "{}{}{}".format(need_tab_strs,
                                           "return Response(res)", line_break_str)

        update_code_str += "{}{}{}{}".format(tab_str, tab_str,
                                             "except Exception as exp:", line_break_str)
        update_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str,
                                               "res = LoggerHelper.set_end_log_info_in_exception(SysLog,logger, start, api_path,request.auth.user, request,function_title, None, exp)",
                                               line_break_str)
        update_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str,
                                               "return Response(res)", line_break_str)

        print(update_code_str)

        #  根据编号查询详情方法重载
        getdetail_code_str = "{}# 根据编号查询方法重载{}".format(tab_str, line_break_str)
        getdetail_code_str += "{}def get_object(self, *args, **kwargs):{}".format(tab_str, line_break_str)
        getdetail_code_str += "{}{}api_path = \"{}\"{}".format(tab_str, tab_str, api_path, line_break_str)
        getdetail_code_str += "{}{}try:{}".format(tab_str, tab_str, line_break_str)
        getdetail_code_str += "{}{}{}function_title = \"通过编号获取{}详情\"{}".format(tab_str, tab_str, tab_str,
                                                                                       table_cname,
                                                                                       line_break_str)
        getdetail_code_str += "{}{}{}start = LoggerHelper.set_start_log_info(logger){}".format(tab_str, tab_str,
                                                                                               tab_str,
                                                                                               line_break_str)
        getdetail_code_str += "{}{}{}result = \"\"{}".format(tab_str, tab_str, tab_str,
                                                             line_break_str)
        info = "#更新会进来"
        getdetail_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str, info,
                                                  line_break_str)
        info = "if self.action == \"update\":"
        getdetail_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str, info,
                                                  line_break_str)
        info = "return super().get_object(*args, **kwargs)"
        getdetail_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info,
                                                    line_break_str)
        info = "else:"
        getdetail_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str, info,
                                                  line_break_str)
        info = "id=self.kwargs[\"pk\"]"
        getdetail_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info,
                                                    line_break_str)
        info = "result = super().get_object(*args, **kwargs)"
        getdetail_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info,
                                                    line_break_str)
        info = "LoggerHelper.set_end_log_info(SysLog,logger, start, api_path + str(id), self.request.auth.user,self.request,function_title)"
        getdetail_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info,
                                                    line_break_str)
        info = "return result"
        getdetail_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info,
                                                    line_break_str)
        getdetail_code_str += "{}{}{}{}".format(tab_str, tab_str,
                                                "except Exception as exp:", line_break_str)
        getdetail_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str,
                                                  "res = LoggerHelper.set_end_log_info_in_exception(SysLog,logger, start, api_path,self.request.auth.user, self.request,function_title, None, exp)",
                                                  line_break_str)
        getdetail_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str,
                                                  "return Response(res)", line_break_str)

        print(getdetail_code_str)

        #  list方法重载
        list_code_str = "{}# list方法重载{}".format(tab_str, line_break_str)
        list_code_str += "{}def get_queryset(self, *args, **kwargs):{}".format(tab_str, line_break_str)
        list_code_str += "{}{}api_path = \"{}\"{}".format(tab_str, tab_str, api_path, line_break_str)
        list_code_str += "{}{}try:{}".format(tab_str, tab_str, line_break_str)
        list_code_str += "{}{}{}function_title = \"获取{}列表\"{}".format(tab_str, tab_str, tab_str, table_cname,
                                                                          line_break_str)
        list_code_str += "{}{}{}start = LoggerHelper.set_start_log_info(logger){}".format(tab_str, tab_str, tab_str,
                                                                                          line_break_str)
        info = "# 更新和通过ID获取详情会进来"
        list_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str, info,
                                             line_break_str)
        info = "if \"pk\" in self.kwargs:"
        list_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str, info,
                                             line_break_str)

        info = "return super().get_queryset(*args, **kwargs)"
        list_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info,
                                               line_break_str)
        info = "else:"
        list_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str, info,
                                             line_break_str)
        info = "querysets = super().get_queryset(*args, **kwargs)"
        list_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info,
                                               line_break_str)
        info = "LoggerHelper.set_end_log_info(SysLog,logger, start, api_path, self.request.auth.user,self.request,function_title)"
        list_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info,
                                               line_break_str)
        info = "return querysets"
        list_code_str += "{}{}{}{}{}{}".format(tab_str, tab_str, tab_str, tab_str, info,
                                               line_break_str)
        list_code_str += "{}{}{}{}".format(tab_str, tab_str,
                                           "except Exception as exp:", line_break_str)
        list_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str,
                                             "res = LoggerHelper.set_end_log_info_in_exception(SysLog,logger, start, api_path,self.request.auth.user, self.request,function_title, None, exp)",
                                             line_break_str)
        list_code_str += "{}{}{}{}{}".format(tab_str, tab_str, tab_str,
                                             "return Response(res)", line_break_str)

        print(list_code_str)


# 生成重复性的代码片段
class BuildCode:
    def __init__(self):
        pass

    ## 包装数量 packing_quanlity
    # obj["{packing_quanlity}"] = pre_insurance_info.packing_quanlity
    # # 投保金额 insured_amount
    # obj["{insured_amount}"] = pre_insurance_info.insured_amount
    def create_snippt(self, obj_name, class_name, attribute_name_list, attribute_caption_list):
        code_str = ""
        for index in range(len(attribute_name_list)):
            attribute_name = attribute_name_list[index]
            if len(attribute_caption_list) > 0:
                attribute_caption = attribute_caption_list[index]
                temp_str = "# {}".format(attribute_caption)
                code_str += temp_str + "\n"
            temp_str = "{}[\"{{{}}}\"] = {}.{}".format(obj_name, attribute_name, class_name, attribute_name)
            code_str += temp_str + "\n"
        print(code_str)
        return code_str

    #  obj = {}
    #  obj['id'] = record[0]
    #  obj['insurance_year'] = record[1]
    #  obj = {}
    #  obj['id'] = record[0] if record[0] is not None else None
    #  obj['insurance_year'] =  if record[1] is not None else None
    #  obj = {}
    #  obj['id'] = record[0] if record[0] is not None else ""
    #  obj['insurance_year'] =  if record[1] is not None else ""
    #  obj = {}
    #  obj['编号'] = record[0]
    #  obj['保险年份'] = record[1]
    #  obj = {}
    #  obj['编号'] = record[0] if record[0] is not None else None
    #  obj['保险年份'] =  if record[1] is not None else None
    #  obj = {}
    #  obj['编号'] = record[0] if record[0] is not None else ""
    #  obj['保险年份'] =  if record[1] is not None else ""

    def create_snippt2(self, obj_name, attribute_enames_str, attribute_cnames_str):
        code_str = "{} = {{}}\n".format(obj_name)
        code_str2 = "{} = {{}}\n".format(obj_name)
        code_str3 = "{} = {{}}\n".format(obj_name)
        if attribute_enames_str is not None:
            attribute_name_list = attribute_enames_str.split(",")
            for index in range(len(attribute_name_list)):
                attribute_name = attribute_name_list[index]
                temp_str = "{}['{}'] = record[{}]".format(obj_name, attribute_name, index)
                temp_str2 = "{}['{}'] = record[{}] if record[{}] is not None else None ".format(obj_name,
                                                                                                attribute_name, index,
                                                                                                index)
                temp_str3 = "{}['{}'] = record[{}] if record[{}] is not None else \"\" ".format(obj_name,
                                                                                                attribute_name, index,
                                                                                                index)
                code_str += temp_str + "\n"
                code_str2 += temp_str2 + "\n"
                code_str3 += temp_str3 + "\n"
            print(code_str)
            print(code_str2)
            print(code_str3)

        code_str = "{} = {{}}\n".format(obj_name)
        code_str2 = "{} = {{}}\n".format(obj_name)
        code_str3 = "{} = {{}}\n".format(obj_name)
        if attribute_cnames_str is not None:
            attribute_name_list = attribute_cnames_str.split(",")
            for index in range(len(attribute_name_list)):
                attribute_name = attribute_name_list[index]
                temp_str = "{}['{}'] = record[{}]".format(obj_name, attribute_name, index)
                temp_str2 = "{}['{}'] = record[{}] if record[{}] is not None else None ".format(obj_name,
                                                                                                attribute_name, index,
                                                                                                index)
                temp_str3 = "{}['{}'] = record[{}] if record[{}] is not None else \"\" ".format(obj_name,
                                                                                                attribute_name, index,
                                                                                                index)
                code_str += temp_str + "\n"
                code_str2 += temp_str2 + "\n"
                code_str3 += temp_str3 + "\n"
            print(code_str)
            print(code_str2)
            print(code_str3)
        return code_str,code_str2,code_str3

    # sub_insurance_policy_number = request.data[ "sub_insurance_policy_number"] if "sub_insurance_policy_number" in request.data else None
    # pre_insurance_policy_number = request.data["pre_insurance_policy_number"] if "pre_insurance_policy_number" in request.data else None
    def create_snippt3(self, obj_name, attribute_names_str):
        code_str = ""
        attribute_name_list = attribute_names_str.split(",")
        for index in range(len(attribute_name_list)):
            attribute_name = attribute_name_list[index]
            temp_str = "{} = {}[\"{}\"] if \"{}\" in {} else None".format(attribute_name, obj_name, attribute_name,
                                                                          attribute_name, obj_name)
            code_str += temp_str + "\n"
        print(code_str)
        return code_str

    # if ExcelHelper.is_has_field_in_excel(excel_data_obj, "总序号"):
    #     ocr_result["total_serial_number"] = excel_data_obj.values[row_index][
    #         ExcelHelper.get_field_index_by_name_in_excel(excel_data_obj, "总序号")]
    #     ocr_result["total_serial_number"] = ocr_result["total_serial_number"] if ocr_result[
    #                                                                                  "total_serial_number"] is not None and str(
    #         ocr_result["total_serial_number"]).strip() != "" else None
    def create_snippt4(self, excel_obj_name, attribute_cnames_str, attribute_enames_str):
        tab_str = "\t"
        line_break_str = "\r\n"
        code_str = ""
        attribute_cname_list = attribute_cnames_str.split(",")
        attribute_ename_list = attribute_enames_str.split(",")
        for index in range(len(attribute_cname_list)):
            attribute_cname = attribute_cname_list[index]
            attribute_ename = attribute_ename_list[index]
            temp_str = "if ExcelHelper.is_has_field_in_excel({}, \"{}\"):".format(excel_obj_name, attribute_cname)
            code_str += temp_str + line_break_str
            temp_str = "{}ocr_result[\"{}\"] = excel_data_obj.values[row_index][ExcelHelper.get_field_index_by_name_in_excel(excel_data_obj, \"{}\")]".format(
                tab_str, attribute_ename, attribute_cname)
            code_str += temp_str + line_break_str
            temp_str = "{0}ocr_result[\"{1}\"] = ocr_result[\"{1}\"] if ocr_result[\"{1}\"] is not None and str(ocr_result[\"{1}\"]).strip() != \"\" else None".format(
                tab_str, attribute_ename)
            code_str += temp_str + line_break_str
        print(code_str)
        return code_str

    # 得到数据表的所有字段英文名和中文名的连接字符串，中间用逗号链接
    # "序号,板块,分公司,投保人,投保人地址,起保日期,终保日期,被保险人职业分类,投保人数,意外伤害身故、残疾（万元/人）,意外伤害医疗（万元/人）,急性病身故（万元/人）,疾病身故（万元/人）,猝死（万元/人）,住院津贴（元/天）,住院津贴天数,门诊误工津贴（元/天）,死亡、伤残（%）,意外医疗（%）,急性病身故（%）,疾病身故（%）,猝死（%）,住院津贴（%）,门诊误工津贴（%）,每人保费,投保天数,总保费,保批单类型,投保单号,保单号,批单号,邮件日期,保费发票抬头（必须为被保险人）,保单发票邮寄联系人、地址及联系方式,邮寄单号,经纪人,到账金额,到账备注,备注,联共保标识"
    # "requirement_enterprise_number,enterprise_sector_name,enterprise_branch_name,applicant,applicant_address,insurance_start_date,insurance_end_date,insured_occupational_classification,policyholders_number,accidental_injury_death_disability_premium_standard,accidental_injury_medical_treatment_premium_standard,acute_illness_death_premium_standard,illness_death_premium_standard,sudden_death_premium_standard,hospitalization_allowance_premium_standard,hospitalization_allowance_days,outpatient_delay_allowance_premium_standard,accidental_injury_death_disability_premium_ratio,accidental_injury_medical_treatment_premium_ratio,acute_illness_death_premium_ratio,illness_death_premium_ratio,sudden_death_premium_ratio,hospitalization_allowance_premium_ratio,outpatient_delay_allowance_premium_ratio,per_person_premium,insurance_days,total_premium,policy_endorsement_type,sub_policy_number,policy_number,endorsement_number,email_received_time,premium_invoice_header,premium_invoice_delivery_information,premium_invoice_delivery_number,agent,received_moneyamount,recevied_money_memo,memo,joint_insurance_label"
    def get_full_field_str(self, connection, tablename):
        sql = "select a.attnum,a.attname,concat_ws('',t.typname,SUBSTRING(format_type(a.atttypid,a.atttypmod) from '\(.*\)')) as type,d.description from pg_class c, pg_attribute a , pg_type t, pg_description d where  c.relname = '{}' and a.attnum>0 and a.attrelid = c.oid and a.atttypid = t.oid and  d.objoid=a.attrelid and d.objsubid=a.attnum".format(
            tablename)
        cursor = connection.cursor()
        cursor.execute(sql)
        records = cursor.fetchall()
        attribute_ename_str = ""
        attribute_cname_str = ""
        for record in records:
            attribute_ename_str += record[1] + ","
            attribute_cname_str += record[3] + ","
        attribute_cname_str = attribute_cname_str.rstrip(",")
        attribute_ename_str = attribute_ename_str.rstrip(",")
        print(attribute_cname_str)
        print(attribute_ename_str)
        return attribute_cname_str, attribute_ename_str


# 构建命令行参数
def make_build_command():
    # 测试命令行
    args = {
        # py文件名称
        "py_file_name": "crawlerWebsiteData.py",
        # 全局变量定义,用分号隔离
        "var_name_list": "website_url;is_turn_page;turn_page_num;fields_name_str;fields_path_str;result_excel_path",
        # 全局变量注释，用分号隔离
        "var_anno_list": "进行网络抓取的网站URL;是否翻页;翻到多少页;提取字段名称字符串，用逗号连接;提取字段路径字符串，用&&连接;提取结果excel文件路径",
        # 全局变量赋值，用分号隔离
        "var_value_list": "https://bj.fang.lianjia.com/loupan;true;5;名称,面积,类型;div.resblock-vgis_list-container.clearfix>ul.resblock-vgis_list-wrapper>li.resblock-vgis_list.post_ulog_exposure_scroll.has-results>div.resblock-desc-wrapper>div.resblock-name>a.name&&div.resblock-vgis_list-container.clearfix>ul.resblock-vgis_list-wrapper>li.resblock-vgis_list.post_ulog_exposure_scroll.has-results>div.resblock-desc-wrapper>div.resblock-area>span&&div.resblock-vgis_list-container.clearfix>ul.resblock-vgis_list-wrapper>li.resblock-vgis_list.post_ulog_exposure_scroll.has-results>div.resblock-desc-wrapper>div.resblock-name>span.resblock-type;d:/qcndata/recong_tmp.xlsx",
        # 长类型定义,用分号隔离
        "var_long_option_list": "websiteUrl;isTurnPage;turnPageNum;fieldsNameStr;fieldsPathStr;resultExcelPath",
        # 短类型定义，用冒号隔离
        "var_short_opt_list": "w:t:s:n:p:d:"
    }
    code_builder = BuildCommand(args)
    code_builder.make_command_str()


# def get_database_conection(HOST, PORT, USER, PASSWORD, DATABASE):
#     # HOST = "192.168.3.191"
#     # PORT = "5432"
#     # USER = "postgres"
#     # PASSWORD = "postgres123"
#     # DATABASE = "BXJCXTDB"
#     try:
#         conn = psycopg2.connect(database=DATABASE, user=USER, password=PASSWORD,
#                                 host=HOST, port=PORT)
#         sql = "select count(*) from pg_tables;"
#         cursor = conn.cursor()
#         cursor.execute(sql)
#         records = cursor.fetchall()
#         print("建立数据库连接成功")
#     except Exception as exp:
#         conn = None
#         print("建立数据库连接失败，可能原因：{}".format(str(exp)))
#     # 需要判断是否连接可视化数据库成功
#     return conn


# 生成django代码
def make_django_code():
    model_file = "E:\\model.txt"
    host = "192.168.3.191"
    port = "5432"
    user = "postgres"
    passwd = "postgres123"
    database = "BXJCXTDB"
    connection = PgHelper.get_database_conection(host, port, user, passwd, database)
    token_key = "Authorization"
    postman_file = "E:\\通用项目.postman_collection.json"
    postman_file_encrpt = "E:\\通用项目（加密）.postman_collection.json"
    aes_key = "myaovgis0713wxgz"
    code_builder = BuildDjango(model_file, connection, token_key, postman_file, postman_file_encrpt, aes_key)
    code_builder.generate_serializer()
    print("-----------------------------------------")
    code_builder.generate_viewer()
    print("-----------------------------------------")
    code_builder.generate_classes()
    print("-----------------------------------------")
    code_builder.generate_urls()
    print("-----------------------------------------")
    # 数据表内先手动插入一条数据，作为postman增加和更新数据的模板
    code_builder.generate_postman()
    code_builder.generate_postman_encrpyt()


# # 包装数量
# obj["{packing_quanlity}"] = pre_insurance_info.packing_quanlity
# # 投保金额
# obj["{insured_amount}"] = pre_insurance_info.insured_amount
# # 运输工具
# obj["{per_conveyance}"] = pre_insurance_info.per_conveyance


# request.data["subject_matter"] = relatedInsurancePreObj.subject_matter
# request.data["packing_quanlity"] = relatedInsurancePreObj.packing_quanlity
def make_code_snippt():
    code_builder = BuildCode()
    obj_name = "obj"
    class_name = "pre_insurance_info"
    attribute_name_list = ["packing_quanlity", "insured_amount", "per_conveyance"]
    # 中文可为空
    attribute_caption_list = ["包装数量", "投保金额", "运输工具"]
    code_builder.create_snippt(obj_name, class_name, attribute_name_list, attribute_caption_list)


#  obj = {}
#  obj['id'] = record[0]
#  obj['insurance_year'] = record[1]
#  obj = {}
#  obj['id'] = record[0] if record[0] is not None else None
#  obj['insurance_year'] =  if record[1] is not None else None
#  obj = {}
#  obj['id'] = record[0] if record[0] is not None else ""
#  obj['insurance_year'] =  if record[1] is not None else ""
#  obj = {}
#  obj['编号'] = record[0]
#  obj['保险年份'] = record[1]
#  obj = {}
#  obj['编号'] = record[0] if record[0] is not None else None
#  obj['保险年份'] =  if record[1] is not None else None
#  obj = {}
#  obj['编号'] = record[0] if record[0] is not None else ""
#  obj['保险年份'] =  if record[1] is not None else ""
def make_code_snippt2():
    code_builder = BuildCode()
    obj_name = "obj"
    attribute_cnames_str = "编号,台账编号,邮件编号"
    attribute_enames_str = "id,standing_book_number,email_number"
    code_builder.create_snippt2(obj_name, attribute_enames_str, attribute_cnames_str)


# sub_insurance_policy_number = request.data[ "sub_insurance_policy_number"] if "sub_insurance_policy_number" in request.data else None
# pre_insurance_policy_number = request.data["pre_insurance_policy_number"] if "pre_insurance_policy_number" in request.data else None
def make_code_snippt3():
    code_builder = BuildCode()
    obj_name = "request.data"
    attribute_names_str = "sub_insurance_policy_number,pre_insurance_policy_number"
    code_builder.create_snippt3(obj_name, attribute_names_str)


def make_code_snippt4():
    code_builder = BuildCode()
    excel_obj_name = "excel_data_obj"
    attribute_cnames_str = "序号,板块,分公司,投保人,投保人地址,起保日期,终保日期,被保险人职业分类,投保人数,意外伤害身故、残疾（万元/人）,意外伤害医疗（万元/人）,急性病身故（万元/人）,疾病身故（万元/人）,猝死（万元/人）,住院津贴（元/天）,住院津贴天数,门诊误工津贴（元/天）,死亡、伤残（%）,意外医疗（%）,急性病身故（%）,疾病身故（%）,猝死（%）,住院津贴（%）,门诊误工津贴（%）,每人保费,投保天数,总保费,保批单类型,投保单号,保单号,批单号,邮件日期,保费发票抬头（必须为被保险人）,保单发票邮寄联系人、地址及联系方式,邮寄单号,经纪人,到账金额,到账备注,备注,联共保标识"
    attribute_enames_str = "requirement_enterprise_number,enterprise_sector_name,enterprise_branch_name,applicant,applicant_address,insurance_start_date,insurance_end_date,insured_occupational_classification,policyholders_number,accidental_injury_death_disability_premium_standard,accidental_injury_medical_treatment_premium_standard,acute_illness_death_premium_standard,illness_death_premium_standard,sudden_death_premium_standard,hospitalization_allowance_premium_standard,hospitalization_allowance_days,outpatient_delay_allowance_premium_standard,accidental_injury_death_disability_premium_ratio,accidental_injury_medical_treatment_premium_ratio,acute_illness_death_premium_ratio,illness_death_premium_ratio,sudden_death_premium_ratio,hospitalization_allowance_premium_ratio,outpatient_delay_allowance_premium_ratio,per_person_premium,insurance_days,total_premium,policy_endorsement_type,sub_policy_number,policy_number,endorsement_number,email_received_time,premium_invoice_header,premium_invoice_delivery_information,premium_invoice_delivery_number,agent,received_moneyamount,recevied_money_memo,memo,joint_insurance_label"
    code_builder.create_snippt4(excel_obj_name, attribute_cnames_str, attribute_enames_str)


def get_full_field_str():
    code_builder = BuildCode()
    host = "192.168.3.191"
    port = "5432"
    user = "postgres"
    passwd = "postgres123"
    database = "ZHBXFZCD"
    connection = PgHelper.get_database_conection(host, port, user, passwd, database)
    code_builder.get_full_field_str(connection, "tt_group_accident_insurance_standing_book")


if __name__ == '__main__':
    # 构建命令行参数
    # make_build_command()
    # print("***************************************************************")
    # 生成django代码
    # make_django_code()
    # print("***************************************************************")
    # 生成代码片段
    get_full_field_str()
    # print("***************************************************************")
    # make_code_snippt()
    # print("***************************************************************")
    make_code_snippt2()
    # print("***************************************************************")
    # # make_code_snippt3()
    # print("***************************************************************")
    # # make_code_snippt4()
    # print("***************************************************************")

    pass
