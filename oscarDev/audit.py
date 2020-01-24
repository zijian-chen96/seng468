from socket import *
import sys

def main():
    sSocket = socket(AF_INET, SOCK_STREAM)
    print 'this is the audit server'

    sSocket.bind(("", 44430))
    sSocket.listen(5)
    print 'listening for connection'


    connection, addr = sSocket.accept()
    try:
        while True:
            transactions = ""
            transactions = connection.recv(1024)
            transactions = transactions.split(',', 1)
            tag = detTag(transactions[0])
            tolog(tag, transactions[1])
            if transactions[2]:
                print(transactions[2])
            else: ##empty / no transactions received
                break

    except IOError:
        connection.send("error")
        connection.close()
    connection.close()
    sSocket.close()

def toLog(tag,command): #use tag to write the logs
    #write to log file
        #type
        #timestamp
        #server
        #transaction number
        #command
        #username
    return
def detTag(typ): #determine the tag of the input
    tag = ''
    if typ = 1:
        tag = "userCommand"
    else if typ = 2:
        tag = "accountTransaction"
    else if typ = 3:
        tag = "systemEvent"
    else if typ = 4:
        tag = "quoteServer"
    else:
        tag = "errorEvent"
    return tag

if __name__=="__main__":
    main()
