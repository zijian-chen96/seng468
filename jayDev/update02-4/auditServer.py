from socket import *
import sys
from xml.dom import minidom
from datetime import datetime
#xmllint --schema logfile.xsd --noout yourlogfile.xml

def main(root):
    sSocket = socket(AF_INET, SOCK_STREAM)
    print 'this is the audit server'

    sSocket.bind(("", 55558))
    sSocket.listen(5)
    print 'listening for connection'


    connection, addr = sSocket.accept()
    print 'accepted'
    try:
        while True:
            # transactions = ""
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

        save_path_file = "logsfile.xml"

        with open(save_path_file, "w+") as f:
            f.write(xml_str)

    except IOError:
        connection.send("error")
        connection.close()
    connection.close()
    sSocket.close()

#trans,command,username,funds,server,types:userCommand-add(1)
def userCommandChildren_1(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data[4])
    transactionNumChild(userCommandChild, data[0])
    commandChild(userCommandChild, data[1])
    usernameChild(userCommandChild, data[2])
    fundsChild(userCommandChild, data[3])
    #print "everything went through"

#trans,command,userid,stockname,server,types:userCommand-quote(2)
def userCommandChildren_2(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data[4])
    transactionNumChild(userCommandChild, data[0])
    commandChild(userCommandChild, data[1])
    usernameChild(userCommandChild, data[2])
    stockSymbolChild(userCommandChild, data[3])

#trans,command,username,stockname,funds,server,types:userCommand-buy(3)
def userCommandChildren_3(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data[5])
    transactionNumChild(userCommandChild, data[0])
    commandChild(userCommandChild, data[1])
    usernameChild(userCommandChild, data[2])
    stockSymbolChild(userCommandChild, data[3])
    fundsChild(userCommandChild, data[4])

#trans,command,username,server,types:userCommand-commitBuy(4)
def userCommandChildren_4(data):
    print("---------"+str(data)+"-----------")
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data[3])
    transactionNumChild(userCommandChild, data[0])
    commandChild(userCommandChild, data[1])
    usernameChild(userCommandChild, data[2])

#trans,command,username,stockname,server,types:userCommand-cancelSetBuy(5)
def userCommandChildren_5(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data[4])
    transactionNumChild(userCommandChild, data[0])
    commandChild(userCommandChild, data[1])
    usernameChild(userCommandChild, data[2])
    stockSymbolChild(userCommandChild, data[3])

#trans,command,username,stockname,stockprice,server,types:userCommand-setBuyTrigger(6)
def userCommandChildren_6(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data[5])
    transactionNumChild(userCommandChild, data[0])
    commandChild(userCommandChild, data[1])
    usernameChild(userCommandChild, data[2])
    stockSymbolChild(userCommandChild, data[3])
    priceChild(userCommandChild, data[4])

#trans,command,username,filename,server,types:userCommand-dumplog1(7)
def userCommandChildren_7(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data[4])
    transactionNumChild(userCommandChild, data[0])
    commandChild(userCommandChild, data[1])
    usernameChild(userCommandChild, data[2])
    filenameChild(userCommandChild,data[3])

#trans,command,filename,server,types:userCommand-dumplog2(8)
def userCommandChildren_8(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data[3])
    transactionNumChild(userCommandChild, data[0])
    commandChild(userCommandChild, data[1])
    filenameChild(userCommandChild, data[2])


#trans,command,userid,stockname,stockprice,timestamp,cryptokey,server,types:quoteServer(9)
def quoteServerChildren_9(data):
    quoteServerChild = root.createElement('quoteServer')
    xml.appendChild(quoteServerChild)

    timestampChild(quoteServerChild, getCurrTimestamp())
    serverChild(quoteServerChild, data[7])
    transactionNumChild(quoteServerChild, data[0])
    quoteServerTimeChild(quoteServerChild, data[5])
    usernameChild(quoteServerChild, data[2])
    stockSymbolChild(quoteServerChild, data[3])
    priceChild(quoteServerChild, data[4])
    cryptokeyChild(quoteServerChild, data[6])


#trans,command,username,stockname,funds,server,types:systemEvent-database(10)
def systemEventChildren_10(data):
    systemEventChild = root.createElement('systemEvent')
    xml.appendChild(systemEventChild)

    timestampChild(systemEventChild, getCurrTimestamp())
    serverChild(systemEventChild, data[5])
    transactionNumChild(systemEventChild, data[0])
    commandChild(systemEventChild, data[1])
    usernameChild(systemEventChild, data[2])
    stockSymbolChild(systemEventChild, data[3])
    fundsChild(systemEventChild, data[4])

#trans,command,username,funds,server,types:accountTransaction-add(11)
def accountTransactionChildren_11(data):
    print('----------enter 11: ' +str(data)+'--------------')
    accountTransactionChild = root.createElement('accountTransaction')
    print(data)
    xml.appendChild(accountTransactionChild)
    print(data)
    timestampChild(accountTransactionChild, getCurrTimestamp())
    print(data)
    serverChild(accountTransactionChild, data[4])
    print(data)
    transactionNumChild(accountTransactionChild, data[0])
    print(data)
    actionChild(accountTransactionChild, 'add')
    print(data)
    usernameChild(accountTransactionChild, data[2])
    print(data)
    fundsChild(accountTransactionChild, data[3])
    #print "everything went through"

#trans,command,username,stockname,server,types:systemEvent-cancelSetBuy(12)
def systemEventChildren_12(data):
    systemEventChild = root.createElement('systemEvent')
    xml.appendChild(systemEventChild)

    timestampChild(systemEventChild, getCurrTimestamp())
    serverChild(systemEventChild, data[4])
    transactionNumChild(systemEventChild, data[0])
    commandChild(systemEventChild, data[1])
    usernameChild(systemEventChild, data[2])
    stockSymbolChild(systemEventChild, data[3])

#trans,command,username,stockname,stockprice,server,types:systemEvent-setBuyTrigger(13)
def systemEventChildren_13(data):
    systemEventChild = root.createElement('systemEvent')
    xml.appendChild(systemEventChild)

    timestampChild(systemEventChild, getCurrTimestamp())
    serverChild(systemEventChild, data[5])
    transactionNumChild(systemEventChild, data[0])
    commandChild(systemEventChild, data[1])
    usernameChild(systemEventChild, data[2])
    stockSymbolChild(systemEventChild, data[3])
    fundsChild(systemEventChild, data[4])

#trans,command,username,funds,server,types:accountTransaction-remove(14)
def accountTransactionChildren_14(data):
    print('----------enter 11: ' +str(data)+'--------------')
    accountTransactionChild = root.createElement('accountTransaction')
    print(data)
    xml.appendChild(accountTransactionChild)
    print(data)
    timestampChild(accountTransactionChild, getCurrTimestamp())
    print(data)
    serverChild(accountTransactionChild, data[4])
    print(data)
    transactionNumChild(accountTransactionChild, data[0])
    print(data)
    actionChild(accountTransactionChild, 'remove')
    print(data)
    usernameChild(accountTransactionChild, data[2])
    print(data)
    fundsChild(accountTransactionChild, data[3])
    #print "everything went through"

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

def quoteServerTimeChild(parent, data):
    quoteServerTimeChild = root.createElement('quoteServerTime')
    quoteServerTimeChild.appendChild(root.createTextNode(data))
    parent.appendChild(quoteServerTimeChild)

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

def filenameChild(parent, data):
    filenameChild = root.createElement('filename')
    filenameChild.appendChild(root.createTextNode(data))
    parent.appendChild(filenameChild)

def errorMessageChild(parent, data):
    errorMessageChild= root.createElement('errorMessage')
    errorMessageChild.appendChild(root.createTextNode(data))
    parent.appendChild(errorMessageChild)

def detTag(data): #determine the tag of the input
    tag = ''
    if data[-1] == "1":
        #types:userCommand-add(1)
        userCommandChildren_1(data)
    elif data[-1] == "2":
        #types:userCommand-quote(2)
        userCommandChildren_2(data)
    elif data[-1] == "3":
        #types:userCommand-buy(3)-sell(3)-setBuyAmount(3)-setSellAmount(3)
        userCommandChildren_3(data)
    elif data[-1] == "4":
        #types:userCommand-commitBuy(4)-commitSell(4)-cancelBuy(4)-cancelSell(4)
        userCommandChildren_4(data)
    elif data[-1] == "5":
        #types:userCommand-cancelSetBuy(5)-cancelSetSell(5)
        userCommandChildren_5(data)
    elif data[-1] == "6":
        #types:userCommand-setBuyTrigger(6)-setSellTrigger(6)
        userCommandChildren_6(data)
    elif data[-1] == "7":
        #types:userCommand-dumplog1(7)
        userCommandChildren_7(data)
    elif data[-1] == "8":
        #types:userCommand-dumplog2(8)
        userCommandChildren_8(data)
    elif data[-1] == "9":
        #types:quoteServer(9)
        quoteServerChildren_9(data)
    elif data[-1] == "10":
        #types:systemEvent-database(10)-setBuyAmount(10)-setSellAmount(10)
        systemEventChildren_10(data)
    elif data[-1] == "11":
        print('----------' +str(data[-1])+'--------------')
        #types:accountTransaction-add(11)-remove(11)
        accountTransactionChildren_11(data)
    elif data[-1] == "12":
        #types:systemEvent-cancelSetBuy(12)-cancelSetSell(12)
        systemEventChildren_12(data)
    elif data[-1] == "13":
        #types:systemEvent-setBuyTrigger(13)-setSellTrigger(13)
        systemEventChildren_13(data)
    elif data[-1] == "14":
        accountTransactionChildren_14(data)
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
