from socket import *
import sys
from xml.dom import minidom
from datetime import datetime
import json
import queue
import threading
#xmllint --schema logfile.xsd --noout logsfile.xml


class logServer(threading.Thread):
    def __init__(self, logQueue):
        threading.Thread.__init__(self)
        self.logQueue = logQueue

    def run(self):
        sSocket = socket(AF_INET, SOCK_STREAM)
        #print('this is the audit server')

        sSocket.bind(("", 51000))
        sSocket.listen(10)
        #print('listening for connection')

        #print('accepted')

        try:
            while True:
                connection, addr = sSocket.accept()

                transactions = ""
                transactions = connection.recv(1024).decode()
                if transactions != "":
                    #print(str(transactions))
                    transactionsDic = json.loads(transactions)
                    self.logQueue.put(transactionsDic)
        except:
            print('error 11')
            connection.send("error")
            connection.close()
        print('error 22')
        connection.close()
        sSocket.close()


def main(root):
    xml_str = root.toprettyxml()

    save_path_file = "logsfile.xml"

    with open(save_path_file, 'ab') as f:

        f.write(xml_str.encode())

    #checkFinal = 0
    while True:
        # if checkFinal == 1 and logQueue.empty() == True:
        #     with open('logsfile.xml', 'a') as f:
        #         f.write('</log>')
        #     break

        if logQueue.empty() != True:
            #sb = transactions.split("")
            #transactionsList = [s.strip() for s in sb]
            transactionsDic = logQueue.get()
            node = detTag(transactionsDic)
            xml_str = node.toprettyxml(indent='\t\t')
            with open('logsfile.xml', 'ab') as f:
                f.write(xml_str.encode())
            # try
            #     if transactionsDic['command'] == "DUMPLOG":
            #         checkFinal = 1
            # except:
            #     continue
            #trans,command,username,funds,server,types:userCommand-add(1)
def userCommandChildren_1(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, data['timestamp'])
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    fundsChild(userCommandChild, data['funds'])
    return userCommandChild

#trans,command,userid,stockname,server,types:userCommand-quote(2)
def userCommandChildren_2(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, data['timestamp'])
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    stockSymbolChild(userCommandChild, data['stockname'])
    return userCommandChild

#trans,command,username,stockname,funds,server,types:userCommand-buy(3)
def userCommandChildren_3(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, data['timestamp'])
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    stockSymbolChild(userCommandChild, data['stockname'])
    fundsChild(userCommandChild, data['funds'])
    return userCommandChild

#trans,command,username,server,types:userCommand-commitBuy(4)
def userCommandChildren_4(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, data['timestamp'])
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    return userCommandChild

#trans,command,username,stockname,server,types:userCommand-cancelSetBuy(5)
def userCommandChildren_5(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, data['timestamp'])
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    stockSymbolChild(userCommandChild, data['stockname'])
    return userCommandChild

#trans,command,username,stockname,stockprice,server,types:userCommand-setBuyTrigger(6)
def userCommandChildren_6(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, data['timestamp'])
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    stockSymbolChild(userCommandChild, data['stockname'])
    fundsChild(userCommandChild, data['funds'])
    return userCommandChild

#trans,command,username,filename,server,types:userCommand-dumplog1(7)
def userCommandChildren_7(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, data['timestamp'])
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    usernameChild(userCommandChild, data['username'])
    filenameChild(userCommandChild, data['filename'])
    return userCommandChild

#trans,command,filename,server,types:userCommand-dumplog2(8)
def userCommandChildren_8(data):
    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, data['timestamp'])
    serverChild(userCommandChild, data['server'])
    transactionNumChild(userCommandChild, data['trans'])
    commandChild(userCommandChild, data['command'])
    filenameChild(userCommandChild, data['filename'])
    return userCommandChild

#trans,command,userid,stockname,stockprice,timestamp,cryptokey,server,types:quoteServer(9)
def quoteServerChildren_9(data):
    quoteServerChild = root.createElement('quoteServer')
    xml.appendChild(quoteServerChild)

    timestampChild(quoteServerChild, data['timestamp'])
    serverChild(quoteServerChild, data['server'])
    transactionNumChild(quoteServerChild, data['trans'])
    quoteServerTimeChild(quoteServerChild, data['quoteServerTime'])
    usernameChild(quoteServerChild, data['username'])
    stockSymbolChild(quoteServerChild, data['stockname'])
    priceChild(quoteServerChild, data['price'])
    cryptokeyChild(quoteServerChild, data['cryptokey'])
    return quoteServerChild

#trans,command,username,stockname,funds,server,types:systemEvent-database(10)
def systemEventChildren_10(data):
    systemEventChild = root.createElement('systemEvent')
    xml.appendChild(systemEventChild)

    timestampChild(systemEventChild, data['timestamp'])
    serverChild(systemEventChild, data['server'])
    transactionNumChild(systemEventChild, data['trans'])
    commandChild(systemEventChild, data['command'])
    usernameChild(systemEventChild, data['username'])
    stockSymbolChild(systemEventChild, data['stockname'])
    fundsChild(systemEventChild, data['funds'])
    return systemEventChild

#trans,action,username,funds,server,types:accountTransaction-add(11)
def accountTransactionChildren_11(data):
    accountTransactionChild = root.createElement('accountTransaction')
    xml.appendChild(accountTransactionChild)

    timestampChild(accountTransactionChild, data['timestamp'])
    serverChild(accountTransactionChild, data['server'])
    transactionNumChild(accountTransactionChild, data['trans'])
    actionChild(accountTransactionChild, data['action'])
    usernameChild(accountTransactionChild, data['username'])
    fundsChild(accountTransactionChild, data['funds'])
    return accountTransactionChild

#trans,command,username,stockname,server,types:systemEvent-cancelSetBuy(12)
def systemEventChildren_12(data):
    systemEventChild = root.createElement('systemEvent')
    xml.appendChild(systemEventChild)

    timestampChild(systemEventChild, data['timestamp'])
    serverChild(systemEventChild, data['server'])
    transactionNumChild(systemEventChild, data['trans'])
    commandChild(systemEventChild, data['command'])
    usernameChild(systemEventChild, data['username'])
    stockSymbolChild(systemEventChild, data['stockname'])
    return systemEventChild

#trans,command,username,stockname,stockprice,server,types:systemEvent-setBuyTrigger(13)
def systemEventChildren_13(data):
    systemEventChild = root.createElement('systemEvent')
    xml.appendChild(systemEventChild)

    timestampChild(systemEventChild, data['timestamp'])
    serverChild(systemEventChild, data['server'])
    transactionNumChild(systemEventChild, data['trans'])
    commandChild(systemEventChild, data['command'])
    usernameChild(systemEventChild, data['username'])
    stockSymbolChild(systemEventChild, data['stockname'])
    fundsChild(systemEventChild, data['funds'])
    return systemEventChild

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
    return errorEventChild


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
    if data['types'] == "one":
        #types:userCommand-add(1)
        return userCommandChildren_1(data)
    elif data['types'] == "two":
        #types:userCommand-quote(2)
        return userCommandChildren_2(data)
    elif data['types'] == "three":
        #types:userCommand-buy(3)-sell(3)-setBuyAmount(3)-setSellAmount(3)
        return userCommandChildren_3(data)
    elif data['types'] == "four":
        #types:userCommand-commitBuy(4)-commitSell(4)-cancelBuy(4)-cancelSell(4)
        return userCommandChildren_4(data)
    elif data['types'] == "five":
        #types:userCommand-cancelSetBuy(5)-cancelSetSell(5)
        return userCommandChildren_5(data)
    elif data['types'] == "six":
        #types:userCommand-setBuyTrigger(6)-setSellTrigger(6)
        return userCommandChildren_6(data)
    elif data['types'] == "seven":
        #types:userCommand-dumplog1(7)
        return userCommandChildren_7(data)
    elif data['types'] == "eight":
        #types:userCommand-dumplog2(8)
        return userCommandChildren_8(data)
    elif data['types'] == "nine":
        #types:quoteServer(9)
        return quoteServerChildren_9(data)
    elif data['types'] == "ten":
        #types:systemEvent-database(10)-setBuyAmount(10)-setSellAmount(10)
        return systemEventChildren_10(data)
    elif data['types'] == "eleven":
        #types:accountTransaction-add(11)-remove(11)
        return accountTransactionChildren_11(data)
    elif data['types'] == "twelve":
        #types:systemEvent-cancelSetBuy(12)-cancelSetSell(12)
        return systemEventChildren_12(data)
    elif data['types'] == "thirteen":
        #types:systemEvent-setBuyTrigger(13)-setSellTrigger(13)
        return systemEventChildren_13(data)
    else:
        tag = "errorEvent"

def getCurrTimestamp():
    dateTimeObj = datetime.now()
    #print(dateTimeObj)

    timestampStr = dateTimeObj.strptime(str(dateTimeObj), '%Y-%m-%d %H:%M:%S.%f').strftime('%s.%f')
    return str(int(float(timestampStr) * 1000))

if __name__=="__main__":
    logQueue = queue.Queue(maxsize = 1000000)

    logServer = logServer(logQueue)
    logServer.start()

    root = minidom.Document()
    xml = root.createElement('log')
    root.appendChild(xml)
    main(root)
