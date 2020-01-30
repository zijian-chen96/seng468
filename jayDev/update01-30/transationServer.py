from socket import *
import threading
import mysql.connector
import sys
from datetime import datetime
from decimal import Decimal


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


def getCurrTimestamp():
    dateTimeObj = datetime.now()
    #print(dateTimeObj)

    timestampStr = dateTimeObj.strptime(str(dateTimeObj), '%Y-%m-%d %H:%M:%S.%f').strftime('%s.%f')
    return str(int(float(timestampStr) * 1000))


def in60s(logTime, commitTime):
    timeGaps = float(commitTime) - float(logTime)
    if timeGaps <= 60000:
        return 1
    else:
        return 0

def sendToQuote(data):
    fromUser = data
    quoteServerSocket = socket(AF_INET,SOCK_STREAM)

    #quoteServerSocket.connect(('quoteserve.seng.uvic.ca',4447))
    quoteServerSocket.connect(('192.168.0.10',44432))

    quoteServerSocket.send(fromUser)

    dataFromQuote = quoteServerSocket.recv(1024)

    quoteServerSocket.close()

    return dataFromQuote


def recvFromHttp():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    host = ''
    port = 44437

    serverSocket.bind((host,port))

    serverSocket.listen(10)

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
    return mycursor.fetchall()[0][0]


def checkStockAmount(username, stockname): # check the stock amount the user owned
    check = "SELECT amount FROM stocks WHERE username = %s and stockname = %s"
    mycursor.execute(check, (username, stockname,))
    return mycursor.fetchall()[0][0]


def checkAcountUser(username): # check is the user already in DB or not
    check = "SELECT count(%s) FROM acounts WHERE username = %s"
    mycursor.execute(check, (username, username,))
    result = mycursor.fetchall()[0][0]
    if result == 1:
        return 1
    else:
        return 0


def checkLogTimestamp(username):
    check = "SELECT times FROM logs WHERE username = %s ORDER BY transnumber DESC LIMIT 1"
    mycursor.execute(check,(username,))
    result = mycursor.fetchall()[0][0]
    return result


def checkBuyAmount(username):
    check = "SELECT stockname,stockprice,amount FROM logs WHERE username = %s ORDER BY transnumber DESC LIMIT 1"
    mycursor.execute(check,(username,))
    result = mycursor.fetchall()[0]
    return result


def updateFunds(username, funds): # update the user acount funds
    updateFormula = "UPDATE acounts SET funds = %s WHERE username = %s"
    mycursor.execute(updateFormula, (funds, username,))
    mydb.commit()


def updateStockAmount(username, stockname, stockprice, amount): # update the stock amount the user owned
    updateFormula = "UPDATE stocks SET amount = %s WHERE username = %s AND stockname = %s"
    mycursor.execute(updateFormula, (amount, username, stockname,))
    mydb.commit()


def addToDB(user): # # add the user into DB if is not in the DB else update the funds
    if checkAcountUser(user[0]) == 0:
        addFormula = "INSERT INTO acounts (username, funds) VALUES (%s, %s)"
        mycursor.execute(addFormula, user)
        mydb.commit()
    else:
        newFunds = checkAcountFunds(user[0]) + user[1]
        updateFunds(user[0], user[1])


def addToStocksDB(user):
    addFormula = "INSERT INTO stocks (username, stockname, stockprice, amount) VALUES (%s,%s,%s,%s)"
    mycursor.execute(addFormula, user)
    mydb.commit()


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


def dbLogs(logInfo):
    #print('here')
    logFormula = "INSERT INTO logs (username, transnumber, command, stockname, stockprice, amount, funds, times) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    mycursor.execute(logFormula, logInfo)
    mydb.commit()


def commandControl(data):
    dataList = data.split(',')

    if dataList[1] == "ADD":
        print("Data should be send direct to Aduit Server: " + data)
        addToDB((dataList[2], dataList[3]))
        dbLogs((dataList[2], dataList[0], dataList[1], None, None, None, dataList[3], getCurrTimestamp()))

        #trans,userid,funds,types
        logQueue.append(data + ',1')
        return data

    elif dataList[1] == "QUOTE":
        newdata = dataList[3] + ',' + dataList[2] + '\r'
        dataFromQuote = sendToQuote(newdata).split(',')
        dbLogs((dataList[2], dataList[0], dataList[1], dataList[3], dataFromQuote[0], None, None, getCurrTimestamp()))
        # userid,stockname,stockprice,timestamp,cryptokey
        result = str(dataList[3]+','+dataList[2]+','+dataFromQuote[0]+','+dataFromQuote[3],+','+dataFromQuote[4])
        return result

    elif dataList[1] == 'BUY':
        currFunds = checkAcountFunds(dataList[2])
        if currFunds >= Decimal(dataList[4]):
            logQueue.append(data + ',1')
            newdata = dataList[3] + ',' + dataList[2] + '\r'
            dataFromQuote = sendToQuote(newdata).split(',')

            dbLogs((dataList[2], dataList[0], dataList[1], dataList[3], dataFromQuote[0], dataList[4], currFunds, getCurrTimestamp()))

            #trans,command,stockname,amount,stockprice,qouteTimestamp,cryptokey,types
            logQueue.append(data+','+dataFromQuote[0]+','+dataFromQuote[3]+','+dataFromQuote[4]+',4')

            #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
            result = str(dataList[1]+','+dataList[2]+','+dataList[4]+','+dataFromQuote[0]+','+dataFromQuote[3]+','+dataFromQuote[4])
            return result
        else:
            return "User Funds Not Enough!"

    elif dataList[1] == "COMMIT_BUY":
        commitTimestamp = getCurrTimestamp()
        logTimestamp = checkLogTimestamp(dataList[2])
        if in60s(logTimestamp, commitTimestamp) == 1:
            currFunds =  Decimal(checkAcountFunds(dataList[2]))
            snspba = checkBuyAmount(dataList[2])
            if currFunds >= snspba[1]:
                userFundsLeft = currFunds - snspba[1]
                updateFunds(dataList[2], userFundsLeft)
                addToStocksDB((dataList[2],snspba[0],snspba[1],snspba[2]))

                #username,stockname,stockprice,amount,funds
                result = dataList[2]+','+snspba[0]+','+str(snspba[1])+','+str(snspba[2])+','+str(userFundsLeft)
                return result

            else:
                return "User Funds Not Enough!"

        else:
            return "User over the commit time CANCEL_BUY!"


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
    # auditIP = "192.168.1.188"
    # auditPort = 44432
    #
    # auditSocket = socket(AF_INET, SOCK_STREAM)
    # auditSocket.connect((auditIP,auditPort))
    #
    # AuditServer = AuditServer(logQueue, auditSocket)
    # AuditServer.start()

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootpassword",
        database="dbone"
    )
    mycursor = mydb.cursor()

    recvFromHttp()
