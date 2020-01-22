from socket import *
import sys

def sendToTrans():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    host = '10.0.0.2'
    port = 44430

    serverSocket.connect((host,port))

    serverSocket.sendall("Hello World!")

    data = serverSocket.recv(1000)

    print(data)

def main():
    sendToTrans()

if __name__ == '__main__':
    main()
