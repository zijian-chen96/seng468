import sys
import readline
import socket
import time
import threading

filename0 = "example.txt"
filename = "user1.txt"
filename2 = "user2.txt"
filename3 = "user10.txt"
filename4 = "user45.txt"
filename5 = "1000User_testWorkLoad"
filename6 = "workload45.txt"

def recvFromTrans():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',52000))
    s.listen(5)


    while True:
        try:
            cSocket, addr = s.accept()
            #print("waiting server send back messages......")
            data = cSocket.recv(10240).decode()
            print(data)
            cSocket.close()
        except:
            continue
        #cSocket.sendall(('ok').encode())


        # if iList[0] == 'DUMPLOG'and len(iList) == 3:
        #     f = open(iList[2], "w+")
        #     while True:
        #         data = s.recv(10240).decode()
        #         newData = data[-7:]
        #         if newData == "the end":
        #             break
        #         else:
        #             f.write(data)
        #
        #     f.close()
        #
        # elif iList[0] == 'DUMPLOG' and len(iList) == 2:
        #     f = open(iList[1], "w+")
        #     while True:
        #         data = s.recv(10240).decode()
        #         newData = data[-7:]
        #         if newData == "the end":
        #             break
        #         else:
        #             f.write(data)
        #
        #     f.close()
        #
        # elif iList[0] == "DISPLAY_SUMMARY":
        #     while True:
        #         data = s.recv(10240).decode()
        #         #print(len(data))
        #         newData = data[-7:]
        #         if newData == "the end":
        #             #print(newData)
        #             break
        #
        # else:
        #     data = s.recv(10240).decode()
        #     #if data:
        #         #print(data)



def sendToTrans():
    alist = [line.rstrip().split(' ')[1] for line in open(filename5)]

    transNum = 0
    userCommandDic = {}
    for i in alist:
        transNum += 1
        newData = ''
        newData = ','.join([str(transNum),i])

        dlist = i.split(',')
        if dlist[1] not in userCommandDic:
            userCommandDic.update({dlist[1]:[newData]})
        else:
            userCommandDic[dlist[1]].append(newData)


    for value in userCommandDic.values():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('',50000))
        value = '\n'.join(value)
        # print(userCommandDic.keys())
        s.sendall((value+"the end").encode())
        #time.sleep(0.1)
        # s.recv(1024).decode()
        #print('the end')

        #s.close()

if __name__=="__main__":

    th = threading.Thread(target=recvFromTrans)
    th.start()

    sendToTrans()

    th.join()
