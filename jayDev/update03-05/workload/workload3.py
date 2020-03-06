import sys
import readline

alist = [line.rstrip().split(' ')[1] for line in open("user10.txt")]

userList = {}

for item in alist:
    itemList = item.strip().split(',')

    if itemList[0] == "DUMPLOG":
        userList.update({itemList[0]:[item]})
    elif itemList[1] not in userList:
        userList.update({itemList[1]:[item]})
    else:
        userList.get(itemList[1]).append(item)

print(userList.keys())
A = []
with open('workload10.txt','w') as f:
    for values in  userList.values():
        for item in values:
            #ilist = item.split(',')
            #if ilist[0] == "QUOTE" and ilist not in A:
                #A.append(ilist)
            f.write(item+'\n')
