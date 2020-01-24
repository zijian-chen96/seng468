from xml.dom import minidom

def main():

    data = "12121212,abcabc"

    userCommandChildren(data)

    accountTransactionChildren(data)

    systemEventChildren(data)

    quoteServerChildren(data)

    errorEventChildren(data)


    xml_str = root.toprettyxml(indent='\t')

    save_path_file = "testxmlfile.xml"

    with open(save_path_file, "w") as f:
        f.write(xml_str)


def userCommandChildren(data):
    #dataList = data.split(',')

    userCommandChild = root.createElement('userCommand')
    xml.appendChild(userCommandChild)

    timestampChild(userCommandChild, data)
    serverChild(userCommandChild, data)
    transactionNumChild(userCommandChild, data)
    commandChild(userCommandChild, data)
    usernameChild(userCommandChild, data)
    fundsChild(userCommandChild, data)

def accountTransactionChildren(data):

    accountTransactionChild = root.createElement('accountTransaction')
    xml.appendChild(accountTransactionChild)

    timestampChild(accountTransactionChild, data)
    serverChild(accountTransactionChild, data)
    transactionNumChild(accountTransactionChild, data)
    actionChild(accountTransactionChild, data)
    usernameChild(accountTransactionChild, data)
    fundsChild(accountTransactionChild, data)

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

def quoteServerChildren(data):

    qouteServerChild = root.createElement('qouteServer')
    xml.appendChild(qouteServerChild)

    timestampChild(qouteServerChild, data)
    serverChild(qouteServerChild, data)
    transactionNumChild(qouteServerChild, data)
    qouteServerTimeChild(qouteServerChild, data)
    usernameChild(qouteServerChild, data)
    stockSymbolChild(qouteServerChild, data)
    priceChild(qouteServerChild, data)
    cryptokeyChild(qouteServerChild, data)

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



if __name__ == '__main__':
    root = minidom.Document()
    xml = root.createElement('log')
    root.appendChild(xml)
    main()
