from socket import *
import sys
###### ip 192.168.1.188

def main():
    #cSocket = socket(AF_INET, SOCK_STREAM) #for quote server
    #cSocket.connect(('quoteserve.seng.uvic.ca',4447))
    sSocket = socket(AF_INET, SOCK_STREAM) #for clients
    print ' this is the transaction server'

    #server socket
    sSocket.bind(("", 44431))
    sSocket.listen(4)
    print 'listen for connections'

    while True:
        #establish connections
        print 'connecting'
        #connectionSocket, addr = sSocket.accept()
        print 'connected'
        print("\nEnter: StockSYM, userid")
        print("  Invalid entry will return 'NA' for userid.")
        print("  Returns: quote,sym,userid,timestamp,cryptokey\n")
        f = open("transaction.txt", "w+")
        try:
            #recieve up to 1k data from http server
            connectionSocket, addr = sSocket.accept()
            while True:
                userCommand = connectionSocket.recv(1024)
                f.write(userCommand + "\n")
                cSocket = socket(AF_INET, SOCK_STREAM) #for quote server
                cSocket.connect(('quoteserve.seng.uvic.ca',4447))
                print(userCommand)
                if userCommand:
                    cSocket.send(userCommand + "\r")
                    data = cSocket.recv(1024)
                    f.write(data + "\n")
                    print 'data sent to quote server'
                    print (data)

                    #print(userCommand)
                    #getQuote(userCommand)
                    print 'not sent'
                    connectionSocket.send(data)
                    print 'sent'
                    connectionSocket.send("\r\n".encode())
                else:
                    print 'no more commands.'
                    break
                cSocket.close()
            #connectionSocket.close()
        except IOError:
            connectionSocket.send("error")
            connectionSocket.close()
    f.close()
    cSocket.close()
    sSocket.close()


if __name__=="__main__":
    main()
