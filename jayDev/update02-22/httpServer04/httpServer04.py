import sys
import readline
import socket
import time
import queue


def jobServer01(newData):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('',50001))

    s.sendall(newData.encode())

    data = s.recv(10240).decode()

    s.close()


def jobServer02(newData):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('',50002))

    s.sendall(newData.encode())

    data = s.recv(10240).decode()

    s.close()


def jobServer03(newData):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('',50003))

    s.sendall(newData.encode())

    data = s.recv(10240).decode()

    s.close()


def jobServer04(newData):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('',50004))

    s.sendall(newData.encode())

    iList = newData.split(',')

    if iList[1] == 'DUMPLOG'and len(iList) == 4:
        f = open(iList[3], "w+")
        while True:
            data = s.recv(10240).decode()
            newData = data[-7:]
            if newData == "the end":
                break
            else:
                f.write(data)

        f.close()

    elif iList[1] == 'DUMPLOG' and len(iList) == 3:
        f = open(iList[2], "w+")
        while True:
            data = s.recv(10240).decode()
            newData = data[-7:]
            if newData == "the end":
                break
            else:
                f.write(data)

        f.close()

    elif iList[1] == "DISPLAY_SUMMARY":
        while True:
            data = s.recv(10240).decode()
            #print(len(data))
            newData = data[-7:]
            if newData == "the end":
                #print(newData)
                break

    s.close()



def sendToTrans():
    filename0 = "example.txt"
    filename1 = "user1.txt"
    filename2 = "user2.txt"
    filename3 = "user10.txt"
    filename4 = "user45.txt"
    filename5 = "workload4.txt"

    alist = [line.rstrip() for line in open(filename5)]

    #transNum = 0
    for newData in alist:
        #transNum += 1

        iList = newData.split(',')

        # newData = ''
        # newData = ','.join([str(transNum),i])


        if iList[1] in ['ADD', 'QUOTE']:
            jobServer01(newData)
        elif iList[1] in ['BUY', 'COMMIT_BUY', 'CANCEL_BUY', 'SELL', 'COMMIT_SELL', 'CANCEL_SELL']:
            jobServer02(newData)
        elif iList[1] in ['SET_BUY_AMOUNT', 'CANCEL_SET_BUY', 'SET_BUY_TRIGGER', 'SET_SELL_AMOUNT', 'CANCEL_SET_SELL', 'SET_SELL_TRIGGER']:
            jobServer03(newData)
        else:
            jobServer04(newData)


if __name__=="__main__":
    sendToTrans()
    print('finished...04')
