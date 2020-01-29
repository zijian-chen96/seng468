from socket import *
import threading
import sys


class AuditServer(threading.Thread):
    def __init__(self, logQueue, auditSocket):
        threading.Thread.__init__(self)
        self.logQueue = logQueue
        self.auditSocket = auditSocket

    def run(self):
        while True:
            if len(logQueue) != 0:
                data = logQueue.pop(0)
                print("This data must send to aduit server: " + data)
                auditSocket.send(data)


def sendToQuote(data):
    fromUser = data
    quoteServerSocket = socket(AF_INET,SOCK_STREAM)

    quoteServerSocket.connect(('quoteserve.seng.uvic.ca',4447))

    quoteServerSocket.send(fromUser)

    dataFromQuote = quoteServerSocket.recv(1024)

    quoteServerSocket.close()

    return dataFromQuote


def recvFromHttp():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    host = ''
    port = 44430

    serverSocket.bind((host,port))

    serverSocket.listen(5)

    print('Waitting for Connection...')

    connectSocket, addr = serverSocket.accept()

    try:
        while True:
            data = ''
            data = connectSocket.recv(1024)

            if data:
                print("Data recv from HTTP Server: " + data)

                dataFromQuote = commandControl(data)

                print("Data recv from Quote Server: " + dataFromQuote)

                connectSocket.send(dataFromQuote) #Send back to HTTP Server

            else:
                auditSocket.close()
                break


    except:
            connectSocket.send('Something Wrong!')
            connectSocket.close()

    serverSocket.close()


def commandControl(data):
    dataList = data.split(',')

    if dataList[1] == "ADD":
        print("Data should be send direct to Aduit Server: " + data)
        logQueue.append(data + ',1')
        return data
    elif dataList[1] == 'BUY':
        print("heloo" + data)
        logQueue.append(data + ',1')
        newdata = dataList[3]+ ',' + dataList[2] + '\r'
        dataFromQuote = sendToQuote(newdata)
        logQueue.append(data + ',' + dataFromQuote + ',4')
        print("aello" + data + ',' + dataFromQuote + ',4')
        return dataFromQuote
    elif dataList[1] == "SELL":
        logQueue.append(data + ',1')
        newdata = dataList[3]+ ',' + dataList[2] + '\r'
        dataFromQuote = sendToQuote(newdata)
        logQueue.append(data + ',' + dataFromQuote + ',4')
        print("bello" + data + ',' + dataFromQuote + ',4')
        return dataFromQuote


if __name__ == '__main__':
    logQueue = []
    auditIP = "192.168.1.188"
    auditPort = 44432

    auditSocket = socket(AF_INET, SOCK_STREAM)
    auditSocket.connect((auditIP,auditPort))

    AuditServer = AuditServer(logQueue, auditSocket)
    AuditServer.start()

    recvFromHttp()
