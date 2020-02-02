from socket import *
import threading
import mysql.connector
import sys
from datetime import datetime
from decimal import Decimal

#sudo iptables -A INPUT -p tcp --dport 10000:50000 -j ACCEPT



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


class TriggerServer(threading.Thread):
    def __init__(self, mydb, dataList):
        threading.Thread.__init__(self)
        self.mydb = mydb
        self.dataList = dataList

    def run(self):
        command = ''
        if dataList[1] == 'SET_BUY_AMOUNT':
            command = 'SET_BUY_TRIGGER'
        else:
            command = 'SET_SELL_TRIGGER'


        while True:
            if checkIsTrigger(dataList[2], dataList[3], command) == 1:





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
    port = 40006

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
    check = "SELECT stockprice,amount FROM stocks WHERE username = %s and stockname = %s"
    mycursor.execute(check, (username, stockname,))
    return mycursor.fetchall()[0]


def checkUserOwnStock(username, stockname):
    check = "SELECT count(stockname) FROM stocks WHERE username = %s and stockname = %s"
    mycursor.execute(check, (username, stockname,))
    result = mycursor.fetchall()[0][0]
    if result == 1:
        return 1
    else:
        return 0


def checkAcountUser(username): # check is the user already in DB or not
    check = "SELECT count(%s) FROM acounts WHERE username = %s"
    mycursor.execute(check, (username, username,))
    result = mycursor.fetchall()[0][0]
    if result == 1:
        return 1
    else:
        return 0


def checkStockUser(username, stockname): # check is the user owned the stock
    check = "SELECT count(stockname) FROM logs WHERE username = %s AND stockname = %s AND command = 'QUOTE'"
    mycursor.execute(check, (username, stockname,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        check2 = "SELECT stockprice FROM logs WHERE username = %s AND stockname = %s AND command = 'QUOTE' ORDER BY transnumber LIMIT 1"
        mycursor.execute(check2, (username, stockname,))
        result2 = mycursor.fetchall()[0][0]
        return result2
    else:
        return 0


def checkLogTimestamp(username, command, stockname):
    check = "SELECT times FROM logs WHERE username = %s AND command = %s AND stockname = %s ORDER BY transnumber DESC LIMIT 1"
    mycursor.execute(check,(username, command, stockname))
    result = mycursor.fetchall()[0][0]
    return result


def checkbsLogTimestamp(username, command):
    check = "SELECT times FROM bslogs WHERE username = %s AND command = %s ORDER BY transnumber DESC LIMIT 1"
    mycursor.execute(check,(username, command,))
    result = mycursor.fetchall()[0][0]
    return result


def checkBuyAmount(username):
    check = "SELECT stockname,stockprice,amount FROM bslogs WHERE username = %s ORDER BY transnumber DESC LIMIT 1"
    mycursor.execute(check,(username,))
    result = mycursor.fetchall()[0]
    return result


def getBuySellData(username, command):
    check = "SELECT stockname,stockprice,amount FROM bslogs WHERE username = %s AND command = %s ORDER BY transnumber DESC LIMIT 1"
    mycursor.execute(check,(username, command,))
    result = mycursor.fetchall()[0]
    return result


def checkCommandInLog(username, command):
    check = "SELECT count(stockname) FROM logs WHERE username = %s AND command = %s"
    mycursor.execute(check, (username, command,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0


def checkCommandInbsLog(username, command):
    check = "SELECT count(stockname) FROM bslogs WHERE username = %s AND command = %s"
    mycursor.execute(check, (username, command,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0


def checkIsQuoteStock(username, stockname):
    check = "SELECT count(stockname) FROM logs WHERE username = %s AND stockname = %s"
    mycursor.execute(check, (username, stockname,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0


def checkCrypto(username, command):
    check = "SELECT cryptokey FROM logs WHERE username = %s AND command = %s ORDER BY transnumber DESC LIMIT 1"
    mycursor.execute(check, (username, command,))
    result = mycursor.fetchall()[0][0]
    return result


def checkIsTrigger(username, stockname, command):
    check = "SELECT count(command) FROM triggers WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
    result = mycursor.fetchall()[0][0]
    print(result)
    if result > 0:
        return 1
    else:
        return 0


def getTriggerStockPrice(username, stockname, command):
    check = "SELECT stockprice FROM triggers WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
    return mycursor.fetchall()[0][0]


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
    if checkUserOwnStock(user[0],user[1]) == 0:
        addFormula = "INSERT INTO stocks (username, stockname, stockprice, amount) VALUES (%s,%s,%s,%s)"
        mycursor.execute(addFormula, user)
        mydb.commit()


def addToTriggerDB(user):
    addFormula = "INSERT INTO triggers (username, stockname, command, stockprice, times) VALUES (%s,%s,%s,%s,%s)"
    mycursor.execute(addFormula, user)
    mydb.commit()


def deleteTriggerFromDB(username, stockname, command):
    deleteFormula = "DELETE FROM triggers WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(deleteFormula, (username,stockname,command,))
    mydb.commit()


def removeFromDB(user): # remove the user funds from DB
    currFunds = checkAcountFunds(user[0])
    if currFunds >= user[1]:
        newFunds = currFunds - user[1]
        updateFunds(user[0], newFunds)
    else:
        print("Acount funds is not enough!")


def dbLogs(logInfo):
    #print('here')
    logFormula = "INSERT INTO logs (username, transnumber, command, stockname, stockprice, amount, funds, times, cryptokey) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    mycursor.execute(logFormula, logInfo)
    mydb.commit()


def dbBuySellLogs(logInfo):
    logFormula = "INSERT INTO bslogs (username, transnumber, command, stockname, stockprice, amount, times, cryptokey) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    mycursor.execute(logFormula, logInfo)
    mydb.commit()


def deleteBuySellLogs(username):
    checkBSLogs = "SELECT * FROM bslogs WHERE username = %s ORDER BY transnumber DESC LIMIT 1"
    mycursor.execute(checkBSLogs, (username,))
    result = mycursor.fetchall()[0]

    #calculate the currFunds
    accountFunds = checkAcountFunds(username)
    currFunds = accountFunds - result[5]

    #add to dbLogs
    dbLogs((result[0], result[1], result[2], result[3], result[4], result[5], (currFunds+result[5]), getCurrTimestamp(), result[7]))

    #remove from bslogs
    deleteFormula = "DELETE FROM bslogs WHERE username = %s ORDER BY transnumber DESC LIMIT 1"
    mycursor.execute(deleteFormula, (username,))
    mydb.commit()



def commandControl(data):
    global dataList
    dataList = data.split(',')

    if dataList[1] == "ADD":
        print("Data should be send direct to Aduit Server: " + data)
        addToDB((dataList[2], dataList[3]))
        dbLogs((dataList[2], dataList[0], dataList[1], None, None, None, dataList[3], getCurrTimestamp(), None))

        #trans,userid,funds,types
        logQueue.append(data + ',1')
        return data

    elif dataList[1] == "QUOTE":
        newdata = dataList[3] + ',' + dataList[2] + '\r'
        dataFromQuote = sendToQuote(newdata).rstrip().split(',')
        dbLogs((dataList[2], dataList[0], dataList[1], dataList[3], dataFromQuote[0], None, None, getCurrTimestamp(), dataFromQuote[4]))
        # userid,stockname,stockprice,timestamp,cryptokey
        result = str(dataList[2])+','+str(dataList[3])+','+dataFromQuote[0]+','+dataFromQuote[3]
        return result

    elif dataList[1] == 'BUY':
        currFunds = checkAcountFunds(dataList[2])
        if currFunds >= Decimal(dataList[4]):
            logQueue.append(data + ',1')
            newdata = dataList[3] + ',' + dataList[2] + '\r'
            stockprice = checkStockUser(dataList[2], dataList[3])

            commandTimestamp = getCurrTimestamp()
            logTimestamp = checkLogTimestamp(dataList[2],'QUOTE',dataList[3])
            crypto = checkCrypto(dataList[2], 'QUOTE')

            if stockprice > 0 and (in60s(logTimestamp, commandTimestamp) == 1):

                dbBuySellLogs((dataList[2], dataList[0], dataList[1], dataList[3], stockprice, dataList[4], getCurrTimestamp(), crypto))

                #trans,command,stockname,amount,stockprice,qouteTimestamp,cryptokey,types
                logQueue.append(data+','+str(stockprice)+','+str(logTimestamp)+','+crypto+',4')

                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1])+','+str(dataList[2])+','+str(dataList[4])+','+str(stockprice)+','+str(logTimestamp)+','+crypto
                return result

            else:
                dataFromQuote = sendToQuote(newdata).split(',')

                dbBuySellLogs((dataList[2], dataList[0], dataList[1], dataList[3], dataFromQuote[0], dataList[4], getCurrTimestamp(), dataFromQuote[4]))

                #trans,command,stockname,amount,stockprice,qouteTimestamp,cryptokey,types
                logQueue.append(data+','+dataFromQuote[0]+','+dataFromQuote[3]+','+dataFromQuote[4]+',4')

                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1]+','+dataList[2]+','+dataList[4]+','+dataFromQuote[0]+','+dataFromQuote[3]+','+dataFromQuote[4])
                return result
        else:
            return "User Funds Not Enough!"

    elif dataList[1] == "COMMIT_BUY":

        check_BUY_in_bsLog = checkCommandInbsLog(dataList[2], 'BUY')

        if check_BUY_in_bsLog == 0:
            return "There is no buy command input!"

        stockname = getBuySellData(dataList[2], 'BUY')[0]

        if check_BUY_in_bsLog == 1:

            commitTimestamp = getCurrTimestamp()
            logTimestamp = checkbsLogTimestamp(dataList[2],'BUY')

            if checkIsQuoteStock(dataList[2], stockname) == 1 and in60s(logTimestamp, commitTimestamp) == 1:

                currFunds =  Decimal(checkAcountFunds(dataList[2]))
                snspba = checkBuyAmount(dataList[2])

                if currFunds >= snspba[2]:

                    userFundsLeft = (snspba[2] % snspba[1]) + (currFunds - snspba[2])
                    stockAmount = int(snspba[2] / snspba[1])


                    addToStocksDB((dataList[2],snspba[0],snspba[1],stockAmount))
                    deleteBuySellLogs(dataList[2])
                    updateFunds(dataList[2], userFundsLeft)

                    #username,stockname,stockprice,amount,funds
                    result = dataList[2]+','+snspba[0]+','+str(snspba[1])+','+str(snspba[2])+','+str(userFundsLeft)
                    return result

                else:
                    return "User Funds Not Enough!"

            else:
                return "User over the commit time CANCEL_BUY!"
        else:
            return "ERROR BUY COMMAND NOT FIND!"

    elif dataList[1] == "CANCEL_BUY":
        deleteBuySellLogs(dataList[2])
        return "BUY Command has been caneled!"

    elif dataList[1] == "SELL":

        if checkUserOwnStock(dataList[2], dataList[3]) == 0:
            return "User does not own the stocks!"

        amount = checkStockAmount(dataList[2], dataList[3])
        ownMoney = Decimal(amount[0]) * Decimal(amount[1])


        if amount[1] > 0 and ownMoney >= Decimal(dataList[4]):

            commandTimestamp = getCurrTimestamp()
            logTimestamp = checkLogTimestamp(dataList[2],'QUOTE',dataList[3])

            if checkCommandInLog(dataList[2],"QUOTE") == 1 and in60s(logTimestamp, commandTimestamp) == 1:
                stockprice = checkStockUser(dataList[2], dataList[3])
                crypto = checkCrypto(dataList[2], 'QUOTE')

                dbBuySellLogs((dataList[2], dataList[0], dataList[1], dataList[3], stockprice, dataList[4], getCurrTimestamp(), crypto))

                #trans,command,stockname,amount,stockprice,qouteTimestamp,cryptokey,types
                logQueue.append(data+','+str(stockprice)+','+str(logTimestamp)+','+crypto+',4')

                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1])+','+str(dataList[2])+','+str(dataList[4])+','+str(stockprice)+','+str(logTimestamp)+','+crypto
                return result

            else:
                dataFromQuote = sendToQuote(newdata).split(',')

                dbBuySellLogs((dataList[2], dataList[0], dataList[1], dataList[3], dataFromQuote[0], dataList[4], getCurrTimestamp(), dataFromQuote[4]))

                #trans,command,stockname,amount,stockprice,qouteTimestamp,cryptokey,types
                logQueue.append(data+','+dataFromQuote[0]+','+dataFromQuote[3]+','+dataFromQuote[4]+',4')

                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1]+','+dataList[2]+','+dataList[4]+','+dataFromQuote[0]+','+dataFromQuote[3]+','+dataFromQuote[4])
                return result

        else:
            return "User dose not own the stocks!"

    elif dataList[1] == "COMMIT_SELL":
        #check to see if user has asked for quote within last 60 seconds

        check_SELL_in_bsLog = checkCommandInbsLog(dataList[2], 'SELL')

        if check_SELL_in_bsLog == 0:
            return "There is no sell command input!"

        stockname = getBuySellData(dataList[2], 'SELL')[0]
        amount = checkStockAmount(dataList[2], stockname)


        if checkCommandInbsLog(dataList[2], 'SELL') == 1 and amount[1] > 0:

            commitTime = getCurrTimestamp()
            logTimestamp = checkbsLogTimestamp(dataList[2],'SELL')

            if checkIsQuoteStock(dataList[2], stockname) == 1 and in60s(logTimestamp, commitTime) == 1:

                currFunds =  Decimal(checkAcountFunds(dataList[2]))
                snspfd = getBuySellData(dataList[2], 'SELL')


                total = amount[1] * snspfd[1]
                if total >= snspfd[2]:

                    amountCanSell = int(snspfd[2]/snspfd[1])
                    moneyCanGet = amountCanSell * snspfd[1]
                    newFunds = currFunds + moneyCanGet
                    shareLeft = amount[1] - amountCanSell

                    updateStockAmount(dataList[2], snspfd[0], snspfd[1], shareLeft)
                    deleteBuySellLogs(dataList[2])
                    updateFunds(dataList[2], newFunds)

                    result = dataList[2]+','+snspfd[0]+','+str(snspfd[1])+','+str(snspfd[2])+','+str(newFunds)
                    return result

                else:
                    return "ERROR USER OWN AMOUNT NOT ENOUGH!"

            else:

                return "ERROR OVER COMMIT TIME!"

        else:
            return "ERROR SELL COMMAND NOT FIND!"




    elif dataList[1] == "CANCEL_SELL":
        deleteBuySellLogs(dataList[2])
        return " SELL Command has been caneled"

    elif dataList[1] == "SET_BUY_AMOUNT":
        ts = TriggerServer(mydb, dataList)
        print('2222')
        ts.start()
        print('3333')
        return "Trigger is hit running..."

    elif dataList[1] == "CANCEL_SET_BUY":
        deleteTriggerFromDB(dataList[2], dataList[3], 'SET_BUY_TRIGGER')
        return "CANCEL SET BUY!"

    elif dataList[1] == "SET_BUY_TRIGGER":
        addToTriggerDB((dataList[2], dataList[3], dataList[1], dataList[4], getCurrTimestamp()))
        return "SET BUY TRIGGER!"

    elif dataList[1] == "SET_SELL_AMOUNT":
        pass

    elif dataList[1] == "SET_SELL_TRIGGER":
        addToTriggerDB((dataList[2], dataList[3], dataList[1], dataList[4], getCurrTimestamp()))
        return "SET SELL TRIGGER!"

    elif dataList[1] == "CANCEL_SET_SELL":
        deleteTriggerFromDB(dataList[2], dataList[3], 'SET_SELL_TRIGGER')
        return "CANCEL SET SELL!"

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
