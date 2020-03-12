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
filename5 = "100User_testWorkLoad"
filename6 = "workload1000.txt"

def recvFromTrans():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',52000))
    s.listen(5)

    try:
        while True:
            cSocket, addr = s.accept()
            data = cSocket.recv(10240).decode()
            cSocket.sendall(('ok').encode())

    except:
        s.close()
        sys.exit()

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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('',50000))
    alist = [line.rstrip() for line in open(filename6)]

    transNum = 0
    for i in alist:
        transNum += 1
        newData = ''
        newData = ','.join([str(transNum),i])
        #print('newData send -- ' + newData)
        s.sendall(newData.encode())
        data = s.recv(1024).decode()
        #data = s.recv(1024)

        #iList = i.split(',')

        #print("iLst is -- " + str(iList))


    s.send(("finish").encode())
    s.close()

if __name__=="__main__":
    th = threading.Thread(target=recvFromTrans)
    th.start()

    sendToTrans()

    th.join()
