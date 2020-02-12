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
s188 = "192.168.1.188"
s161 = "192.168.1.161"
s198 = "192.168.1.198"
s33 = "192.168.0.33"


# def recvall(s):
#     buffer_size = 10240
#     data = b''
#     while True:
#         part = s.recv(buffer_size)
#         data += part
#         if len(part) < buffer_size:
#             break
#     return data


def readFile():
    alist = [line.rstrip().split(' ')[1] for line in open(filename3)]
    sendToTrans(alist)

def sendToTrans(alist):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((s33,50007))

    transNum = 0
    for i in alist:
        transNum += 1
        print('---------------------- ' + str(transNum) + ' -----------------------')
        newData = ''
        newData = ','.join([str(transNum),i])
        print('newData send -- ' + newData)
        #s.send(newData)
        #data = s.recv(1024)

        iList = i.split(',')

        print("iLst is -- " + str(iList))

        if iList[0] == 'DUMPLOG'and len(iList) == 3:
            f = open(iList[2], "w+")
            s.send(newData)
            while True:
                data = s.recv(10240)
                if newData == "the end":
                    break
                else:
                    f.write(data)

            f.close()

        elif iList[0] == 'DUMPLOG' and len(iList) == 2:
            f = open(iList[2], "w+")
            s.send(newData)
            while True:
                data = s.recv(10240)
                if newData == "the end":
                    break
                else:
                    f.write(data)

            f.close()

        elif iList[0] == "DISPLAY_SUMMARY":
            s.send(newData)
            while True:
                data = s.recv(1024)
                print(data)
                newData = data[-7:]
                if newData == "the end":
                    break

        else:
            s.send(newData)
            data = s.recv(10240)
            if data:
                print(data)

    s.close()

def main():
    readFile()

if __name__=="__main__":
    main()
