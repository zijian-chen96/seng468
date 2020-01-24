from socket import *
import sys

def recvFromHttp():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    host = ''
    port = 44431

    serverSocket.bind((host,port))

    serverSocket.listen(5)

    s = socket(AF_INET, SOCK_STREAM)
    s.connect(("192.168.1.188",44430))

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
                    s.send(dataFromQuote) #Send to Aduit Server

                else:
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
    dataList = data.split(', ')

    if dataList[0] == "ADD":
        print("Data should be send direct to Aduit Server: " + data)
        return data
    else:
        newdata = dataList[2]+ ', ' + dataList[1] + '\r'
        dataFromQuote = sendToQuote(newdata)
        return dataFromQuote

def main():
    recvFromHttp()
    #commandControl("ADD, jiosesdo, 100.00")

if __name__ == '__main__':
    main()
