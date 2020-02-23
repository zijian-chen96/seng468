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
        cSocket, addr = sSocket.accept()
        while True:
            # data = jobQueue.get()
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

    if dataList[1] == "ADD":
        ##print("Data should be send direct to Aduit Server: " + data)
        addToDB(mycursor, mydb, (dataList[2], dataList[3]))
        dbLogs(mycursor, mydb, (dataList[2], dataList[0], dataList[1], None, None, None, dataList[3], getCurrTimestamp(), None))

        #trans,command,username,funds,server,types:userCommand-add(1)
        #dataToAudit = ",".join([data,"CLT1","one"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'funds': dataList[3], 'server': "CLT1", 'types': 'one'}
        logQueue.put(dataToAudit)
        #trans,command,username,funds,server,types:accountTransaction-add(11)
        #dataToAudit = ",".join([data,"HSD1","eleven"])
        dataToAudit = {'trans': dataList[0], 'action': 'add', 'username': dataList[2], 'funds': dataList[3], 'server': "CLT1", 'types': 'eleven'}
        logQueue.put(dataToAudit)

        return data

    elif dataList[1] == "QUOTE":
        dataFromLogs = getQuoteFromLogs(mycursor, mydb, dataList[2],dataList[3],dataList[1])

        if dataFromLogs != 0 and checkIsQuoteStock(mycursor, mydb, dataList[2], dataList[3]) == 1 and in60s(dataFromLogs[3], getCurrTimestamp()) == 1:

            result = str(dataList[2])+','+str(dataList[3])+','+str(dataFromLogs[0])+','+str(dataFromLogs[3])
            #trans,command,userid,stockname,server,types:userCommand-quote(2)
            #dataToAudit = ",".join([data,"CLT1","two"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "CLT1", 'types': 'two'}
            logQueue.put(dataToAudit)

            return result

        else:
            newdata = dataList[3] + ',' + dataList[2] + '\r'
            dataFromQuote = sendToQuote(newdata).strip().split(',')
            dbLogs(mycursor, mydb, (dataList[2], dataList[0], dataList[1], dataList[3], dataFromQuote[0], None, None, getCurrTimestamp(), dataFromQuote[4]))
            # userid,stockname,stockprice,timestamp,cryptokey
            result = str(dataList[2])+','+str(dataList[3])+','+dataFromQuote[0]+','+dataFromQuote[3]

            #trans,command,userid,stockname,server,types:userCommand-quote(2)
            #dataToAudit = ",".join([data,"CLT1","two"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "CLT1", 'types': 'two'}
            logQueue.put(dataToAudit)
            #trans,command,userid,stockname,stockprice,timestamp,cryptokey,server,types:quoteServer(9)
            #dataToAudit = ",".join([data,dataFromQuote[0],dataFromQuote[3],dataFromQuote[4],"QSRV1","nine"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'price': dataFromQuote[0],'quoteServerTime': dataFromQuote[3],'cryptokey': dataFromQuote[4] , 'server': "QSRV1", 'types': 'nine'}
            logQueue.put(dataToAudit)

            return result

    elif dataList[1] == 'BUY':
        #trans,command,username,stockname,funds,server,types:userCommand-buy(3)
        #dataToAudit = ",".join([data,"CLT2","three"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "CLT2", 'types': 'three'}
        logQueue.put(dataToAudit)

        currFunds = getkAcountFunds(mycursor, mydb, dataList[2])
        if currFunds >= Decimal(dataList[4]):
            newdata = dataList[3] + ',' + dataList[2] + '\r'

            stockprice = checkStockUser(mycursor, mydb, dataList[2], dataList[3])
            commandTimestamp = getCurrTimestamp()
            logTimestamp = checkLogTimestamp(mycursor, mydb, dataList[2],'QUOTE',dataList[3])
            crypto = checkCrypto(mycursor, mydb, dataList[2], dataList[3], 'QUOTE')

            if logTimestamp != 0 and stockprice > 0 and (in60s(logTimestamp, commandTimestamp) == 1):
                dbBuySellLogs(mycursor, mydb, (dataList[2], dataList[0], dataList[1], dataList[3], stockprice, dataList[4], getCurrTimestamp(), crypto))
                #trans,command,username,stockname,funds,server,types:systemEvent-database(10)
                #dataToAudit = ",".join([data,"HSD2","ten"])
                dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD2", 'types': 'ten'}
                logQueue.put(dataToAudit)

                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1])+','+str(dataList[2])+','+str(dataList[4])+','+str(stockprice)+','+str(logTimestamp)+','+crypto

                return result

            else:
                dataFromQuote = sendToQuote(newdata).split(',')
                dbBuySellLogs(mycursor, mydb, (dataList[2], dataList[0], dataList[1], dataList[3], dataFromQuote[0], dataList[4], getCurrTimestamp(), dataFromQuote[4]))

                #trans,command,username,stockname,funds,server,types:systemEvent-database(10)
                #dataToAudit = ",".join([data,"HSD2","ten"])
                dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD2", 'types': 'ten'}
                logQueue.put(dataToAudit)
                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1]+','+dataList[2]+','+dataList[4]+','+dataFromQuote[0]+','+dataFromQuote[3]+','+dataFromQuote[4])
                return result
        else:

            return "User Funds Not Enough!"

    elif dataList[1] == "COMMIT_BUY":
        #trans,command,username,server,types:userCommand-commitBuy(4)
        #dataToAudit = ",".join([data,"CLT2","four"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT2", 'types': 'four'}
        logQueue.put(dataToAudit)

        check_BUY_in_bsLog = checkCommandInbsLog(mycursor, mydb, dataList[2], 'BUY')

        if check_BUY_in_bsLog == 0:
            return "There is no buy command input!"

        stockname = getBuySellData(mycursor, mydb, dataList[2], 'BUY')[0]

        if check_BUY_in_bsLog == 1:

            commitTimestamp = getCurrTimestamp()
            logTimestamp = getbsLogTimestamp(mycursor, mydb, dataList[2],'BUY')

            if checkIsQuoteStock(mycursor, mydb, dataList[2], stockname) == 1 and in60s(logTimestamp, commitTimestamp) == 1:

                currFunds =  Decimal(getkAcountFunds(mycursor, mydb, dataList[2]))
                snspba = getBuyAmount(mycursor, mydb, dataList[2])

                if currFunds >= snspba[2]:

                    userFundsLeft = (snspba[2] % snspba[1]) + (currFunds - snspba[2])
                    stockAmount = int(snspba[2] / snspba[1])

                    addToStocksDB(mycursor, mydb, (dataList[2],snspba[0],stockAmount))
                    deleteBuySellLogs(mycursor, mydb, dataList[2],'BUY')
                    updateFunds(mycursor, mydb, dataList[2], userFundsLeft)

                    #trans,command,username,funds,server,types:accountTransaction-remove(11)
                    #dataToAudit = ",".join([dataList[0],'remove',dataList[2],str(snspba[2]),"CLT2","eleven"])
                    dataToAudit = {'trans': dataList[0], 'action': 'remove', 'username': dataList[2], 'funds': str(snspba[2]), 'server': "CLT2", 'types': 'eleven'}
                    logQueue.put(dataToAudit)

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

        result = deleteBuySellLogs(mycursor, mydb, dataList[2],'BUY')
        if result == 1:
            #trans,command,username,server,types:userCommand-cancelBuy(4)
            #dataToAudit = ",".join([data,"CLT2","four"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT2", 'types': 'four'}
            logQueue.put(dataToAudit)

            return "BUY Command has been caneled!"
        else:
            #trans,command,username,server,types:userCommand-cancelBuy(4)
            #dataToAudit = ",".join([data,"CLT2","four"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT2", 'types': 'four'}
            logQueue.put(dataToAudit)

            return "NO BUY COMMAN IN DB"

    elif dataList[1] == "SELL":
        #trans,command,username,stockname,funds,server,types:userCommand-sell(3)
        #dataToAudit = ",".join([data,"CLT2","three"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "CLT2", 'types': 'three'}
        logQueue.put(dataToAudit)

        if checkUserOwnStock(mycursor, mydb, dataList[2], dataList[3]) == 0:
            return "User does not own the stocks!"

        amount = checkStockAmount(mycursor, mydb, dataList[2], dataList[3])

        if amount > 0:
            commandTimestamp = getCurrTimestamp()
            logTimestamp = checkLogTimestamp(mycursor, mydb, dataList[2],'QUOTE',dataList[3])
            if logTimestamp != 0 and checkCommandInLog(mycursor, mydb, dataList[2], dataList[3], "QUOTE") == 1 and in60s(logTimestamp, commandTimestamp) == 1:
                stockprice = checkStockUser(mycursor, mydb, dataList[2], dataList[3])

                ownMoney = stockprice * Decimal(amount)

                if ownMoney < Decimal(dataList[4]):
                    return "User money is not enough!"

                crypto = checkCrypto(mycursor, mydb, dataList[2], dataList[3], 'QUOTE')

                dbBuySellLogs(mycursor, mydb, (dataList[2], dataList[0], dataList[1], dataList[3], stockprice, dataList[4], getCurrTimestamp(), crypto))

                #trans,command,username,stockname,funds,server,types:systemEvent-database(10)
                #dataToAudit = ",".join([data,"HSD2","ten"])
                dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD2", 'types': 'ten'}
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

                dbBuySellLogs(mycursor, mydb, (dataList[2], dataList[0], dataList[1], dataList[3], dataFromQuote[0], dataList[4], getCurrTimestamp(), dataFromQuote[4]))

                #trans,command,username,stockname,funds,server,types:systemEvent-database(10)
                #dataToAudit = ",".join([data,"HSD2","ten"])
                dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD2", 'types': 'ten'}
                logQueue.put(dataToAudit)

                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1]+','+dataList[2]+','+dataList[4]+','+dataFromQuote[0]+','+dataFromQuote[3]+','+dataFromQuote[4])

                return result

        else:
            return "User dose not own the stocks!"

    elif dataList[1] == "COMMIT_SELL":
        #check to see if user has asked for quote within last 60 seconds

        #trans,command,username,server,types:userCommand-commitBuy(4)
        #dataToAudit = ",".join([data,"CLT2","four"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT2", 'types': 'four'}
        logQueue.put(dataToAudit)

        check_SELL_in_bsLog = checkCommandInbsLog(mycursor, mydb, dataList[2], 'SELL')

        if check_SELL_in_bsLog == 0:
            return "There is no sell command input!"

        stockname = getBuySellData(mycursor, mydb, dataList[2], 'SELL')[0]
        amount = checkStockAmount(mycursor, mydb, dataList[2], stockname)

        if checkCommandInbsLog(mycursor, mydb, dataList[2], 'SELL') == 1 and amount > 0:

            commitTime = getCurrTimestamp()
            logTimestamp = getbsLogTimestamp(mycursor, mydb, dataList[2],'SELL')

            if checkIsQuoteStock(mycursor, mydb, dataList[2], stockname) == 1 and in60s(logTimestamp, commitTime) == 1:

                currFunds =  Decimal(getkAcountFunds(mycursor, mydb, dataList[2]))
                snspfd = getBuySellData(mycursor, mydb, dataList[2], 'SELL')

                total = amount * snspfd[1]
                if total >= snspfd[2]:

                    amountCanSell = int(snspfd[2]/snspfd[1])
                    moneyCanGet = amountCanSell * snspfd[1]
                    newFunds = currFunds + moneyCanGet
                    shareLeft = amount - amountCanSell

                    updateStockAmount(mycursor, mydb, dataList[2], snspfd[0], shareLeft)
                    deleteBuySellLogs(mycursor, mydb, dataList[2],'SELL')
                    updateFunds(mycursor, mydb, dataList[2], newFunds)

                    #trans,command,username,funds,server,types:accountTransaction-add(11)
                    #dataToAudit = ",".join([dataList[0],'add',dataList[2],str(snspfd[2]),"CLT2","eleven"])
                    dataToAudit = {'trans': dataList[0], 'action': 'add', 'username': dataList[2], 'funds': str(snspfd[2]), 'server': "CLT2", 'types': 'eleven'}
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

        result = deleteBuySellLogs(mycursor, mydb, dataList[2],'SELL')
        if result == 1:
            #trans,command,username,server,types:userCommand-cancelBuy(4)
            #dataToAudit = ",".join([data,"CLT2","four"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT2", 'types': 'four'}
            logQueue.put(dataToAudit)

            return "SELL Command has been caneled"
        else:
            #trans,command,username,server,types:userCommand-cancelBuy(4)
            #dataToAudit = ",".join([data,"CLT2","four"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT2", 'types': 'four'}
            logQueue.put(dataToAudit)

            return "NO SELL COMMAND IN DB"

    elif dataList[1] == "DUMPLOG" and len(dataList) == 4:
        #trans,command,username,filename,server,types:userCommand-dumplog1(7)
        #dataToAudit = ",".join([data,"CLT4","seven"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'filename': dataList[3], 'server': "CLT4", 'types': 'seven'}
        logQueue.put(dataToAudit)

        result = getLogUser(mycursor, mydb, dataList[2])
        cSocket.sendall(result.encode())
        return "the end"

    elif dataList[1] == "DUMPLOG" and len(dataList) == 3:
        #trans,command,filename,server,types:userCommand-dumplog2(8)
        #dataToAudit = ",".join([data,"CLT4","eight"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'filename': dataList[2], 'server': "CLT4", 'types': 'eight'}
        logQueue.put(dataToAudit)

        result = getLog(mycursor, mydb)
        cSocket.sendal(result.encode())
        return "the end"

    elif dataList[1] == "DISPLAY_SUMMARY":
        #trans,command,username,server,types:userCommand-dumplog1(5)
        #dataToAudit = ",".join([data,"CLT4","four"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT4", 'types': 'four'}
        logQueue.put(dataToAudit)

        result = getSummary(mycursor, mydb, dataList[2])
        cSocket.sendall(result.encode())
        return "the end"

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
    port = 50005
    sSocket.bind(('',port))
    sSocket.listen(5)
    # cSocket, addr = sSocket.accept()

    mydb = mysql.connector.connect(
        host="localhost",
        port=52000,
        user="root",
        password="rootpassword",
        database="dbone"
    )
    mycursor = mydb.cursor()

    recvFromHttp(sSocket)

    #logQueue.put("GAMEOVER")

    AuditServer.join()
