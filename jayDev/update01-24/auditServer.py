from socket import *
import sys
from xml.dom import minidom
from datetime import datetime

def main(root):
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
            transactionsList = transactions.split(',')
            print(transactionsList, "calling detTage")


            #tolog(tag, transactions[1])

            if transactions:
                detTag(transactionsList)
                #print(transactions)
            else: ##empty / no transactions received
                break

        #print("Yhea man")
        xml_str = root.toprettyxml(indent='\t')

        save_path_file = "testxmlfile.xml"

        with open(save_path_file, "w") as f:
            f.write(xml_str)

    except IOError:
        connection.send("error")
        connection.close()
    connection.close()
    sSocket.close()

def userCommandChildren(data): #[transNum, command, username, funds, types]
    #dataList = data.split(',')
    #print "userCommandChild = root.createElement('userCommand')"
    userCommandChild = root.createElement('userCommand')
    #print "worked"
    #print "xml.appendChild(userCommandChild)"
    xml.appendChild(userCommandChild)
    #print "worked"

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, "CLT1")
    transactionNumChild(userCommandChild, data[0])
    commandChild(userCommandChild, data[1])
    usernameChild(userCommandChild, data[2])
    fundsChild(userCommandChild, data[3])
    print "everything went through"

def accountTransactionChildren(data):

    accountTransactionChild = root.createElement('accountTransaction')
    xml.appendChild(accountTransactionChild)

    timestampChild(accountTransactionChild, data)
    serverChild(accountTransactionChild, data)
    transactionNumChild(accountTransactionChild, data)
    actionChild(accountTransactionChild, data)
    usernameChild(accountTransactionChild, data)
    fundsChild(accountTransactionChild, data)
    print "everything went through"

def systemEventChildren(data):

    systemEventChild = root.createElement('systemEvent')
    xml.appendChild(systemEventChild)

    timestampChild(systemEventChild, data)
    serverChild(systemEventChild, data)
    transactionNumChild(systemEventChild, data)
    commandChild(systemEventChild, data)
    usernameChild(systemEventChild, data)
    stockSymbolChild(systemEventChild, data)
    fundsChild(systemEventChild, data)

def quoteServerChildren(data): #[transNum, command, username, stack, funds, price,---
                               #---stack, username, qouteServerTime, cryptokey, types]

    qouteServerChild = root.createElement('qouteServer')
    xml.appendChild(qouteServerChild)

    timestampChild(qouteServerChild, getCurrTimestamp())
    serverChild(qouteServerChild, "QSRV1")
    transactionNumChild(qouteServerChild, data[0])
    qouteServerTimeChild(qouteServerChild, data[8])
    usernameChild(qouteServerChild, data[2])
    stockSymbolChild(qouteServerChild, data[3])
    priceChild(qouteServerChild, data[5])
    cryptokeyChild(qouteServerChild, data[9])
    print "everything went through"

def errorEventChildren(data):

    errorEventChild = root.createElement('errorEvent')
    xml.appendChild(errorEventChild)

    timestampChild(errorEventChild, data)
    serverChild(errorEventChild, data)
    transactionNumChild(errorEventChild, data)
    commandChild(errorEventChild, data)
    usernameChild(errorEventChild, data)
    stockSymbolChild(errorEventChild, data)
    fundsChild(errorEventChild, data)
    errorMessageChild(errorEventChild, data)


def timestampChild(parent, data):
    #print "timestampChild"
    timestampChild = root.createElement('timestamp')
    timestampChild.appendChild(root.createTextNode(data))
    parent.appendChild(timestampChild)

def serverChild(parent, data):
    serverChild = root.createElement('server')
    serverChild.appendChild(root.createTextNode(data))
    parent.appendChild(serverChild)

def transactionNumChild(parent, data):
    transactionNumChild = root.createElement('transactionNum')
    transactionNumChild.appendChild(root.createTextNode(data))
    parent.appendChild(transactionNumChild)

def commandChild(parent, data):
    commandChild = root.createElement('command')
    commandChild.appendChild(root.createTextNode(data))
    parent.appendChild(commandChild)

def usernameChild(parent, data):
    usernameChild = root.createElement('username')
    usernameChild.appendChild(root.createTextNode(data))
    parent.appendChild(usernameChild)

def fundsChild(parent, data):
    fundsChild = root.createElement('funds')
    fundsChild.appendChild(root.createTextNode(data))
    parent.appendChild(fundsChild)

def actionChild(parent, data):
    actionChild = root.createElement('action')
    actionChild.appendChild(root.createTextNode(data))
    parent.appendChild(actionChild)

def qouteServerTimeChild(parent, data):
    qouteServerTimeChild = root.createElement('qouteServerTime')
    qouteServerTimeChild.appendChild(root.createTextNode(data))
    parent.appendChild(qouteServerTimeChild)

def stockSymbolChild(parent, data):
    stockSymbolChild = root.createElement('stockSymbol')
    stockSymbolChild.appendChild(root.createTextNode(data))
    parent.appendChild(stockSymbolChild)

def priceChild(parent, data):
    priceChild = root.createElement('price')
    priceChild.appendChild(root.createTextNode(data))
    parent.appendChild(priceChild)

def cryptokeyChild(parent, data):
    cryptokeyChild = root.createElement('cryptokey')
    cryptokeyChild.appendChild(root.createTextNode(data))
    parent.appendChild(cryptokeyChild)

def errorMessageChild(parent, data):
    errorMessageChild= root.createElement('errorMessage')
    errorMessageChild.appendChild(root.createTextNode(data))
    parent.appendChild(errorMessageChild)

def detTag(data): #determine the tag of the input
    tag = ''
    if data[-1] == '1':
        #print "calling userCommandChildren"
        userCommandChildren(data)
    elif data[-1] == '2':
        #print " calling accountTransaction"
        tag = "accountTransaction"
    elif data[-1] == '3':
        tag = "systemEvent"
    elif data[-1] == '4':
        quoteServerChildren(data)
    else:
        tag = "errorEvent"

def getCurrTimestamp():
    dateTimeObj = datetime.now()
    #print(dateTimeObj)

    timestampStr = dateTimeObj.strptime(str(dateTimeObj), '%Y-%m-%d %H:%M:%S.%f').strftime('%s.%f')
    return str(int(float(timestampStr) * 1000))

if __name__=="__main__":
    root = minidom.Document()
    xml = root.createElement('log')
    root.appendChild(xml)
    main(root)
