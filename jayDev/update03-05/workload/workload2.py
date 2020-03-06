import sys
import readline

userDic = {}
userADD = []
alist = [line.rstrip().split(' ')[1] for line in open('user45.txt')]

for i in alist:
    iList = i.split(',')
    if iList[0] == "ADD" and (iList[0]+','+iList[1]) not in userDic:
        userDic.update({(iList[0]+','+iList[1]): i})
    else:
        userADD.append(i)
print(userDic.keys())
f = open('workload45.txt', 'w+')
for values in userDic.values():
    f.write(values+'\n')
for i in userADD:
    f.write(i+'\n')
f.close()
