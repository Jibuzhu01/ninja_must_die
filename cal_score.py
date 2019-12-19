#coding=gbk
import sys
import os
import time
import json
import datetime

class CalScore:
    def __init__(self, need_dict):
        self.model = need_dict.get("model", 0)
        self.root = ["", "./data/shenyuan", "./data"]
        self.date_set = self.get_ava_date()
        self.my_dict = self.make_score_dict()
        self.name_dict = self.make_name_dict()
        self.name_list_file = ["", "./data/name_list_shenyuan", "./data/name_list_tuanben"]

    def make_name_dict(self):
        file_name = "./data/name_dict"
        name_dict = {}
        with open(file_name) as fr:
            for line in fr:
                ori, now = line.strip().split(' ')
                name_dict[ori] = now
        name_dict[""] = " "
        return name_dict


    def get_ava_date(self):
        #计算距离现在最近的日期，对于深渊来说，是上个周五，对于族战来说，是上个周六和周日，返回一个set，记录所有需要的八位日期
        today = int(time.strftime("%w"))
        ans = set([])
        if self.model == 1:
            #深渊
            if today == 5:
                ans.add(str(datetime.date.today().strftime("%Y%m%d")))
            elif today > 5:
                ans.add(str((datetime.date.today() - datetime.timedelta(today - 5)).strftime("%Y%m%d")))
            else:
                ans.add(str((datetime.date.today() - datetime.timedelta(today + 2)).strftime("%Y%m%d")))
        elif self.model == 2:
            #找到上个周六周日
            gap_day = 0
            while len(ans) < 2:
                want_day = int((datetime.date.today() - datetime.timedelta(gap_day)).strftime("%w"))
                if want_day == 6:
                    ans.add(str((datetime.date.today() - datetime.timedelta(gap_day)).strftime("%Y%m%d")))
                elif want_day == 0:
                    ans.add(str((datetime.date.today() - datetime.timedelta(gap_day)).strftime("%Y%m%d")))
                gap_day += 1
                if gap_day > 15:
                    break
        return ans

    def make_score_dict(self):
        #hetun = [[109,2],[108,1.5],[106,1],[103,0.5],[100,-0.5],[-100,-1]]
        hetun = [[-100, 0]]
        wujin = [[4067,2],[3600,1.5],[3100,1],[2800,0.5],[2300,-0.5],[-100,-1]]
        wujin = [[4067,2],[3500,1.5],[3000,1],[2726,0.5],[2200,-0.5],[-100,-1]]
        bianfu = [[380,3],[370,2],[350,1.5],[320,1],[290,0.5],[260,-0.5],[-100,-1]]
        baoxiang = [[60,3],[58,2],[55,1.5],[52,1],[48,0.5],[42,-0.5],[-100,-1]]
        jinbi = [[3075,3],[3025,2],[2925,1.5],[2825,1],[2650,0.5],[2500,-0.5],[-100,-1]]
        feibiao = [[595,3],[590,2],[570,1.5],[545,1],[520,0.5],[470,-0.5],[-100,-1]]
        xigua = [[314,3],[310,2],[300,1.5],[280,1],[270,0.5],[245,-0.5],[-100,-1]]
        lidai = [[75,3],[70,2],[65,1.5],[60,1],[52,0.5],[46,-0.5],[-100,-1]]
        shenyuan = [[3,4],[10,3],[20,2],[35,1],[50,0.5],[100,0]]
        my_dict = {"hetun": hetun, "wujin": wujin, "bianfu": bianfu, "baoxiang": baoxiang, "jinbi": jinbi, "feibiao": feibiao, "xigua": xigua, "lidai": lidai, "shenyuan": shenyuan}
        return my_dict

    def SearchFile(self, root, date, return_set):
        #本函数输入检索根目录，输出带有指定date的全部文件名，返回一个集合
        files = os.listdir(root)
        for file in files:
            path = os.path.join(root, file)
            if os.path.isdir(path):
                self.SearchFile(path, date, return_set)
            elif date in path:
                return_set.add(path)


    def get_want_file(self):
        file_set = set([])
        for date in self.date_set:
            self.SearchFile(self.root[self.model], date, file_set)
        return file_set

    def get_score(self, ben_name, num):
        ans = -100
        if ben_name == "shenyuan":
            for item in self.my_dict[ben_name]:
                if num <= item[0]:
                    return item[1]
        else:
            for item in self.my_dict[ben_name]:
                if num >= item[0]:
                    return item[1]
        return ans


    def get_name_dict(self):
        file_name = self.name_list_file[self.model]
        total_name_dict = {}
        #{"讨厌的周末": {"20191123": 3, "20191124": 1}}
        line_num = 0
        index = 0
        if self.model == 1:
            index = 0
        with open(file_name) as fr:
            for line in fr:
                if line_num == 0:
                    feature = line.strip().split('\t')
                else:
                    temp_list = line.strip('\n').split('\t')
                    name = temp_list[index]
                    total_name_dict[name] = {}
                    for i in range(index + 1, len(temp_list)):
                        total_name_dict[name][feature[i]] = temp_list[i]
                line_num += 1
        #print total_name_dict
        return total_name_dict


    def change_score_for_vocation(self, ori_score):
        if ori_score < 0:
            return 0
        else:
            return ori_score/2

    def process_jifen(self, total_name_dict, total_dict, name_set, out_file, singal_list):
        with open(out_file, 'w') as fr:
            out_str = "name" + '\t'
            for item in singal_list:
                out_str += item + '\t' + 'score' + '\t'
            out_str = out_str + 'total_score\n'
            fr.write(out_str)
            for name in total_name_dict:
                #对于每一个原始人，首先记录其原始分数，如果之前的分数没有就是-1
                #接下来对每一个人，处理请假的情况和减半逻辑
                out_str = name + '\t'
                temp_dict = {}
                attend_num = 0
                temp_score = 0.0
                for item in singal_list:
                    temp_dict[item] = -1
                    #print item
                    ben_name, date, flag = item.split('_')
                    if name in total_dict:
                        if item in total_dict[name]:
                            temp_dict[item] = self.get_score(ben_name, int(total_dict[name][item]))
                            attend_num += 1
                        else:
                            total_dict[name][item] = -1
                    else:
                        total_dict[name] = {}
                        total_dict[name][item] = -1
                        temp_dict[item] = self.get_score(ben_name, int(total_dict[name][item]))
                    if date in total_name_dict[name]:
                        if flag == '1' and (total_name_dict[name][date] == '2' or total_name_dict[name][date] == '3'):
                            #团本1请假，正分减半，负分清零
                            temp_dict[item] = self.change_score_for_vocation(temp_dict[item])
                            attend_num -= 1
                        if flag == '2' and (total_name_dict[name][date] == '1' or total_name_dict[name][date] == '3'):
                            #团本2请假，正分减半，负分清零
                            temp_dict[item] = self.change_score_for_vocation(temp_dict[item])
                            attend_num -= 1
                    temp_score += temp_dict[item]
                    out_str += str(total_dict[name][item]) + '\t' + str(temp_dict[item]) + '\t' 

                if temp_score < 0 and attend_num >= 3:
                    temp_score /= 2
                out_str += str(temp_score) + '\n'
                #接下来打印到输出文件当中
                fr.write(out_str)
                #处理完之后将这个name从有记录的name_set中删除，循环结束之后需要print name_set，看看谁没处理，多半就是名字错了
                if name in name_set:
                    name_set.remove(name)
        for name in name_set:
            print name

    def process_shenyuan(self, total_name_dict, total_dict, name_set, out_file):
        with open(out_file, 'w') as fr:
            out_str = "name" + '\t' + 'rank' + '\t' + 'damage' + '\t' + 'num' + '\t' + 'score\n'
            fr.write(out_str)
            for name in total_name_dict:
                out_str = name + '\t'
                temp_score = -4
                num = 0
                damage = 0

                if name in total_dict:
                    num = int(total_dict[name]['num'])
                    damage = int(total_dict[name]['damage'])
                    cishu = int(total_dict[name]['cishu'])
                    temp_score = self.get_score("shenyuan", num)
                    if cishu >= 3 and damage < 300000:
                        temp_score = -3

                #接下来处理请假
                data = list(self.get_ava_date())[0]
                if total_name_dict[name][data] != '0':
                    if temp_score > 0:
                        temp_score /= 2
                    else:
                        temp_score = 0

                #output
                out_str += str(num) + '\t' + str(damage) + '\t' + str(cishu) + '\t' + str(temp_score) + '\n'
                fr.write(out_str)
                if name in name_set:
                    name_set.remove(name)
        for name in name_set:
            print name







    def process(self):
        file_set = self.get_want_file()
        total_dict = {}
        singal_list = []
        name_set = set([])
        #将信息都存入字典中
        for file in file_set:
            with open(file) as fr:
                line_num = 0
                ben_name = ""
                ben_date = ""
                singal_flag = ""
                for line in fr:
                    if line_num == 0:
                        ben_name, ben_date = line.strip().split('\t')[0:2]
                        singal_flag = ben_name + '_' + ben_date
                        singal_list.append(singal_flag)
                    elif line_num > 1:
                        if self.model == 2:
                            name, num = line.strip('\n').split('\t')[0:2]
                        if self.model == 1:
                            name, num, damage, cishu = line.strip('\n').split('\t')[0:4]
                        name = name.strip()
                        if name in self.name_dict:
                            name = self.name_dict[name]
                        name_set.add(name)
                        if name not in total_dict:
                            total_dict[name] = {}
                        if singal_flag not in total_dict[name]:
                            if self.model == 2:
                                total_dict[name][singal_flag] = num
                        if self.model == 1:
                            total_dict[name] = {'num': num, "damage": damage, "cishu": cishu}
                    line_num += 1
        #按照日期对singal_list进行排序
        singal_list = sorted(singal_list, key = lambda x:x[-10:])
        #通过字典和载入的json将信息计算成分数并存入列表当中
        out_file = "./data/total_score_" + str(datetime.date.today().strftime("%Y%m%d"))
        total_name_dict = self.get_name_dict()
        if self.model == 2:
            self.process_jifen(total_name_dict, total_dict, name_set, out_file, singal_list)
        if self.model == 1:
            self.process_shenyuan(total_name_dict, total_dict, name_set, out_file)


if __name__ == '__main__':
    need_dict = {"model": 2}
    my_class = CalScore(need_dict)
    #return_set = my_class.get_want_file()
    my_class.process()
    #total_name_dict = my_class.get_name_dict()
    #print total_name_dict



