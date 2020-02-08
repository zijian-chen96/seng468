from socket import *
import threading
import mysql.connector
import sys
from datetime import datetime
from decimal import Decimal
import time
import Queue as queue

#sudo iptables -A INPUT -p tcp --dport 10000:60000 -j ACCEPT
#sudo /etc/init.d/mysql restart


class AuditServer(threading.Thread):
    def __init__(self, time, logQueue, auditSocket):
        threading.Thread.__init__(self)
        self.logQueue = logQueue
        self.auditSocket = auditSocket
        self.time = time

    def run(self):
        while True:
            if logQueue.empty() != True:
                #time.sleep(0.2)
                data = logQueue.get()
                # if data == "GMAEOVER":
                #     break
                #print("This data must send to aduit server: " + data)
                auditSocket.send(data)


class TRIGGERS(threading.Thread):

    def __init__(self, dataList):
        super(TRIGGERS, self).__init__()
        self._stop = threading.Event()
        self.dataList2 = []
        self.dataList2.extend(dataList)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def run(self):

        command = ''
        if self.dataList2[1] == 'SET_BUY_AMOUNT':
            command = 'SET_BUY_TRIGGER'
        else:
            command = 'SET_SELL_TRIGGER'

        #with cond:
        while command == 'SET_BUY_TRIGGER':
            if checkIsTrigger(self.dataList2[2], self.dataList2[3], command) == 1:
                buyStockPrice = getTriggerStockPrice(self.dataList2[2], self.dataList2[3], command)

                holdMoney = Decimal(self.dataList2[4])
                if holdMoneyFromAcount(self.dataList2[2], self.dataList2[4]) == 1:
                    currFunds =  Decimal(checkAcountFunds(self.dataList2[2]))

                    #time.sleep(0.01)
                    #cond.notifyAll()

                    # username, transnumber, command, stockname, stockprice, amount, funds, times, cryptokey
                    dbLogs((self.dataList2[2], self.dataList2[0], 'BUY-TRIGGER-HOLDER', self.dataList2[3], None, holdMoney, currFunds, getCurrTimestamp(), None))

                    while True:
                        if self.stopped():
                            return
                        #cond.notifyAll()
                        dataFromQuote = sendToQuote(self.dataList2[3] + ',' + self.dataList2[2] + '\r').split(',')

                        if Decimal(dataFromQuote[0]) <= buyStockPrice and Decimal(dataFromQuote[0]) <= holdMoney:

                            #currFunds =  Decimal(checkAcountFunds(dataList[2]))

                            userFundsLeft = (holdMoney % Decimal(dataFromQuote[0])) + currFunds
                            stockAmount = int(holdMoney / Decimal(dataFromQuote[0]))

                            addToStocksDB((self.dataList2[2],self.dataList2[3],stockAmount))
                            # username, transnumber, command, stockname, stockprice, amount, funds, times, cryptokey
                            dbLogs((self.dataList2[2], self.dataList2[0], 'BUY', self.dataList2[3], dataFromQuote[0], self.dataList2[4], currFunds, getCurrTimestamp(), dataFromQuote[4]))
                            updateFunds(self.dataList2[2],userFundsLeft)
                            #deleteTriggerFromDB(self.dataList2[2],self.dataList2[3],command)

                            break

                        else:
                            print("current stock price: " + dataFromQuote[0])
                            time.sleep(1)
                    print('finish exit out of thread!')

                    break

                else:
                    #time.sleep(0.01)
                    #cond.notifyAll()
                    return "User funds is not enough!"

            else:
                #time.sleep(0.01)
                #cond.notifyAll()
                return 'TRIGGER NOT FOUND!'

        while command == 'SET_SELL_TRIGGER':
            if checkIsTrigger(self.dataList2[2], self.dataList2[3], command) == 1:
                sellStockPrice = getTriggerStockPrice(self.dataList2[2],self.dataList2[3],command)
                numStocks = checkStockAmount(self.dataList2[2], self.dataList2[3])
                holdStockAmount = int(Decimal(self.dataList2[4])/sellStockPrice)
                if numStocks != 0 and holdStockAmountFromAcount(self.dataList2[2], self.dataList2[3], holdStockAmount) == 1:

                    currFunds = Decimal(checkAcountFunds(self.dataList2[2]))
                    #time.sleep(0.01)
                    #cond.notifyAll()

                    dbLogs((self.dataList2[2], self.dataList2[0], 'SELL-TRIGGER-HOLDER', self.dataList2[3], None, holdStockAmount, currFunds, getCurrTimestamp(), None))

                    while True:
                        if self.stopped():
                            return
                        #cond.notifyAll()
                        dataFromQuote = sendToQuote(self.dataList2[3] + ',' + self.dataList2[2] + '\r').split(',')
                        numStocksToSell = int(Decimal(self.dataList2[4]) / Decimal(dataFromQuote[0]))

                        if Decimal(dataFromQuote[0]) >= sellStockPrice and holdStockAmount >= numStocksToSell:


                            moneyCanGet = numStocksToSell * Decimal(dataFromQuote[0])
                            newFunds = currFunds + moneyCanGet

                            updateStockAmount(self.dataList2[2], self.dataList2[3], (numStocks-numStocksToSell))
                            dbLogs((self.dataList2[2], self.dataList2[0], 'SELL', self.dataList2[3], dataFromQuote[0], self.dataList2[4], currFunds, getCurrTimestamp(), dataFromQuote[4]))
                            updateFunds(self.dataList2[2], newFunds)
                            #deleteTriggerFromDB(self.dataList2[2],self.dataList2[3],command)

                            break

                        else:
                            print("current stock price: " + dataFromQuote[0])
                            time.sleep(1)
                    print('finish exit out of thread!')

                    break

                else:
                    #time.sleep(0.01)
                    #cond.notifyAll()
                    return "User stock amount is not enough!"

            else:
                #time.sleep(0.01)
                #cond.notifyAll()
                return 'TRIGGER NOT FOUND!'


# def triggers(self.dataList2, cond):
    #
    # dataList = []
    # dataList.extend(self.dataList2)

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
    port = 50017

    serverSocket.bind((host,port))

    serverSocket.listen(10)

    print('Waitting for Connection...')

    connectSocket, addr = serverSocket.accept()

    try:
        while True:
            data = ''
            data = connectSocket.recv(10240)

            if data:
                print("Data recv from HTTP Server: " + data)

                dataFromQuote = commandControl(data)

                print("Data recv from Quote Server: " + dataFromQuote)

                connectSocket.send(dataFromQuote) #Send back to HTTP Server

            else:
                if len(logQueue) == 0:
                    auditSocket.close()
                    break


    except:
            connectSocket.send('------SOMETHING WRONG!------')
            connectSocket.close()


    serverSocket.close()


def checkAcountFunds(username): # check the acount funds
    check = "SELECT funds FROM acounts WHERE username = %s"
    mycursor.execute(check, (username,))
    return mycursor.fetchall()[0][0]


def checkStockAmount(username, stockname): # check the stock amount the user owned
    if checkUserOwnStock(username, stockname) == 1:
        check = "SELECT amount FROM stocks WHERE username = %s and stockname = %s"
        mycursor.execute(check, (username, stockname,))
        return mycursor.fetchall()[0][0]
    else:
        return 0

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
    if checkCommandInLog(username,stockname,"QUOTE") == 1:
        check = "SELECT times FROM logs WHERE username = %s AND command = %s AND stockname = %s ORDER BY transnumber DESC LIMIT 1"
        mycursor.execute(check,(username, command, stockname))
        result = mycursor.fetchall()[0][0]
        return result
    else:
        return 0


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


def checkCommandInLog(username, stockname, command):
    check = "SELECT count(username) FROM logs WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0


def checkCommandInbsLog(username, command):
    check = "SELECT count(username) FROM bslogs WHERE username = %s AND command = %s"
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


def checkCrypto(username, stockname, command):
    if checkCommandInLog(username, stockname, command) == 1:
        check = "SELECT cryptokey FROM logs WHERE username = %s AND stockname = %s AND command = %s ORDER BY transnumber DESC LIMIT 1"
        mycursor.execute(check, (username, stockname, command,))
        result = mycursor.fetchall()[0][0]
        return result
    else:
        return 0


def checkIsTrigger(username, stockname, command):
    check = "SELECT count(command) FROM triggers WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0

def updateTrigger(username, stockname, command, stockprice):
    updateFormula = "UPDATE triggers SET stockprice = %s WHERE username = %s and stockname = %s and command = %s"
    mycursor.execute(updateFormula, (stockprice, username, stockname, command,))
    mydb.commit()

def getQuoteFromLogs(username, stockname, command):
    if checkCommandInLog(username, stockname, "QUOTE") == 1:
        #quote,sym,userid,timestamp,cryptokey
        check = "SELECT stockprice,stockname,username,times,cryptokey FROM logs WHERE username = %s AND stockname = %s AND command = %s"
        mycursor.execute(check, (username, stockname, command,))
        result = mycursor.fetchall()[0]
        return result
    else:
        return 0

def getTriggerStockPrice(username, stockname, command):
    check = "SELECT stockprice FROM triggers WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
    return mycursor.fetchall()[0][0]


def getLogUser(username): # get one user's transation log
    getlog = "SELECT * FROM logs WHERE username = %s"
    mycursor.execute(getlog, (username,))
    result = mycursor.fetchall()
    s = ''
    for i in result:
        for j in i:
            s += str(j)+' '
        s += '\n'
    return s


def getLog(): # get all transation log
    getlog = "SELECT * FROM logs"
    mycursor.execute(getlog)
    result = mycursor.fetchall()
    s = ''
    for i in result:
        for j in i:
            s += str(j)+' '
        s += '\n'
    return s


def getAccountSummary(username):
    getAccount = "SELECT * FROM acounts"
    mycursor.execute(getAccount)
    result = mycursor.fetchall()
    s = ''
    for i in result:
        for j in i:
            s += str(j)+' '
        s += '\n'
    return s


def getTriggerSummary(username):
    getTrigger = "SELECT * FROM triggers WHERE username = %s"
    mycursor.execute(getTrigger,(username,))
    result = mycursor.fetchall()
    s = ''
    for i in result:
        for j in i:
            s += str(j)+' '
        s += '\n'
    return s


def getSummary(username):
    transSummary = getLogUser(username)
    accountSummary = getAccountSummary(username)
    triggerSummary = getTriggerSummary(username)
    return 'Acount: '+accountSummary+'\nTrigger_Set: '+triggerSummary+'\nTransations: '+transSummary


def holdMoneyFromAcount(username, amount):
    getFunds =  checkAcountFunds(username)
    newFunds = getFunds - Decimal(amount)
    if getFunds >= Decimal(amount):
        holdMoneyFormula = "UPDATE acounts SET funds = %s WHERE username = %s"
        mycursor.execute(holdMoneyFormula, (newFunds,username))
        mydb.commit()
        return 1
    else:
        return 0


def holdStockAmountFromAcount(username, stockname, amount):
    getAmount =  checkStockAmount(username, stockname)
    newAmount = getAmount - Decimal(amount)
    if getAmount >= Decimal(amount):
        holdStockAmountFormula = "UPDATE stocks SET amount = %s WHERE username = %s"
        mycursor.execute(holdStockAmountFormula, (newAmount,username))
        mydb.commit()
        return 1
    else:
        return 0


def updateFunds(username, funds): # update the user acount funds
    updateFormula = "UPDATE acounts SET funds = %s WHERE username = %s"
    mycursor.execute(updateFormula, (funds, username,))
    mydb.commit()


def updateStockAmount(username, stockname, amount): # update the stock amount the user owned
    updateFormula = "UPDATE stocks SET amount = %s WHERE username = %s AND stockname = %s"
    mycursor.execute(updateFormula, (amount, username, stockname,))
    mydb.commit()


def addToDB(user): # # add the user into DB if is not in the DB else update the funds
    if checkAcountUser(user[0]) == 0:
        addFormula = "INSERT INTO acounts (username, funds) VALUES (%s, %s)"
        mycursor.execute(addFormula, user)
        mydb.commit()
    else:
        newFunds = checkAcountFunds(user[0]) + Decimal(user[1])
        updateFunds(user[0], newFunds)


def addToStocksDB(user):
    if checkUserOwnStock(user[0],user[1]) == 0:
        addFormula = "INSERT INTO stocks (username, stockname, amount) VALUES (%s,%s,%s)"
        mycursor.execute(addFormula, user)
        mydb.commit()
    else:
        oldShare = checkStockAmount(user[0], user[1])
        newShare = user[2] + oldShare
        updateStockAmount(user[0], user[1], newShare)


def addToTriggerDB(user):
    addFormula = "INSERT INTO triggers (username, stockname, command, stockprice, times) VALUES (%s,%s,%s,%s,%s)"
    mycursor.execute(addFormula, user)
    mydb.commit()


def deleteTriggerFromDB(username, stockname, command):
    if checkIsTrigger(username, stockname, command) == 1:
        deleteFormula = "DELETE FROM triggers WHERE username = %s AND stockname = %s AND command = %s"
        mycursor.execute(deleteFormula, (username,stockname,command,))
        mydb.commit()
        return 1
    else:
        return 0


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


def deleteBuySellLogs(username, command):
    if checkCommandInbsLog(username, command) == 1:
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
        return 1
    else:
        return 0


def commandControl(data):
    global dataList
    dataList = data.split(',')

    if dataList[1] == "ADD":
        #print("Data should be send direct to Aduit Server: " + data)
        addToDB((dataList[2], dataList[3]))
        dbLogs((dataList[2], dataList[0], dataList[1], None, None, None, dataList[3], getCurrTimestamp(), None))

        #trans,command,username,funds,server,types:userCommand-add(1)
        dataToAudit = data + ',CLT1' + ',1#'
        logQueue.put(dataToAudit)
        #trans,command,username,funds,server,types:accountTransaction-add(11)
        dataToAudit = data + ',HSD1' + ',11#'
        logQueue.put(dataToAudit)

        return data

    elif dataList[1] == "QUOTE":
        dataFromLogs = getQuoteFromLogs(dataList[2],dataList[3],dataList[1])

        if dataFromLogs != 0 and checkIsQuoteStock(dataList[2], dataList[3]) == 1 and in60s(dataFromLogs[3], getCurrTimestamp()) == 1:

            result = str(dataList[2])+','+str(dataList[3])+','+str(dataFromLogs[0])+','+str(dataFromLogs[3])
            #trans,command,userid,stockname,server,types:userCommand-quote(2)
            dataToAudit = data + ',CLT1' + ',2#'
            logQueue.put(dataToAudit)

            return result

        else:

            newdata = dataList[3] + ',' + dataList[2] + '\r'
            dataFromQuote = sendToQuote(newdata).rstrip().split(',')
            dbLogs((dataList[2], dataList[0], dataList[1], dataList[3], dataFromQuote[0], None, None, getCurrTimestamp(), dataFromQuote[4]))
            # userid,stockname,stockprice,timestamp,cryptokey
            result = str(dataList[2])+','+str(dataList[3])+','+dataFromQuote[0]+','+dataFromQuote[3]

            #trans,command,userid,stockname,server,types:userCommand-quote(2)
            dataToAudit = data + ',CLT1' + ',2#'
            logQueue.put(dataToAudit)
            #trans,command,userid,stockname,stockprice,timestamp,cryptokey,server,types:quoteServer(9)
            dataToAudit = data + ',' + dataFromQuote[0]+','+dataFromQuote[3]+','+dataFromQuote[4] + ',QSRV1' + ',9#'
            logQueue.put(dataToAudit)

            return result

    elif dataList[1] == 'BUY':
        #trans,command,username,stockname,funds,server,types:userCommand-buy(3)
        dataToAudit = data+','+'CLT1'+',3#'
        logQueue.put(dataToAudit)

        currFunds = checkAcountFunds(dataList[2])
        if currFunds >= Decimal(dataList[4]):
            newdata = dataList[3] + ',' + dataList[2] + '\r'
            stockprice = checkStockUser(dataList[2], dataList[3])

            commandTimestamp = getCurrTimestamp()
            logTimestamp = checkLogTimestamp(dataList[2],'QUOTE',dataList[3])
            crypto = checkCrypto(dataList[2], dataList[3], 'QUOTE')
            if logTimestamp != 0 and stockprice > 0 and (in60s(logTimestamp, commandTimestamp) == 1):
                dbBuySellLogs((dataList[2], dataList[0], dataList[1], dataList[3], stockprice, dataList[4], getCurrTimestamp(), crypto))


                #trans,command,username,stockname,funds,server,types:systemEvent-database(10)
                dataToAudit = data+','+'HSD1'+',10#'
                logQueue.put(dataToAudit)


                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1])+','+str(dataList[2])+','+str(dataList[4])+','+str(stockprice)+','+str(logTimestamp)+','+crypto
                return result

            else:
                dataFromQuote = sendToQuote(newdata).split(',')

                dbBuySellLogs((dataList[2], dataList[0], dataList[1], dataList[3], dataFromQuote[0], dataList[4], getCurrTimestamp(), dataFromQuote[4]))

                # #trans,command,username,stockname,funds,server,types:userCommand-buy(3)
                # logQueue.put(data+','+dataList[4]+',CLT1'+',3')
                #trans,command,username,stockname,funds,server,types:systemEvent-database(10)
                dataToAudit = data+','+'HSD1'+',10#'
                logQueue.put(dataToAudit)

                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1]+','+dataList[2]+','+dataList[4]+','+dataFromQuote[0]+','+dataFromQuote[3]+','+dataFromQuote[4])
                return result
        else:
            return "User Funds Not Enough!"

    elif dataList[1] == "COMMIT_BUY":

        #trans,command,username,server,types:userCommand-commitBuy(4)
        dataToAudit = data+',CLT1'+',4#'
        logQueue.put(dataToAudit)

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


                    addToStocksDB((dataList[2],snspba[0],stockAmount))
                    deleteBuySellLogs(dataList[2],'BUY')
                    updateFunds(dataList[2], userFundsLeft)


                    #trans,command,username,funds,server,types:accountTransaction-remove(11)
                    dataToAudit = dataList[0]+',remove,'+dataList[2]+','+str(snspba[2])+',CLT1'+',11#'
                    logQueue.put(dataToAudit)
                    #print(dataList[0]+',remove,'+dataList[2]+','+str(snspba[2])+',CLT1'+',14')

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
        result = deleteBuySellLogs(dataList[2],'BUY')
        if result == 1:
            #trans,command,username,server,types:userCommand-cancelBuy(4)
            dataToAudit = data+',CLT1'+',4#'
            logQueue.put(dataToAudit)
            return "BUY Command has been caneled!"
        else:
            #trans,command,username,server,types:userCommand-cancelBuy(4)
            dataToAudit = data+',CLT1'+',4#'
            logQueue.put(dataToAudit)
            return "NO BUY COMMAN IN DB"

    elif dataList[1] == "SELL":

        #trans,command,username,stockname,funds,server,types:userCommand-sell(3)
        dataToAudit = data+','+'CLT1'+',3#'
        logQueue.put(dataToAudit)
        if checkUserOwnStock(dataList[2], dataList[3]) == 0:
            return "User does not own the stocks!"

        amount = checkStockAmount(dataList[2], dataList[3])

        if amount > 0:
            commandTimestamp = getCurrTimestamp()
            logTimestamp = checkLogTimestamp(dataList[2],'QUOTE',dataList[3])
            if logTimestamp != 0 and checkCommandInLog(dataList[2], dataList[3], "QUOTE") == 1 and in60s(logTimestamp, commandTimestamp) == 1:
                stockprice = checkStockUser(dataList[2], dataList[3])

                ownMoney = stockprice * Decimal(amount)

                if ownMoney < Decimal(dataList[4]):
                    return "User money is not enough!"

                crypto = checkCrypto(dataList[2], dataList[3], 'QUOTE')

                dbBuySellLogs((dataList[2], dataList[0], dataList[1], dataList[3], stockprice, dataList[4], getCurrTimestamp(), crypto))


                #trans,command,username,stockname,funds,server,types:systemEvent-database(10)
                dataToAudit = data+','+'HSD1'+',10#'
                logQueue.put(dataToAudit)

                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1])+','+str(dataList[2])+','+str(dataList[4])+','+str(stockprice)+','+str(logTimestamp)+','+crypto
                return result

            else:
                newdata = dataList[3] + ',' + dataList[2] + '\r'
                dataFromQuote = sendToQuote(newdata).split(',')
                ownMoney = Decimal(dataFromQuote[0]) * Decimal(amount)
                if ownMoney < Decimal(dataList[4]):
                    return "User money is not enough!"

                dbBuySellLogs((dataList[2], dataList[0], dataList[1], dataList[3], dataFromQuote[0], dataList[4], getCurrTimestamp(), dataFromQuote[4]))

                # #trans,command,username,stockname,funds,server,types:userCommand-sell(3)
                # logQueue.put(data+','+dataList[4]+',CLT1'+','+',3')
                #trans,command,username,stockname,funds,server,types:systemEvent-database(10)
                dataToAudit = data+','+'HSD1'+',10#'
                logQueue.put(dataToAudit)

                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1]+','+dataList[2]+','+dataList[4]+','+dataFromQuote[0]+','+dataFromQuote[3]+','+dataFromQuote[4])
                return result

        else:
            return "User dose not own the stocks!"

    elif dataList[1] == "COMMIT_SELL":
        #check to see if user has asked for quote within last 60 seconds

        #trans,command,username,server,types:userCommand-commitBuy(4)
        dataToAudit = data+',CLT1'+',4#'
        logQueue.put(dataToAudit)

        check_SELL_in_bsLog = checkCommandInbsLog(dataList[2], 'SELL')

        if check_SELL_in_bsLog == 0:
            return "There is no sell command input!"

        stockname = getBuySellData(dataList[2], 'SELL')[0]
        amount = checkStockAmount(dataList[2], stockname)

        if checkCommandInbsLog(dataList[2], 'SELL') == 1 and amount > 0:

            commitTime = getCurrTimestamp()
            logTimestamp = checkbsLogTimestamp(dataList[2],'SELL')

            if checkIsQuoteStock(dataList[2], stockname) == 1 and in60s(logTimestamp, commitTime) == 1:

                currFunds =  Decimal(checkAcountFunds(dataList[2]))
                snspfd = getBuySellData(dataList[2], 'SELL')

                total = amount * snspfd[1]
                if total >= snspfd[2]:

                    amountCanSell = int(snspfd[2]/snspfd[1])
                    moneyCanGet = amountCanSell * snspfd[1]
                    newFunds = currFunds + moneyCanGet
                    shareLeft = amount - amountCanSell

                    updateStockAmount(dataList[2], snspfd[0], shareLeft)
                    deleteBuySellLogs(dataList[2],'SELL')
                    updateFunds(dataList[2], newFunds)

                    #trans,command,username,funds,server,types:accountTransaction-add(11)
                    dataToAudit = dataList[0]+',add,'+dataList[2]+','+str(snspfd[2])+',CLT1'+',11#'
                    logQueue.put(dataToAudit)

                    result = dataList[2]+','+snspfd[0]+','+str(snspfd[1])+','+str(snspfd[2])+','+str(newFunds)
                    return result

                else:
                    return "ERROR USER OWN AMOUNT NOT ENOUGH!"

            else:

                return "ERROR OVER COMMIT TIME!"

        else:
            return "ERROR SELL COMMAND NOT FIND!"

    elif dataList[1] == "CANCEL_SELL":
        result = deleteBuySellLogs(dataList[2],'SELL')
        if result == 1:
            #trans,command,username,server,types:userCommand-cancelBuy(4)
            dataToAudit = data+',CLT1'+',4#'
            logQueue.put(dataToAudit)
            return "SELL Command has been caneled"
        else:
            #trans,command,username,server,types:userCommand-cancelBuy(4)
            dataToAudit = data+',CLT1'+',4#'
            logQueue.put(dataToAudit)
            return "NO SELL COMMAND IN DB"

    elif dataList[1] == "SET_BUY_AMOUNT":
        #trans,command,username,stockname,funds,server,types:userCommand-setBuyAmount(3)
        dataToAudit = data+',CLT1'+',3#'
        logQueue.put(dataToAudit)
        #trans,command,username,stockname,funds,server,types:systemEvent-setBuyAmount(10)
        dataToAudit = data+',HSD1'+',10#'
        logQueue.put(dataToAudit)

        #with cond:
        #ts = threading.Thread(target=triggers, args=(dataList, cond))

        ts = TRIGGERS(dataList)
        ts.start()
        print('------BUY TRIGGER START------')

        diName = dataList[2]+'-'+dataList[3]
        if diName in buyTriggerQueue:
            if buyTriggerQueue.get(diName).isAlive():
                buyTriggerQueue.get(diName).stop()
                buyTriggerQueue[diName] = ts
            else:
                buyTriggerQueue[diName] = ts
        else:
            buyTriggerQueue.update({diName:ts})

        time.sleep(0.1)
        #cond.wait()

        return "Trigger is hit running..."

    elif dataList[1] == "CANCEL_SET_BUY":
        result = deleteTriggerFromDB(dataList[2], dataList[3], 'SET_BUY_TRIGGER')
        diName = dataList[2]+'-'+dataList[3]

        if result == 1 and diName in buyTriggerQueue and buyTriggerQueue.get(diName).isAlive():
            #trans,command,username,stockname,server,types:userCommand-cancelSetBuy(5)
            dataToAudit = data+',CLT1'+',5#'
            logQueue.put(dataToAudit)
            #trans,command,username,stockname,server,types:systemEvent-cancelSetBuy(12)
            dataToAudit = data+',HSD1'+',12#'
            logQueue.put(dataToAudit)

            buyTriggerQueue.get(diName).stop()
            #buyTriggerQueue.get(diName).join()

            return "CANCEL SET BUY!"
        else:
            #trans,command,username,stockname,server,types:userCommand-cancelSetBuy(5)
            dataToAudit = data+',CLT1'+',5#'
            logQueue.put(dataToAudit)
            return "NO BUY TRIGGER"

    elif dataList[1] == "SET_BUY_TRIGGER":
        #trans,command,username,stockname,stockprice,server,types:userCommand-setBuyTrigger(6)
        dataToAudit = data+',CLT1'+',6#'
        logQueue.put(dataToAudit)
        #trans,command,username,stockname,stockprice,server,types:systemEvent-setBuyTrigger(13)
        dataToAudit = data+',HSD1'+',13#'
        logQueue.put(dataToAudit)

        if checkIsTrigger(dataList[2], dataList[3], dataList[1]) == 1:
            updateTrigger(dataList[2], dataList[3], dataList[1], dataList[4])
        else:
            addToTriggerDB((dataList[2], dataList[3], dataList[1], dataList[4], getCurrTimestamp()))
        return "SET BUY TRIGGER!"

    elif dataList[1] == "SET_SELL_AMOUNT":
        #trans,command,username,stockname,funds,server,types:userCommand-setSellAmount(3)
        dataToAudit = data+',CLT1'+',3#'
        logQueue.put(dataToAudit)
        #trans,command,username,stockname,funds,server,types:systemEvent-setSellAmount(10)
        dataToAudit = data+',HSD1'+',10#'
        logQueue.put(dataToAudit)

        #with cond:
        #ts = threading.Thread(target=triggers, args=(dataList, cond))
        ts = TRIGGERS(dataList)
        ts.start()
        print('------BUY TRIGGER START------')

        diName = dataList[2]+'-'+dataList[3]
        if diName in sellTriggerQueue:
            if sellTriggerQueue.get(diName).isAlive():
                sellTriggerQueue.get(diName).stop()
                sellTriggerQueue[diName] = ts
            else:
                sellTriggerQueue[diName] = ts
        else:
            sellTriggerQueue.update({diName:ts})

        time.sleep(0.1)
        #cond.wait()

        return "Trigger is hit running..."

    elif dataList[1] == "SET_SELL_TRIGGER":
        #trans,command,username,stockname,stockprice,server,types:userCommand-setSellTrigger(6)
        dataToAudit = data+',CLT1'+',3#'
        logQueue.put(dataToAudit)
        #trans,command,username,stockname,stockprice,server,types:systemEvent-setSellTrigger(13)
        dataToAudit = data+',HSD1'+',13#'
        logQueue.put(dataToAudit)

        if checkIsTrigger(dataList[2], dataList[3], dataList[1]) == 1:
            updateTrigger(dataList[2], dataList[3], dataList[1], dataList[4])
        else:
            addToTriggerDB((dataList[2], dataList[3], dataList[1], dataList[4], getCurrTimestamp()))
        return "SET SELL TRIGGER!"

    elif dataList[1] == "CANCEL_SET_SELL":
        result = deleteTriggerFromDB(dataList[2], dataList[3], 'SET_SELL_TRIGGER')
        diName = dataList[2]+'-'+dataList[3]
        if result == 1 and diName in sellTriggerQueue and sellTriggerQueue.get(diName).isAlive():
            #trans,command,username,stockname,server,types:userCommand-cancelSetSell(5)
            dataToAudit = data+',CLT1'+',5#'
            logQueue.put(dataToAudit)
            #trans,command,username,stockname,server,types:systemEvent-cancelSetSell(12)
            dataToAudit = data+',HSD1'+',12#'
            logQueue.put(dataToAudit)

            sellTriggerQueue.get(diName).stop()
            #sellTriggerQueue.get(diName).join()

            return "CANCEL SET SELL!"
        else:
            #trans,command,username,stockname,server,types:userCommand-cancelSetSell(5)
            dataToAudit = data+',CLT1'+',5#'
            logQueue.put(dataToAudit)
            return "NO SELL TRIGGER"

    elif dataList[1] == "DUMPLOG" and len(dataList) == 4:
        #trans,command,username,filename,server,types:userCommand-dumplog1(7)
        dataToAudit = data+',CLT1'+',7#'
        logQueue.put(dataToAudit)

        result = getLogUser(dataList[2])
        return result

    elif dataList[1] == "DUMPLOG" and len(dataList) == 3:
        #trans,command,filename,server,types:userCommand-dumplog2(8)
        dataToAudit = data+',CLT1'+',8#'
        logQueue.put(dataToAudit)

        return getLog()

    elif dataList[1] == "DISPLAY_SUMMARY":
        #trans,command,username,server,types:userCommand-dumplog1(5)
        dataToAudit = data+',CLT1'+',4#'
        logQueue.put(dataToAudit)
        return getSummary(dataList[2])

if __name__ == '__main__':
    cond = threading.Condition()
    lock = threading.Lock()

    logQueue = queue.Queue(maxsize = 15000)
    global buyTriggerQueue
    global sellTriggerQueue

    #{username-stockname:buyTrigger}
    buyTriggerQueue = {}
    #{username-stockname:sellTrigger}
    sellTriggerQueue = {}

    auditIP = '192.168.1.188'
    auditIP2 = "10.0.2.15"
    auditIP3 = "192.168.0.21"
    auditIP4 = "192.168.1.161"
    auditPort = 55565

    auditSocket = socket(AF_INET, SOCK_STREAM)
    auditSocket.connect((auditIP3,auditPort))

    AuditServer = AuditServer(time, logQueue, auditSocket)
    AuditServer.start()


    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootpassword",
        database="dbone"
    )
    mycursor = mydb.cursor()

    recvFromHttp()
    # for b in buyTriggerQueue:
    #     b.join()
    # for s in sellTriggerQueue:
    #     s.join()
    #logQueue.put("GAMEOVER")

    # print(logQueue)
    #AuditServer.join()
