import sys
import readline
import socket

filename = "example.txt"
s188 = "192.168.1.188"
s161 = "192.168.1.161"
s198 = "192.168.1.198"

def readFile():
    alist = [line.rstrip() for line in open(filename)]
    print(alist)
    sendToTrans(alist)

def sendToTrans(alist):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((s198,44430))

    transNum = 0
    for i in alist:
        transNum += 1

        s.send(str(transNum) + ',' + i)
        print(i)
        data = s.recv(1024)
        if data:
            print (data)

    s.close()

def main():
    readFile()

if __name__=="__main__":
    main()
