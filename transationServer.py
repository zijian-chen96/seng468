from socket import *
import sys

def recvFromHttp():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    host = ''
    port = 44430

    serverSocket.bind((host,port))

    serverSocket.listen(5)

    while True:
        print('Waitting for Connection...')

        connectSocket, addr = serverSocket.accept()

        try:
            data = connectSocket.recv(1024)
            print(data)

            connectSocket.send('200 OK ' + data)

            #dataFromQuote = sendToQuote(data)

            #connectSocket.send(dataFromQuote)

            connectSocket.close()
        except:
            connectSocket.send('Something Wrong!')
            connectSocket.close()

    serverSocket.close()

def sendToQuote(data):
    fromUser = data
    quoteServerSocket = socket((AF_INET,SOCK_STREAM))

    quoteServerSocket.connect(('quoteserve.seng.uvic.ca',4447))

    quoteServerSocket.send(fromUser)

    dataFromQuote = quoteServerSocket.recv(1024)
    print(dataFromQuote)

    quoteServerSocket.close()

    return dataFromQuote


def main():
    recvFromHttp()

if __name__ == '__main__':
    main()
