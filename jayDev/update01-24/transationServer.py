from socket import *
import sys

def recvFromHttp(auditServerSocket):


    while True:
        print('Waitting for Connection...')

        connectSocket, addr = serverSocket.accept()

        try:
            while True:
                data = ''
                data = connectSocket.recv(1024)
                if data:
                    print("Data recv from HTTP Server: " + data)

                    dataFromQuote = commandControl(data)

                    #dataFromQuote = sendToQuote(data + '\r')
                    print("Data recv from Quote Server: " + dataFromQuote)
                    connectSocket.send(dataFromQuote) #Send back to HTTP Server
                    #auditServerSocket.send(dataFromQuote) #Send to Aduit Server

                else:
                    auditServerSocket.close()
                    break

            #connectSocket.close()
        except:
            connectSocket.send('Something Wrong!')
            connectSocket.close()

    serverSocket.close()

def sendToQuote(data):
    fromUser = data
    quoteServerSocket = socket(AF_INET,SOCK_STREAM)

    quoteServerSocket.connect(('quoteserve.seng.uvic.ca',4447))

    quoteServerSocket.send(fromUser)

    dataFromQuote = quoteServerSocket.recv(1024)

    quoteServerSocket.close()

    return dataFromQuote

def commandControl(data):
    dataList = data.split(',')

    if dataList[1] == "ADD":
        print("Data should be send direct to Aduit Server: " + data)
        auditServerSocket.send(data + ',1')
        return data
    elif dataList[1] == 'BUY':
        print("heloo" + data)
        auditServerSocket.send(data + ',1')
        newdata = dataList[3]+ ',' + dataList[2] + '\r'
        dataFromQuote = sendToQuote(newdata)
        auditServerSocket.send(data + ',' + dataFromQuote + ',4')
        print("aello" + data + ',' + dataFromQuote + ',4')
        return dataFromQuote
    elif dataList[1] == "SELL":
        auditServerSocket.send(data + ',1')
        newdata = dataList[3]+ ',' + dataList[2] + '\r'
        dataFromQuote = sendToQuote(newdata)
        auditServerSocket.send(data + ',' + dataFromQuote + ',4')
        print("bello" + data + ',' + dataFromQuote + ',4')
        return dataFromQuote

#def main(auditServerSocket):
    #recvFromHttp(auditServerSocket)
    #commandControl("ADD, jiosesdo, 100.00")

if __name__ == '__main__':
    serverSocket = socket(AF_INET, SOCK_STREAM)
    host = ''
    port = 44431
    s188 = "192.168.1.188"
    s15 = "10.0.2.15"

    serverSocket.bind((host,port))

    serverSocket.listen(5)

    auditServerSocket = socket(AF_INET, SOCK_STREAM)
    auditServerSocket.connect((s188,44430))

    #main(auditServerSocket)
    recvFromHttp(auditServerSocket)
