
import sys

fuben_name = sys.argv[1]
date = sys.argv[2]

out_file = "./data/" + fuben_name + "/" + fuben_name + "_" + date
fr = open(out_file, 'w')

line_num = 0
my_list = []
for line in sys.stdin:
    line_num += 1
    if line_num == 1:
        print >> fr, fuben_name + '\t' + date
    elif line_num == 2:
        print >> fr,line.strip()
    else:
        temp_list = line.strip('\n').split('\t')
        my_list.append(temp_list)
my_list = sorted(my_list, key = lambda x:int(x[1]), reverse = True)
for item in my_list:
    print >> fr,item[0] + '\t' + item[1]
fr.close()


