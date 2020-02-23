import sys
import readline
import socket
import time
import queue
import threading



class Server(threading.Thread):
    def __init__(self, port, filename):
        threading.Thread.__init__(self)
        self.port = port
        self.filename = filename

    def jobServer01(self, newData):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('',50000))

        s.sendall(newData.encode())

        data = s.recv(10240).decode()

        s.close()


    def jobServer02(self, newData, iList, s):
        s.sendall(newData.encode())

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
        else:
            data = s.recv(10240).decode()

    def sendToTrans(self):
        alist = [line.rstrip() for line in open(self.filename)]

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('',self.port))

        transNum = 0
        for newData in alist:
            transNum += 1

            iList = newData.split(',')

            # newData = ''
            # newData = ','.join([str(transNum),i])

            if iList[1] in ['SET_BUY_AMOUNT', 'CANCEL_SET_BUY', 'SET_BUY_TRIGGER', 'SET_SELL_AMOUNT', 'CANCEL_SET_SELL', 'SET_SELL_TRIGGER']:
                self.jobServer01(newData)
            else:
                self.jobServer02(newData, iList, s)

            print(transNum)
        s.close()

    def run(self):
        self.sendToTrans()

if __name__=="__main__":
    filename1 = "workload1.txt"
    server1 = Server(50001, filename1)
    server1.start()
    server1.join()

    print('finished...01')
