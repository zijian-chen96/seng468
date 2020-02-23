from socket import *
import threading
import mysql.connector
import sys
from datetime import datetime
from decimal import Decimal
import time
import queue
import json

#sudo iptables -A INPUT -p tcp --dport 10000:60000 -j ACCEPT
#sudo /etc/init.d/mysql restart
#sudo lsof -i :50000
#sudo kill -9 50000
#sudo docker cp update0220_auditserver_1:/auditServer/logsfile.xml logsfile.xml


class AuditServer(threading.Thread):
    def __init__(self, time, logQueue):
        threading.Thread.__init__(self)
        self.logQueue = logQueue
        self.time = time

    def run(self):

        while True:
            if self.logQueue.empty() != True:
                auditSocket = socket(AF_INET, SOCK_STREAM)
                auditSocket.connect(('',51000))

                data = self.logQueue.get()

                data = json.dumps(data)
                auditSocket.sendall(data.encode())

                auditSocket.close()
                #print("This data must send to aduit server: " + data)


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

        mydb2 = mysql.connector.connect(
            host="localhost",
            port=52000,
            user="root",
            password="rootpassword",
            database="dbone"
        )
        mycursor = mydb2.cursor()

        command = ''
        if self.dataList2[1] == 'SET_BUY_AMOUNT':
            command = 'SET_BUY_TRIGGER'
        else:
            command = 'SET_SELL_TRIGGER'

        while command == 'SET_BUY_TRIGGER':
            if checkIsTrigger(mycursor, mydb2, self.dataList2[2], self.dataList2[3], command) == 1:
                buyStockPrice = getTriggerStockPrice(mycursor, mydb2, self.dataList2[2], self.dataList2[3], command)

                holdMoney = Decimal(self.dataList2[4])
                if holdMoneyFromAcount(mycursor, mydb2, self.dataList2[2], self.dataList2[4]) == 1:
                    currFunds =  Decimal(getkAcountFunds(mycursor, mydb2, self.dataList2[2]))

                    # username, transnumber, command, stockname, stockprice, amount, funds, times, cryptokey
                    dbLogs(mycursor, mydb2, (self.dataList2[2], self.dataList2[0], 'BUY-TRIGGER-HOLDER', self.dataList2[3], None, holdMoney, currFunds, getCurrTimestamp(), None))

                    while True:
                        if self.stopped():
                            return

                        dataFromQuote = sendToQuote(self.dataList2[3] + ',' + self.dataList2[2] + '\r').split(',')

                        if Decimal(dataFromQuote[0]) <= buyStockPrice and Decimal(dataFromQuote[0]) <= holdMoney:

                            userFundsLeft = (holdMoney % Decimal(dataFromQuote[0])) + currFunds
                            stockAmount = int(holdMoney / Decimal(dataFromQuote[0]))

                            addToStocksDB(mycursor, mydb2, (self.dataList2[2],self.dataList2[3],stockAmount))
                            # username, transnumber, command, stockname, stockprice, amount, funds, times, cryptokey
                            dbLogs(mycursor, mydb2, (self.dataList2[2], self.dataList2[0], 'BUY', self.dataList2[3], dataFromQuote[0], self.dataList2[4], currFunds, getCurrTimestamp(), dataFromQuote[4]))
                            updateFunds(mycursor, mydb2, self.dataList2[2],userFundsLeft)

                            #deleteTriggerFromDB(mycursor, mydb, self.dataList2[2],self.dataList2[3],command)
                            break

                        else:
                            #print("current stock price: " + dataFromQuote[0])
                            time.sleep(10)
                    #print('finish exit out of thread!')

                    break

                else:
                    #print("User funds is not enough!")
                    break

            else:
                #print('TRIGGER NOT FOUND!')
                break

        while command == 'SET_SELL_TRIGGER':
            if checkIsTrigger(mycursor, mydb2, self.dataList2[2], self.dataList2[3], command) == 1:
                sellStockPrice = getTriggerStockPrice(mycursor, mydb2, self.dataList2[2],self.dataList2[3],command)
                numStocks = checkStockAmount(mycursor, mydb2, self.dataList2[2], self.dataList2[3])
                holdStockAmount = int(Decimal(self.dataList2[4])/sellStockPrice)
                if numStocks != 0 and holdStockAmountFromAcount(mycursor, mydb2, self.dataList2[2], self.dataList2[3], holdStockAmount) == 1:

                    currFunds = Decimal(getkAcountFunds(mycursor, mydb2, self.dataList2[2]))

                    dbLogs(mycursor, mydb2, (self.dataList2[2], self.dataList2[0], 'SELL-TRIGGER-HOLDER', self.dataList2[3], None, holdStockAmount, currFunds, getCurrTimestamp(), None))

                    while True:
                        if self.stopped():
                            return

                        dataFromQuote = sendToQuote(self.dataList2[3] + ',' + self.dataList2[2] + '\r').split(',')
                        numStocksToSell = int(Decimal(self.dataList2[4]) / Decimal(dataFromQuote[0]))

                        if Decimal(dataFromQuote[0]) >= sellStockPrice and holdStockAmount >= numStocksToSell:


                            moneyCanGet = numStocksToSell * Decimal(dataFromQuote[0])
                            newFunds = currFunds + moneyCanGet
                            #dblock.acquire()
                            updateStockAmount(mycursor, mydb2, self.dataList2[2], self.dataList2[3], (numStocks-numStocksToSell))
                            dbLogs(mycursor, mydb2, (self.dataList2[2], self.dataList2[0], 'SELL', self.dataList2[3], dataFromQuote[0], self.dataList2[4], currFunds, getCurrTimestamp(), dataFromQuote[4]))
                            updateFunds(mycursor, mydb2, self.dataList2[2], newFunds)

                            #deleteTriggerFromDB(mycursor, mydb, self.dataList2[2],self.dataList2[3],command)

                            break

                        else:
                            #print("current stock price: " + dataFromQuote[0])
                            time.sleep(10)
                    #print('finish exit out of thread!')

                    break

                else:
                    #print("User stock amount is not enough!")
                    break
            else:
                #print('TRIGGER NOT FOUND!')
                break


def getCurrTimestamp():
    dateTimeObj = datetime.now()
    ##print(dateTimeObj)

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
    quoteServerSocket.connect(('192.168.0.10',44433))

    quoteServerSocket.send(fromUser.encode())

    dataFromQuote = quoteServerSocket.recv(1024).decode()

    quoteServerSocket.close()

    return dataFromQuote


def recvFromHttp(sSocket):

    try:
        while True:
            # data = jobQueue.get()
            cSocket, addr = sSocket.accept()
            data = cSocket.recv(1024).decode()
            if data:
                #print("Data recv from HTTP Server: " + data)

                dataFromQuote = commandControl(data, cSocket)

                #print("Data send to Quote Server: " + dataFromQuote)

                cSocket.sendall(dataFromQuote.encode())
                #finQueue.put(dataFromQuote)

    except:
        sys.exit()


def getkAcountFunds(mycursor, mydb, username): # check the acount funds
    check = "SELECT funds FROM acounts WHERE username = %s"
    mycursor.execute(check, (username,))
    return mycursor.fetchall()[0][0]


def checkStockAmount(mycursor, mydb, username, stockname): # check the stock amount the user owned
    if checkUserOwnStock(mycursor, mydb, username, stockname) == 1:
        check = "SELECT amount FROM stocks WHERE username = %s and stockname = %s"
        mycursor.execute(check, (username, stockname,))
        return mycursor.fetchall()[0][0]
    else:
        return 0

def checkUserOwnStock(mycursor, mydb, username, stockname):
    check = "SELECT count(username) FROM stocks WHERE username = %s and stockname = %s"
    mycursor.execute(check, (username, stockname,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0



def checkAcountUser(mycursor, mydb, username): # check is the user already in DB or not
    check = "SELECT count(%s) FROM acounts WHERE username = %s"
    mycursor.execute(check, (username, username,))
    result = mycursor.fetchall()[0][0]
    if result == 1:
        return 1
    else:
        return 0


def checkStockUser(mycursor, mydb, username, stockname): # check is the user owned the stock
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


def checkLogTimestamp(mycursor, mydb, username, command, stockname):
    if checkCommandInLog(mycursor, mydb, username,stockname,"QUOTE") == 1:
        check = "SELECT times FROM logs WHERE username = %s AND command = %s AND stockname = %s ORDER BY transnumber DESC LIMIT 1"
        mycursor.execute(check,(username, command, stockname))
        result = mycursor.fetchall()[0][0]
        return result
    else:
        return 0


def getbsLogTimestamp(mycursor, mydb, username, command):
    check = "SELECT times FROM bslogs WHERE username = %s AND command = %s ORDER BY transnumber DESC LIMIT 1"
    mycursor.execute(check,(username, command,))
    result = mycursor.fetchall()[0][0]
    return result


def getBuyAmount(mycursor, mydb, username):
    check = "SELECT stockname,stockprice,amount FROM bslogs WHERE username = %s ORDER BY transnumber DESC LIMIT 1"
    mycursor.execute(check,(username,))
    result = mycursor.fetchall()[0]
    return result


def getBuySellData(mycursor, mydb, username, command):
    check = "SELECT stockname,stockprice,amount FROM bslogs WHERE username = %s AND command = %s ORDER BY transnumber DESC LIMIT 1"
    mycursor.execute(check,(username, command,))
    result = mycursor.fetchall()[0]
    return result


def checkCommandInLog(mycursor, mydb, username, stockname, command):
    check = "SELECT count(username) FROM logs WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0


def checkCommandInbsLog(mycursor, mydb, username, command):
    check = "SELECT count(username) FROM bslogs WHERE username = %s AND command = %s"
    mycursor.execute(check, (username, command,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0


def checkIsQuoteStock(mycursor, mydb, username, stockname):
    check = "SELECT count(stockname) FROM logs WHERE username = %s AND stockname = %s"
    mycursor.execute(check, (username, stockname,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0


def checkCrypto(mycursor, mydb, username, stockname, command):
    if checkCommandInLog(mycursor, mydb, username, stockname, command) == 1:
        check = "SELECT cryptokey FROM logs WHERE username = %s AND stockname = %s AND command = %s ORDER BY transnumber DESC LIMIT 1"
        mycursor.execute(check, (username, stockname, command,))
        result = mycursor.fetchall()[0][0]
        return result
    else:
        return 0


def checkIsTrigger(mycursor, mydb, username, stockname, command):
    check = "SELECT count(command) FROM triggers WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0

def updateTrigger(mycursor, mydb, username, stockname, command, stockprice):
    updateFormula = "UPDATE triggers SET stockprice = %s WHERE username = %s and stockname = %s and command = %s"
    mycursor.execute(updateFormula, (stockprice, username, stockname, command,))
    mydb.commit()

def getQuoteFromLogs(mycursor, mydb, username, stockname, command):
    if checkCommandInLog(mycursor, mydb, username, stockname, "QUOTE") == 1:
        #quote,sym,userid,timestamp,cryptokey
        check = "SELECT stockprice,stockname,username,times,cryptokey FROM logs WHERE username = %s AND stockname = %s AND command = %s"
        mycursor.execute(check, (username, stockname, command,))
        result = mycursor.fetchall()[0]
        return result
    else:
        return 0

def getTriggerStockPrice(mycursor, mydb, username, stockname, command):
    check = "SELECT stockprice FROM triggers WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
    return mycursor.fetchall()[0][0]


def getLogUser(mycursor, mydb, username): # get one user's transation log
    getlog = "SELECT * FROM logs WHERE username = %s"
    mycursor.execute(getlog, (username,))
    result = mycursor.fetchall()
    s = ''
    for i in result:
        for j in i:
            s += str(j)+' '
        s += '\n'
    return s


def getLog(mycursor, mydb): # get all transation log
    getlog = "SELECT * FROM logs"
    mycursor.execute(getlog)
    result = mycursor.fetchall()
    s = ''
    for i in result:
        for j in i:
            s += str(j)+' '
        s += '\n'
    return s


def getAccountSummary(mycursor, mydb, username):
    getAccount = "SELECT * FROM acounts WHERE username = %s"
    mycursor.execute(getAccount, (username,))
    result = mycursor.fetchall()
    s = ''
    for i in result:
        for j in i:
            s += str(j)+' '
        s += '\n'
    return s


def getTriggerSummary(mycursor, mydb, username):
    getTrigger = "SELECT * FROM triggers WHERE username = %s"
    mycursor.execute(getTrigger,(username,))
    result = mycursor.fetchall()
    s = ''
    for i in result:
        for j in i:
            s += str(j)+' '
        s += '\n'
    return s


def getSummary(mycursor, mydb, username):
    transSummary = getLogUser(mycursor, mydb, username)
    accountSummary = getAccountSummary(mycursor, mydb, username)
    triggerSummary = getTriggerSummary(mycursor, mydb, username)
    return ('Acount: '+accountSummary+'Trigger_Set: '+triggerSummary+'Transations: '+transSummary)


def holdMoneyFromAcount(mycursor, mydb, username, amount):
    getFunds =  getkAcountFunds(mycursor, mydb, username)
    newFunds = getFunds - Decimal(amount)
    if getFunds >= Decimal(amount):
        holdMoneyFormula = "UPDATE acounts SET funds = %s WHERE username = %s"
        mycursor.execute(holdMoneyFormula, (newFunds,username))
        mydb.commit()
        return 1
    else:
        return 0


def holdStockAmountFromAcount(mycursor, mydb, username, stockname, amount):
    getAmount =  checkStockAmount(mycursor, mydb, username, stockname)
    newAmount = getAmount - Decimal(amount)
    if getAmount >= Decimal(amount):
        holdStockAmountFormula = "UPDATE stocks SET amount = %s WHERE username = %s"
        mycursor.execute(holdStockAmountFormula, (newAmount,username))
        mydb.commit()
        return 1
    else:
        return 0


def updateFunds(mycursor, mydb, username, funds): # update the user acount funds
    updateFormula = "UPDATE acounts SET funds = %s WHERE username = %s"
    mycursor.execute(updateFormula, (funds, username,))
    mydb.commit()


def updateStockAmount(mycursor, mydb, username, stockname, amount): # update the stock amount the user owned
    updateFormula = "UPDATE stocks SET amount = %s WHERE username = %s AND stockname = %s"
    mycursor.execute(updateFormula, (amount, username, stockname,))
    mydb.commit()


def addToDB(mycursor, mydb, user): # # add the user into DB if is not in the DB else update the funds
    if checkAcountUser(mycursor, mydb, user[0]) == 0:
        addFormula = "INSERT INTO acounts (username, funds) VALUES (%s, %s)"
        mycursor.execute(addFormula, user)
        mydb.commit()
    else:
        newFunds = getkAcountFunds(mycursor, mydb, user[0]) + Decimal(user[1])
        updateFunds(mycursor, mydb, user[0], newFunds)


def addToStocksDB(mycursor, mydb, user):
    if checkUserOwnStock(mycursor, mydb, user[0],user[1]) == 0:
        addFormula = "INSERT INTO stocks (username, stockname, amount) VALUES (%s,%s,%s)"
        mycursor.execute(addFormula, user)
        mydb.commit()
    else:
        oldShare = checkStockAmount(mycursor, mydb, user[0], user[1])
        newShare = user[2] + oldShare
        updateStockAmount(mycursor, mydb, user[0], user[1], newShare)


def addToTriggerDB(mycursor, mydb, user):
    addFormula = "INSERT INTO triggers (username, stockname, command, stockprice, times) VALUES (%s,%s,%s,%s,%s)"
    mycursor.execute(addFormula, user)
    mydb.commit()


def deleteTriggerFromDB(mycursor, mydb, username, stockname, command):
    if checkIsTrigger(mycursor, mydb, username, stockname, command) == 1:
        deleteFormula = "DELETE FROM triggers WHERE username = %s AND stockname = %s AND command = %s"
        mycursor.execute(deleteFormula, (username,stockname,command,))
        mydb.commit()
        return 1
    else:
        return 0


def removeFromDB(mycursor, mydb, user): # remove the user funds from DB
    currFunds = getkAcountFunds(mycursor, mydb, user[0])
    if currFunds >= user[1]:
        newFunds = currFunds - user[1]
        updateFunds(mycursor, mydb, user[0], newFunds)
    else:
        print("Acount funds is not enough!")


def dbLogs(mycursor, mydb, logInfo):
    ##print('here')
    logFormula = "INSERT INTO logs (username, transnumber, command, stockname, stockprice, amount, funds, times, cryptokey) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    mycursor.execute(logFormula, logInfo)
    mydb.commit()


def dbBuySellLogs(mycursor, mydb, logInfo):
    logFormula = "INSERT INTO bslogs (username, transnumber, command, stockname, stockprice, amount, times, cryptokey) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    mycursor.execute(logFormula, logInfo)
    mydb.commit()


def deleteBuySellLogs(mycursor, mydb, username, command):
    if checkCommandInbsLog(mycursor, mydb, username, command) == 1:
        checkBSLogs = "SELECT * FROM bslogs WHERE username = %s ORDER BY transnumber DESC LIMIT 1"
        mycursor.execute(checkBSLogs, (username,))
        result = mycursor.fetchall()[0]

        #calculate the currFunds
        accountFunds = getkAcountFunds(mycursor, mydb, username)
        currFunds = accountFunds - result[5]

        #add to dbLogs
        dbLogs(mycursor, mydb, (result[0], result[1], result[2], result[3], result[4], result[5], (currFunds+result[5]), getCurrTimestamp(), result[7]))

        #remove from bslogs
        deleteFormula = "DELETE FROM bslogs WHERE username = %s ORDER BY transnumber DESC LIMIT 1"
        mycursor.execute(deleteFormula, (username,))
        mydb.commit()
        return 1
    else:
        return 0


def commandControl(data, cSocket):
    dl = data.split(',')
    dataList = [s.strip() for s in dl]
    #print(dataList)

    mydb = mysql.connector.connect(
        host="localhost",
        port=52000,
        user="root",
        password="rootpassword",
        database="dbone"
    )
    mycursor = mydb.cursor()

    if dataList[1] == "SET_BUY_AMOUNT":
        #trans,command,username,stockname,funds,server,types:userCommand-setBuyAmount(3)
        #dataToAudit = ",".join([data,"CLT3","three"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "CLT3", 'types': 'three'}
        logQueue.put(dataToAudit)

        #trans,command,username,stockname,funds,server,types:systemEvent-setBuyAmount(10)
        #dataToAudit = ",".join([data,"HSD3","ten"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD3", 'types': 'ten'}
        logQueue.put(dataToAudit)

        ts = TRIGGERS(dataList)
        ts.deamon = True
        ts.start()

        diName = dataList[2]+'-'+dataList[3]
        if diName in buyTriggerQueue:
            try:
                # if buyTriggerQueue.get(diName).is_alive():
                buyTriggerQueue.get(diName).stop()
                buyTriggerQueue[diName] = ts
            except:
                buyTriggerQueue[diName] = ts
        else:
            buyTriggerQueue.update({diName:ts})

        return "Trigger is hit running..."

    elif dataList[1] == "CANCEL_SET_BUY":

        result = deleteTriggerFromDB(mycursor, mydb, dataList[2], dataList[3], 'SET_BUY_TRIGGER')
        diName = dataList[2]+'-'+dataList[3]

        if result == 1 and diName in buyTriggerQueue:
            #trans,command,username,stockname,server,types:userCommand-cancelSetBuy(5)
            #dataToAudit = ",".join([data,"CLT3","five"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "CLT3", 'types': 'five'}
            logQueue.put(dataToAudit)

            #trans,command,username,stockname,server,types:systemEvent-cancelSetBuy(12)
            #dataToAudit = ",".join([data,"HSD3","twelve"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "HSD3", 'types': 'twelve'}
            logQueue.put(dataToAudit)

            try:
                buyTriggerQueue.get(diName).stop()
            except:
                pass

            return "CANCEL SET BUY!"
        else:
            #trans,command,username,stockname,server,types:userCommand-cancelSetBuy(5)
            #dataToAudit = ",".join([data,"CLT3","five"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "CLT3", 'types': 'five'}
            logQueue.put(dataToAudit)

            return "NO BUY TRIGGER"

    elif dataList[1] == "SET_BUY_TRIGGER":

        #trans,command,username,stockname,stockprice,server,types:userCommand-setBuyTrigger(6)
        #dataToAudit = ",".join([data,"CLT3","six"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "CLT3", 'types': 'six'}
        logQueue.put(dataToAudit)

        #trans,command,username,stockname,stockprice,server,types:systemEvent-setBuyTrigger(13)
        #dataToAudit = ",".join([data,"HSD3","thirteen"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD3", 'types': 'thirteen'}
        logQueue.put(dataToAudit)

        if checkIsTrigger(mycursor, mydb, dataList[2], dataList[3], dataList[1]) == 1:
            updateTrigger(mycursor, mydb, dataList[2], dataList[3], dataList[1], dataList[4])
        else:
            addToTriggerDB(mycursor, mydb, (dataList[2], dataList[3], dataList[1], dataList[4], getCurrTimestamp()))

        return "SET BUY TRIGGER!"

    elif dataList[1] == "SET_SELL_AMOUNT":
        #trans,command,username,stockname,funds,server,types:userCommand-setSellAmount(3)
        #dataToAudit = ",".join([data,"CLT3","three"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "CLT3", 'types': 'three'}
        logQueue.put(dataToAudit)

        #trans,command,username,stockname,funds,server,types:systemEvent-setSellAmount(10)
        #dataToAudit = ",".join([data,"HSD3","ten"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD3", 'types': 'ten'}
        logQueue.put(dataToAudit)

        ts = TRIGGERS(dataList)
        ts.deamon = True
        ts.start()

        diName = dataList[2]+'-'+dataList[3]
        if diName in sellTriggerQueue:
            try:
            #if sellTriggerQueue.get(diName).is_alive():
                sellTriggerQueue.get(diName).stop()
                sellTriggerQueue[diName] = ts
            except:
                sellTriggerQueue[diName] = ts
        else:
            sellTriggerQueue.update({diName:ts})

        return "Trigger is hit running..."

    elif dataList[1] == "SET_SELL_TRIGGER":

        #trans,command,username,stockname,stockprice,server,types:userCommand-setSellTrigger(6)
        #dataToAudit = ",".join([data,"CLT3","three"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "CLT3", 'types': 'three'}
        logQueue.put(dataToAudit)

        #trans,command,username,stockname,stockprice,server,types:systemEvent-setSellTrigger(13)
        #dataToAudit = ",".join([data,"HSD3","thirteen"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD3", 'types': 'thirteen'}
        logQueue.put(dataToAudit)

        if checkIsTrigger(mycursor, mydb, dataList[2], dataList[3], dataList[1]) == 1:
            updateTrigger(mycursor, mydb, dataList[2], dataList[3], dataList[1], dataList[4])
        else:
            addToTriggerDB(mycursor, mydb, (dataList[2], dataList[3], dataList[1], dataList[4], getCurrTimestamp()))

        return "SET SELL TRIGGER!"

    elif dataList[1] == "CANCEL_SET_SELL":

        result = deleteTriggerFromDB(mycursor, mydb, dataList[2], dataList[3], 'SET_SELL_TRIGGER')
        diName = dataList[2]+'-'+dataList[3]
        if result == 1 and diName in sellTriggerQueue:
            #trans,command,username,stockname,server,types:userCommand-cancelSetSell(5)
            #dataToAudit = ",".join([data,"CLT3","five"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "CLT3", 'types': 'five'}
            logQueue.put(dataToAudit)

            #trans,command,username,stockname,server,types:systemEvent-cancelSetSell(12)
            #dataToAudit = ",".join([data,"HSD3","twelve"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "HSD3", 'types': 'twelve'}
            logQueue.put(dataToAudit)
            try:
                sellTriggerQueue.get(diName).stop()
            except:
                pass

            return "CANCEL SET SELL!"
        else:
            #trans,command,username,stockname,server,types:userCommand-cancelSetSell(5)
            #dataToAudit = ",".join([data,"CLT3","five"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "CLT3", 'types': 'five'}
            logQueue.put(dataToAudit)

            return "NO SELL TRIGGER"


if __name__ == '__main__':
    global logQueue

    global buyTriggerQueue
    global sellTriggerQueue

    #{username-stockname:buyTrigger}
    buyTriggerQueue = {}
    #{username-stockname:sellTrigger}
    sellTriggerQueue = {}

    #thread 2 only use to sent the log to AuditServer
    logQueue = queue.Queue(maxsize = 10000)


    AuditServer = AuditServer(time, logQueue)
    AuditServer.start()

    sSocket = socket(AF_INET, SOCK_STREAM)
    port = 50003
    sSocket.bind(('',port))
    sSocket.listen(5)
    # cSocket, addr = sSocket.accept()


    recvFromHttp(sSocket)


    #logQueue.put("GAMEOVER")

    AuditServer.join()
