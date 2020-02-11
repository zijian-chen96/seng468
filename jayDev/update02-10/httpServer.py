import sys
import readline
import socket
import time
import threading

filename0 = "example.txt"
filename = "user1.txt"
filename2 = "user2.txt"
filename3 = "user10.txt"
s188 = "192.168.1.188"
s161 = "192.168.1.161"
s198 = "192.168.1.198"


# def recvall(s):
#     buffer_size = 10240
#     data = b''
#     while True:
#         part = s.recv(buffer_size)
#         data += part
#         if len(part) < buffer_size:
#             break
#     return data

# class recvSystem(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#
#     def run(self):
#         rSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         rSocket.connect((s198,51007))
#
#         while True:
#             data = rSocket.recv(1024)
#
#             iList = data.split(',')
#
#             print("data recv -- " + str(iList))



def readFile():
    alist = [line.split(' ')[1] for line in open(filename3)]

    sendToTrans(alist)

def sendToTrans(alist):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((s198,50010))

    transNum = 0
    recvNum = 0
    for i in alist:
        transNum += 1

        newData = ''
        newData = ','.join([str(transNum),i])
        print('newData send -- ' + newData)
        #s.send(newData)
        #data = s.recv(1024)


        iList = i.split(',')

        print("iLst is -- " + str(iList))
        if iList[0] == 'DUMPLOG'and len(iList) == 3:
            s.send(newData)
            while True:
                if recvNum == 10000:
                    recvNum += 1
                    f = open(iList[2], "w+")
                    f.write(data)
                    f.close()
                    break

                else:
                    data = s.recv(1024)
                    recvNum += 1
                    print(data)


        elif iList[0] == 'DUMPLOG' and len(iList) == 2:
            s.send(newData)
            data = s.recv(1024)
            transNum += 1
            f = open(iList[1], "w+")
            f.write(data)
            f.close()

        elif iList[0] == "DISPLAY_SUMMARY":
            s.send(newData)
            data = s.recv(1024)
            recvNum += 1
        else:
            s.send(newData)
            data = s.recv(1024)
            recvNum += 1
            if data:
                print(data)


    s.close()

def main():
    readFile()

if __name__=="__main__":
    # recvSystem = recvSystem()
    # recvSystem.start()
    main()
