from socket import *
import threading
import mysql.connector
import sys
from datetime import datetime
from decimal import Decimal
import time
import Queue as queue
import json
#sudo lsof -i :50000
#sudo kill -9 50000

class jobSystem(threading.Thread):
    def __init__(self, jobQueue, finQueue, sSocket):
        threading.Thread.__init__(self)
        self.jobQueue = jobQueue
        self.finQueue = finQueue
        self.sSocket = sSocket

    def run(self):
        cSocket, addr = self.sSocket.accept()
        count = 0
        try:
            while True:
                if self.jobQueue.qsize() < 999:
                    data = ""
                    data = cSocket.recv(1024)
                    dataList = data.split('\n')
                    if len(dataList) > 1 and dataList[-1] != '':
                        print(dataList)
                        for i in dataList:
                            self.jobQueue.put(i)

                    cSocket.send('next')

                else:
                    data = ""
                    data = cSocket.recv(1024)
                    dataList = data.split('\n')
                    if len(dataList) > 1 and dataList[-1] != '':
                        print(dataList)
                        for i in dataList:
                            self.jobQueue.put(i)

                    else:
                        self.jobQueue.put(dataList[0])

                    for i in self.jobQueue.queue:
                        count += 1
                        print(i + ' --- '+ str(count))
                    self.jobQueue.queue.clear()
                    print(jobQueue.qsize())
                    cSocket.send('next')

        except:
            #print('ERROR: jobSystem')
            sys.exit()


if __name__ == '__main__':

    sSocket = socket(AF_INET, SOCK_STREAM)
    host = ''
    port = 50000
    sSocket.bind((host,port))
    sSocket.listen(10)

    #thread 1 only use to recv command from http
    jobQueue = queue.Queue(maxsize = 10000)
    #thread 1 only use for send response back to http
    finQueue = queue.Queue(maxsize = 10000)

    #thread 2 only use to sent the log to AuditServer
    logQueue = queue.Queue(maxsize = 10000)


    jobSystem = jobSystem(jobQueue, finQueue, sSocket)
    jobSystem.start()
