from socket import *
import threading
import mysql.connector
import sys



class AuditServer(threading.Thread):
    def __init__(self, logQueue, auditSocket):
        threading.Thread.__init__(self)
        self.logQueue = logQueue
        self.auditSocket = auditSocket

    def run(self):
        while True:
            if len(logQueue) != 0:
                data = logQueue.pop(0)
                print("This data must send to aduit server: " + data)
                auditSocket.send(data)


def sendToQuote(data):
    fromUser = data
    quoteServerSocket = socket(AF_INET,SOCK_STREAM)

    quoteServerSocket.connect(('quoteserve.seng.uvic.ca',4447))

    quoteServerSocket.send(fromUser)

    dataFromQuote = quoteServerSocket.recv(1024)

    quoteServerSocket.close()

    return dataFromQuote


def recvFromHttp():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    host = ''
    port = 44430

    serverSocket.bind((host,port))

    serverSocket.listen(5)

    print('Waitting for Connection...')

    connectSocket, addr = serverSocket.accept()

    try:
        while True:
            data = ''
            data = connectSocket.recv(1024)

            if data:
                print("Data recv from HTTP Server: " + data)

                dataFromQuote = commandControl(data)

                print("Data recv from Quote Server: " + dataFromQuote)

                connectSocket.send(dataFromQuote) #Send back to HTTP Server

            else:
                auditSocket.close()
                break


    except:
            connectSocket.send('Something Wrong!')
            connectSocket.close()

    serverSocket.close()


def checkAcountFunds(username): # check the acount funds
    check = "SELECT funds FROM acounts WHERE username = %s"
    mycursor.execute(check, (username,))
    return result mycursor.fetchall()[0][0]


def checkStockAmount(username, stockname): # check the stock amount the user owned
    check = "SELECT amount FROM stocks WHERE username = %s and stockname = %s"
    mycursor.execute(check, (username, stockname,))
    return mycursor.fetchall()[0][0]


def checkAcountUser(username): # check is the user already in DB or not
    check = "SELECT count(%s) FROM acounts WHERE username = %s"
    mycursor.execute(check, (username, username,))
    result = mycursor.fetchall()[0][0]
    if result == 1:
        return True
    else:
        return False


def updateFunds(username, funds): # update the user acount funds
    updateFormula = "UPDATE acounts SET funds = %s WHERE username = %s"
    mycursor.execute(updateFormula, (funds, username,))
    mydb.commit()


def updateStockAmount(username, stockname, amount): # update the stock amount the user owned
    updateFormula = "UPDATE stocks SET amount = %s WHERE username = %s AND stockname = %s"
    mycursor.execute(updateFormula, (amount, username, stockname,))
    mydb.commit()


def addToDB(user): # # add the user into DB if is not in the DB else update the funds
    if checkAcountUser(user[0]) == False:
        addFormula = "INSERT INTO acounts (username, funds) VALUES (%s, %s)"
        mycursor.execute(addFormula, user)
        mydb.commit()
    else:
        newFunds = checkAcountFunds(user[0]) + user[1]
        updateFunds(user[0], user[1])


def removeFromDB(user): # remove the user funds from DB
    currFunds = checkAcountFunds(user[0])
    if currFunds >= user[1]:
        newFunds = currFunds - user[1]
        updateFunds(user[0], newFunds)
    else:
        print("Acount funds is not enough!")


def sellStock(username, stockname, amount): # sell the user stock amount if is enough
    currAmount = checkStockAmount(username, stockname)
    if currAmount >= amount:
        newAmount = currAmount - amount
        updateStockAmount(username, stockname, newAmount)
    else:
        print("Stock Amount is not enough!")


def commandControl(data):
    dataList = data.split(',')

    if dataList[1] == "ADD":
        print("Data should be send direct to Aduit Server: " + data)
        logQueue.append(data + ',1')
        return data

    elif dataList[1] == "QUOTE":
        newdata = dataList[3] + ',' + dataList[2] + '\r'
        return newdata

    elif dataList[1] == 'BUY':
        print("heloo" + data)
        logQueue.append(data + ',1')
        newdata = dataList[3] + ',' + dataList[2] + '\r'
        dataFromQuote = sendToQuote(newdata)
        logQueue.append(data + ',' + dataFromQuote + ',4')
        print("aello" + data + ',' + dataFromQuote + ',4')
        return dataFromQuote

    elif dataList[1] == "COMMIT_BUY":
        pass

    elif dataList[1] == "CANCEL_BUY":
        pass

    elif dataList[1] == "SELL":
        logQueue.append(data + ',1')
        newdata = dataList[3] + ',' + dataList[2] + '\r'
        dataFromQuote = sendToQuote(newdata)
        logQueue.append(data + ',' + dataFromQuote + ',4')
        print("bello" + data + ',' + dataFromQuote + ',4')
        return dataFromQuote

    elif dataList[1] == "COMMIT_SELL":
        pass

    elif dataList[1] == "CANCEL_SELL":
        pass

    elif dataList[1] == "SET_BUY_AMOUNT":
        pass

    elif dataList[1] == "CANCEL_SET_BUY":
        pass

    elif dataList[1] == "SET_BUY_TRIGGER":
        pass

    elif dataList[1] == "SET_SELL_AMOUNT":
        pass

    elif dataList[1] == "SET_SELL_TRIGGER":
        pass

    elif dataList[1] == "CANCEL_SET_SELL":
        pass

    elif dataList[1] == "DUMPLOG":
        pass

    elif dataList[1] == "DUMPLOG":
        pass

    elif dataList[1] == "DISPLAY_SUMMARY":
        pass

if __name__ == '__main__':
    logQueue = []
    auditIP = "192.168.1.188"
    auditPort = 44432

    auditSocket = socket(AF_INET, SOCK_STREAM)
    auditSocket.connect((auditIP,auditPort))

    AuditServer = AuditServer(logQueue, auditSocket)
    AuditServer.start()

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootpassword",
        database="testdb"
    )
    mycursor = mydb.cursor()

    recvFromHttp()
