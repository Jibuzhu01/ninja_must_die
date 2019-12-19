#coding=gbk
import sys
import os

name = sys.argv[1] #全拼
name_dict_file = "./data/name_dict"
name_dict = {}
file_path = "./data/" + name + '/'
files = os.listdir(file_path)
file_set = set()

with open(name_dict_file) as fr:
    for line in fr:
        ori_name = line.strip().split(' ')[0]
        now_name = line.strip().split(' ')[1]
        name_dict[ori_name] = now_name

for file in files:
    file_set.add(file_path + file)

def Process(file, sta_dict, total_tm_set):
    #sta_dict记录统计值，total_tm_set记录出现过哪些时间戳，便于后面遍历
    with open(file) as fr:
        line_num = 0
        for line in fr:
            if line_num == 0:
                fuben, tm = line.strip().split('\t')
                total_tm_set.add(tm)
            if line_num > 1:
                name, num = line.strip('\n').split('\t')
                if name in name_dict:
                    name = name_dict[name]
                name = name.strip()
                if name not in sta_dict:
                    sta_dict[name] = {}
                sta_dict[name][tm] = int(num)
            line_num += 1



def Output(sta_dict, total_tm_set, group):
    tm_list = sorted(total_tm_set)
    out_file_name = "./data/total_" + group
    out_file = open(out_file_name, 'w')
    total_dict = {}
    out_str = group + '\t'
    for item in tm_list:
        out_str += item + '\t'
        total_dict[item] = []
    out_str += 'max' + '\t' + 'average' + '\t' + 'times' + '\n'
    out_file.write(out_str)
    for name in sta_dict:
        out_str = name
        one_user_times = 0
        one_user_total_num = 0
        one_user_max_num = 0
        for tm in tm_list:
            if tm in sta_dict[name]:
                out_str += '\t' + str(sta_dict[name][tm])
                one_user_times += 1
                one_user_total_num += int(sta_dict[name][tm])
                one_user_max_num = max(one_user_max_num, sta_dict[name][tm])
                total_dict[tm].append(sta_dict[name][tm])
            else:
                out_str += '\t' + "-1"
        out_str += '\t' + str(one_user_max_num) + '\t' + str(float(one_user_total_num)/float(one_user_times)) + '\t' + str(one_user_times) + '\n'
        #print out_str
        #out_file.write(out_str.encode('gbk', 'ignore'))
        out_file.write(out_str)
    out_str = "total" + '\t'
    for tm in tm_list:
        temp_list = sorted(total_dict[tm], reverse = True)
        temp_int = sum(temp_list[0:30])
        out_str += str(temp_int) + '\t'
    out_str = out_str.strip() + '\n'
    out_file.write(out_str)
    out_file.close()



sta_dict = {}
total_tm_set = set([])
for file in file_set:
    Process(file, sta_dict, total_tm_set)
Output(sta_dict, total_tm_set, name)


