import sys
import readline
import queue



def reader():
    filename0 = "example.txt"
    filename1 = "user1.txt"
    filename2 = "user2.txt"
    filename3 = "user10.txt"
    filename4 = "user45.txt"

    alist = [line.rstrip().split(' ')[1] for line in open(filename3)]

    userDic = {}

    transNum = 0
    for i in alist:
        transNum += 1

        iList = i.split(',')

        newData = ''
        newData = ','.join([str(transNum),i])


        if iList[0] == "DUMPLOG":
            userDic.update({iList[0]:[newData]})
        elif iList[1] not in userDic:
            userDic.update({iList[1]:[newData]})
        else:
            userDic.get(iList[1]).append(newData)


    spliter = 0
    loadcount = 1
    for v in userDic.values():
        if spliter == 0:
            filename = 'workload'+str(loadcount)+'.txt'
            f = open(filename, 'w')
            loadcount += 1

        for item in v:
            f.write(item+'\n')

        spliter += 1

        if spliter == 3:
            spliter = 0
            f.close()


if __name__ == '__main__':
    reader()
