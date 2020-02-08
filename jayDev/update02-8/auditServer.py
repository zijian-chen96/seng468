from socket import *
import sys
import json
from xml.dom import minidom
from datetime import datetime
#xmllint --schema logfile.xsd --noout logsfile.xml

def main(root):
    sSocket = socket(AF_INET, SOCK_STREAM)
    print 'this is the audit server'

    sSocket.bind(("", 55571))
    sSocket.listen(5)
    print 'listening for connection'


    #print 'accepted'
    try:
        while True:
            connection, addr = sSocket.accept()
            # transactions = ""
            transactions = connection.recv(1024)
            if transactions == "GAMEOVER":
                break
            #transactionsList = transactions.split(',')
            transactionsDic = json.loads(transactions)

            print(transactionsDic, "calling detTage")

            if transactions:
                detTag(transactionsDic)
                #connection.send('next')

            #else: ##empty / no transactions received
                #break

        #print("Yhea man")
        xml_str = root.toprettyxml(indent='\t\t')

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
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    fundsChild(userCommandChild, data['funds'])
    #print "everything went through"

#trans,command,userid,stockname,server,types:userCommand-quote(2)
def userCommandChildren_2(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    stockSymbolChild(userCommandChild, data['stockname'])

#trans,command,username,stockname,funds,server,types:userCommand-buy(3)
def userCommandChildren_3(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    stockSymbolChild(userCommandChild, data['stockname'])
    fundsChild(userCommandChild, data['funds'])

#trans,command,username,server,types:userCommand-commitBuy(4)
def userCommandChildren_4(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])

#trans,command,username,stockname,server,types:userCommand-cancelSetBuy(5)
def userCommandChildren_5(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    stockSymbolChild(userCommandChild, data['stockname'])

#trans,command,username,stockname,stockprice,server,types:userCommand-setBuyTrigger(6)
def userCommandChildren_6(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    stockSymbolChild(userCommandChild, data['stockname'])
    fundsChild(userCommandChild, data['funds'])

#trans,command,username,filename,server,types:userCommand-dumplog1(7)
def userCommandChildren_7(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    filenameChild(userCommandChild, data['filename'])

#trans,command,filename,server,types:userCommand-dumplog2(8)
def userCommandChildren_8(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, getCurrTimestamp())
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    filenameChild(userCommandChild, data['filename'])


#trans,command,userid,stockname,stockprice,timestamp,cryptokey,server,types:quoteServer(9)
def quoteServerChildren_9(data):
    quoteServerChild = root.createElement('quoteServer')
    xml.appendChild(quoteServerChild)

    timestampChild(quoteServerChild, getCurrTimestamp())
    serverChild(quoteServerChild, data['server'])
    transactionNumChild(quoteServerChild, data['trans'])
    quoteServerTimeChild(quoteServerChild, data['quoteServerTime'])
    usernameChild(quoteServerChild, data['username'])
    stockSymbolChild(quoteServerChild, data['stockname'])
    priceChild(quoteServerChild, data['price'])
    cryptokeyChild(quoteServerChild, data['cryptokey'])


#trans,command,username,stockname,funds,server,types:systemEvent-database(10)
def systemEventChildren_10(data):
    systemEventChild = root.createElement('systemEvent')
    xml.appendChild(systemEventChild)

    timestampChild(systemEventChild, getCurrTimestamp())
    serverChild(systemEventChild, data['server'])
    transactionNumChild(systemEventChild, data['trans'])
    commandChild(systemEventChild, data['command'])
    usernameChild(systemEventChild, data['username'])
    stockSymbolChild(systemEventChild, data['stockname'])
    fundsChild(systemEventChild, data['funds'])

#trans,action,username,funds,server,types:accountTransaction-add(11)
def accountTransactionChildren_11(data):
    accountTransactionChild = root.createElement('accountTransaction')
    xml.appendChild(accountTransactionChild)

    timestampChild(accountTransactionChild, getCurrTimestamp())
    serverChild(accountTransactionChild, data['server'])
    transactionNumChild(accountTransactionChild, data['trans'])
    actionChild(accountTransactionChild, data['action'])
    usernameChild(accountTransactionChild, data['username'])
    fundsChild(accountTransactionChild, data['funds'])
    #print "everything went through"

#trans,command,username,stockname,server,types:systemEvent-cancelSetBuy(12)
def systemEventChildren_12(data):
    systemEventChild = root.createElement('systemEvent')
    xml.appendChild(systemEventChild)

    timestampChild(systemEventChild, getCurrTimestamp())
    serverChild(systemEventChild, data['server'])
    transactionNumChild(systemEventChild, data['trans'])
    commandChild(systemEventChild, data['command'])
    usernameChild(systemEventChild, data['username'])
    stockSymbolChild(systemEventChild, data['stockname'])

#trans,command,username,stockname,stockprice,server,types:systemEvent-setBuyTrigger(13)
def systemEventChildren_13(data):
    systemEventChild = root.createElement('systemEvent')
    xml.appendChild(systemEventChild)

    timestampChild(systemEventChild, getCurrTimestamp())
    serverChild(systemEventChild, data['server'])
    transactionNumChild(systemEventChild, data['trans'])
    commandChild(systemEventChild, data['command'])
    usernameChild(systemEventChild, data['username'])
    stockSymbolChild(systemEventChild, data['stockname'])
    fundsChild(systemEventChild, data['funds'])

def errorEventChildren(data):

    errorEventChild = root.createElement('errorEvent')
    xml.appendChild(errorEventChild)

    timestampChild(errorEventChild, getCurrTimestamp())
    serverChild(errorEventChild, data['server'])
    transactionNumChild(errorEventChild, data['trans'])
    commandChild(errorEventChild, data['command'])
    usernameChild(errorEventChild, data['username'])
    stockSymbolChild(errorEventChild, data['stockname'])
    fundsChild(errorEventChild, data['funds'])
    errorMessageChild(errorEventChild, data['errorMessage'])


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
    if data['types'] == 1:
        #types:userCommand-add(1)
        userCommandChildren_1(data)
    elif data['types'] == 2:
        #types:userCommand-quote(2)
        userCommandChildren_2(data)
    elif data['types'] == 3:
        #types:userCommand-buy(3)-sell(3)-setBuyAmount(3)-setSellAmount(3)
        userCommandChildren_3(data)
    elif data['types'] == 4:
        #types:userCommand-commitBuy(4)-commitSell(4)-cancelBuy(4)-cancelSell(4)
        userCommandChildren_4(data)
    elif data['types'] == 5:
        #types:userCommand-cancelSetBuy(5)-cancelSetSell(5)
        userCommandChildren_5(data)
    elif data['types'] == 6:
        #types:userCommand-setBuyTrigger(6)-setSellTrigger(6)
        userCommandChildren_6(data)
    elif data['types'] == 7:
        #types:userCommand-dumplog1(7)
        userCommandChildren_7(data)
    elif data['types'] == 8:
        #types:userCommand-dumplog2(8)
        userCommandChildren_8(data)
    elif data['types'] == 9:
        #types:quoteServer(9)
        quoteServerChildren_9(data)
    elif data['types'] == 10:
        #types:systemEvent-database(10)-setBuyAmount(10)-setSellAmount(10)
        systemEventChildren_10(data)
    elif data['types'] == 11:
        #types:accountTransaction-add(11)-remove(11)
        accountTransactionChildren_11(data)
    elif data['types'] == 12:
        #types:systemEvent-cancelSetBuy(12)-cancelSetSell(12)
        systemEventChildren_12(data)
    elif data['types'] == 13:
        #types:systemEvent-setBuyTrigger(13)-setSellTrigger(13)
        systemEventChildren_13(data)
    else:
        errorEventChild(data)

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
