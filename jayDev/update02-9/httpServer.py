import sys
import readline
import socket
import time

filename0 = "example.txt"
filename = "user1.txt"
filename2 = "user2.txt"
filename3 = "user10.txt"
s188 = "192.168.1.188"
s161 = "192.168.1.161"
s198 = "192.168.1.198"

def recvall(s):
    buffer_size = 10240
    data = b''
    while True:
        part = s.recv(buffer_size)
        # print(part)
        data += part
        if len(part) < buffer_size:
            check = 1
            break
    return data

def readFile():
    alist = [line.strip().split(' ')[1] for line in open(filename3)]

    #print(alist)
    sendToTrans(alist)

def sendToTrans(alist):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((s198,50067))

    transNum = 0
    check = 1
    for i in alist:
        transNum += 1

        #print(i)
        newData = ''
        newData = ','.join([str(transNum),i])
        print('newData recv' + newData)

        # s.send(newData)
        # print 'sent'
        #time.sleep(0.01)
        # data = s.recv(1024)
        # print('data recv' + data)

        iList = i.split(',')
        # if iList[0] == "DISPLAY_SUMMARY":
        #     while data != "200 OK":
        #         print('whileing')
        #         print('whileing else')
        #         data = s.recv(1024)
        #         print('data recv in while' + data)
        print("iLst is -- " + str(iList))
        if iList[0] == 'DUMPLOG'and len(iList) == 3:
            f = open(iList[2], "w+")
            #print(data)
            f.write(i)
            f.close()

        elif iList[0] == 'DUMPLOG' and len(iList) == 2:
            f = open(iList[1], "w+")
            f.write(i)
            f.close()

        elif iList[0] == "DISPLAY_SUMMARY":
            check2 = 2
            s.send(newData)
            print 'sent'
            data = recvall(s)
            print("-------------elif--------------" )

        else:
            if check == 1:
                s.send(newData)
                print 'sent in else'
                data = s.recv(1024)
                if data:
                    print("------------else-----------")

    s.close()

def main():
    readFile()

if __name__=="__main__":
    main()
