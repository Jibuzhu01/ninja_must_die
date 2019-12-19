#coding=gbk
import sys
import requests
import json
import base64
import urllib
import os
import time
import datetime

from aip import AipOcr


class OcrSta:
    def __init__(self, need_dict):
        self.appid = "17190994"
        self.api_key = "QG8ZlQll0h3Ue1sSau33oAXi"
        self.secret_key = "DQSYSiVelTsbX2SF9iY5qkRN8krpMsOM"
        self.model = need_dict.get("model", 0)
        self.templateList = ["", "8bfde40b92dbc0327b9856eceb132881", "d13744efe98c81097165696ecb306ba0", "01a1dc76d0b37cd5540365026ea302f1"] #深渊,副本,团本
        self.table_kw = [set([]), set(["damage", "num", "name"]), set(["name", "num"]), set(["name", "num"])]
        self.picture_path = ["moren/", "shenyuan/", "fuben/", "tuanben/"]
        self.client = AipOcr(self.appid, self.api_key, self.secret_key)
        self.pic_set = self.get_all_picture()
        self.options = {"templateSign": self.templateList[self.model]}
        self.my_info_dict = {}

    def get_all_picture(self):
        path = "./" + self.picture_path[self.model]
        files = os.listdir(path)
        pic_set = set()
        for file in files:
            if ".jpg" in file:
                pic_set.add(path + file)
        return pic_set

    def get_file_content(self, filepath):
        with open(filepath, 'rb') as fp:
            return fp.read()

    def OcrPic(self):
        pic_num = 0
        for pic in self.pic_set:
            pic_num += 1
            print pic_num
            image = self.get_file_content(pic)
            a = self.client.custom(image, self.options)
            print a
            ans_data = a["data"]
            ret = ans_data["ret"]
            name = ""
            #print a
            for item in ret:
                #遍历这张表里的每一行
                info_list = item["word_name"].strip().split('#')
                if self.model == 1: #以下处理深渊
                    if "name" == info_list[2]:
                        name = item["word"].replace(u'\u526f\u65cf\u957f',"").replace(u"\u65cf\u5458","").replace(u"\u65cf\u957f","").replace(u'\u957f\u8001',"").replace(u'\u65b0\u4eba',"").replace(u'\u7cbe\u82f1',"").replace(u'\u8c6a\u6770',"")
                        self.my_info_dict[name] = {"damage":0, "num":0}
                    if "damage" == info_list[2]:
                        self.my_info_dict[name]["damage"] = item["word"]
                    if "num" == info_list[2]:
                        self.my_info_dict[name]["num"] = item["word"]
                elif self.model == 2 or self.model == 3: #以下处理副本和团本
                    if "name" == info_list[2]:
                        name = item["word"].replace(u'\u526f\u65cf\u957f',"").replace(u"\u65cf\u5458","").replace(u"\u65cf\u957f","").replace(u'\u957f\u8001',"").replace(u'\u65b0\u4eba',"").replace(u'\u7cbe\u82f1',"").replace(u'\u8c6a\u6770',"")
                        if not name:
                            name = " "
                        self.my_info_dict[name] = {"num":0}
                    if "num" == info_list[2]:
                        filter_word = ""
                        for char in item["word"]:
                            if char.isdigit():
                                filter_word += char
                        self.my_info_dict[name]["num"] = filter_word

             
    def PrintToScreen(self):
        for key in self.my_info_dict:
            out_str = key + '\t' 
            for label in self.my_info_dict[key]:
                out_str += label + '\t' + str(self.my_info_dict[key][label]) + '\t'
            print out_str

    def PrintToFile(self):
        today = datetime.date.today().strftime("%Y%m%d")
        out_file = self.picture_path[self.model].strip('/') + '_' + str(today)
        f = open(out_file, 'w')
        if self.model == 1: #以下处理深渊
            out_str = "shenyuan" + '\t' + today + '\n'
            f.write(out_str)
            out_str = "名字" + '\t' + "排名" + '\t' + "总伤害" + '\t' + "次数" + '\n'
            f.write(out_str)
            #2019.11.18修改，现在增加表头并且按照数值排序输出
            out_list = []
            for key in self.my_info_dict:
                temp_list = [key, self.my_info_dict[key]['damage'], self.my_info_dict[key]['num']]
                out_list.append(temp_list)
            out_list = sorted(out_list, key = lambda x:int(x[1]), reverse = True)
            index = 1
            for item in out_list:
                out_str = item[0] +  '\t' + str(index) + '\t' + str(item[1]) + '\t' + str(item[2]) + '\n'
                index += 1
                f.write(out_str.encode('gbk', 'ignore'))
        if self.model == 2 or self.model == 3: #以下处理副本和团本
            out_str = "副本名字" + '\t' + today + '\n'
            f.write(out_str)
            out_str = "名字" + '\t' + "成绩" + '\n'
            f.write(out_str)
            #2019.11.18修改，现在增加表头并且按照数值排序输出
            out_list = []
            for key in self.my_info_dict:
                temp_list = [key, self.my_info_dict[key]['num']]
                out_list.append(temp_list)
            out_list = sorted(out_list, key = lambda x:int(x[1]), reverse = True)
            for item in out_list:
                out_str = item[0] + '\t' + str(item[1]) + '\n'
                f.write(out_str.encode('gbk', 'ignore'))
        f.close()


if __name__ == '__main__':
    need_dict = {"model": 3}
    my_class = OcrSta(need_dict)
    my_class.OcrPic()
    #my_class.PrintToScreen()
    my_class.PrintToFile()

                

