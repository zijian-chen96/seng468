from socket import *
import threading
import mysql.connector
import sys
from datetime import datetime
from decimal import Decimal
import time
import queue
import json
import redis
from concurrent.futures import ThreadPoolExecutor

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
                auditSocket.connect(('auditserver',51000))
                data = self.logQueue.get()
                #print("This data must send to aduit server: " + str(data))
                data = json.dumps(data)
                auditSocket.sendall(data.encode())

        auditSocket.close()


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
            host="mysqldb",
            port=3306,
            user="root",
            password="rootpassword",
            database="dbone"
        )
        mycursor = mydb2.cursor()

        redClient2 = redis.Redis(host="myredis", port=6379, decode_responses=True)

        command = ''
        if self.dataList2[1] == 'SET_BUY_AMOUNT':
            command = 'SET_BUY_TRIGGER'
        else:
            command = 'SET_SELL_TRIGGER'

        if command == 'SET_BUY_TRIGGER':
            btriDataFromRedis = redClient2.get('Btri_'+self.dataList2[2]+'_'+self.dataList2[3])

            if btriDataFromRedis != None:

                holdMoney = Decimal(self.dataList2[4])
                if holdMoneyFromAcount(mycursor, mydb2, self.dataList2[2], self.dataList2[4]) == 1:
                    currFunds =  Decimal(getkAcountFunds(mycursor, mydb2, self.dataList2[2]))

                    # username, transnumber, command, stockname, stockprice, amount, funds, times, cryptokey
                    dbLogs(mycursor, mydb2, (self.dataList2[2], self.dataList2[0], 'BUY-TRIGGER-HOLDER', self.dataList2[3], None, holdMoney, currFunds, getCurrTimestamp(), None))

                    while True:
                        if self.stopped():
                            mycursor.close()
                            mydb2.close()
                            return

                        dataFromQuote = sendToQuote(self.dataList2[3] + ',' + self.dataList2[2] + '\r').split(',')

                        if Decimal(dataFromQuote[0]) <= Decimal(btriDataFromRedis) and Decimal(dataFromQuote[0]) <= holdMoney:

                            userFundsLeft = (holdMoney % Decimal(dataFromQuote[0])) + currFunds
                            stockAmount = int(holdMoney / Decimal(dataFromQuote[0]))

                            addToStocksDB(mycursor, mydb2, (self.dataList2[2],self.dataList2[3],stockAmount))
                            # username, transnumber, command, stockname, stockprice, amount, funds, times, cryptokey
                            dbLogs(mycursor, mydb2, (self.dataList2[2], self.dataList2[0], 'BUY', self.dataList2[3], dataFromQuote[0], self.dataList2[4], currFunds, getCurrTimestamp(), dataFromQuote[4]))
                            updateFunds(mycursor, mydb2, self.dataList2[2],userFundsLeft)

                            break

                        else:
                            #print("current stock price: " + dataFromQuote[0])
                            time.sleep(10)
                    #print('finish exit out of thread!')

        else:
            striDataFromRedis = redClient2.get('Stri_'+self.dataList2[2]+'_'+self.dataList2[3])
            numStocks = getStockAmount(mycursor, mydb2, self.dataList2[2], self.dataList2[3])

            if striDataFromRedis != None and numStocks != 0:
                holdStockAmount = int(Decimal(self.dataList2[4]) / Decimal(striDataFromRedis))

                if numStocks != 0 and holdStockAmountFromAcount(mycursor, mydb2, self.dataList2[2], self.dataList2[3], holdStockAmount) == 1:
                    currFunds = Decimal(getkAcountFunds(mycursor, mydb2, self.dataList2[2]))

                    dbLogs(mycursor, mydb2, (self.dataList2[2], self.dataList2[0], 'SELL-TRIGGER-HOLDER', self.dataList2[3], None, holdStockAmount, currFunds, getCurrTimestamp(), None))

                    while True:
                        if self.stopped():
                            mycursor.close()
                            mydb2.close()
                            return

                        dataFromQuote = sendToQuote(self.dataList2[3] + ',' + self.dataList2[2] + '\r').split(',')
                        numStocksToSell = int(Decimal(self.dataList2[4]) / Decimal(dataFromQuote[0]))

                        if Decimal(dataFromQuote[0]) >= Decimal(striDataFromRedis) and holdStockAmount >= numStocksToSell:

                            moneyCanGet = numStocksToSell * Decimal(dataFromQuote[0])
                            newFunds = currFunds + moneyCanGet

                            #dblock.acquire()
                            updateStockAmount(mycursor, mydb2, self.dataList2[2], self.dataList2[3], (numStocks - numStocksToSell))
                            # username, transnumber, command, stockname, stockprice, amount, funds, times, cryptokey
                            dbLogs(mycursor, mydb2, (self.dataList2[2], self.dataList2[0], 'SELL', self.dataList2[3], dataFromQuote[0], self.dataList2[4], currFunds, getCurrTimestamp(), dataFromQuote[4]))
                            updateFunds(mycursor, mydb2, self.dataList2[2], newFunds)

                            break

                        else:
                            #print("current stock price: " + dataFromQuote[0])
                            time.sleep(10)
                    #print('finish exit out of thread!')
        mycursor.close()
        mydb2.close()

# def recvJob():
#     sSocket = socket(AF_INET, SOCK_STREAM)
#     port = 50000
#     sSocket.bind(('',port))
#     sSocket.listen(5)
#     cSocket, addr = sSocket.accept()
#
#     while True:
#         data = cSocket.recv(1024).decode()
#         if data == "finish":
#             break
#         # if data!="":
#         #     print(data)
#         #     print(jobQueue.qsize())
#         if data:
#             jobQueue.put(data)
#             cSocket.send(("ok").encode())
#             #cSocket.close()


def sendJob():
    while True:
        if finQueue.empty() != True:
            httpSocket = socket(AF_INET, SOCK_STREAM)
            httpSocket.connect(('192.168.1.245',52000))
            data = finQueue.get()
            httpSocket.sendall(data.encode())
            #httpSocket.recv(1024)

    # while True:
    #     if finQueue.empty() != True:
    #         data = finQueue.get()
    #         httpSocket.sendall(data.encode())
    #         httpSocket.recv(1024)



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

    quoteServerSocket.connect(('quoteserve.seng.uvic.ca',4447))
    #quoteServerSocket.connect(('192.168.0.10',44433))

    quoteServerSocket.send(fromUser.encode())

    dataFromQuote = quoteServerSocket.recv(1024).decode()

    quoteServerSocket.close()

    return dataFromQuote


def recvFromHttp(redClient, dList, threadCount):

    mydb = mysql.connector.connect(
        host="mysqldb",
        port=3306,
        user="root",
        password="rootpassword",
        database="dbone"
    )
    mycursor = mydb.cursor()

    for data in dList:
        try:
            #data = cSocket.recv(1024).decode()

            print("Thread #" +str(threadCount)+ " " + getCurrTimestamp()+ " " + "Data recv from HTTP Server: " + data)

            dataFromQuote = commandControl(mydb, mycursor, data, redClient)

            #print("Thread #" +str(i)+ " " + "Data send to Quote Server: " + dataFromQuote)

            finQueue.put(dataFromQuote)

        except:
            print('ERROR during processing...' + ' ' + str(threadCount))
            mycursor.close()
            mydb.close()
            sys.exit()

    mycursor.close()
    mydb.close()


def getkAcountFunds(mycursor, mydb, username): # check the acount funds
    check = "SELECT funds FROM acounts WHERE username = %s"
    mycursor.execute(check, (username,))
    return mycursor.fetchall()[0][0]


def getStockAmount(mycursor, mydb, username, stockname): # check the stock amount the user owned
    try:
        check = "SELECT amount FROM stocks WHERE username = %s and stockname = %s"
        mycursor.execute(check, (username, stockname,))
        result = mycursor.fetchall()[0][0]
        return result
    except:
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


def checkCommandInLog(mycursor, mydb, username, stockname, command):
    check = "SELECT count(username) FROM logs WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0


def checkIsQuoteStock(mycursor, mydb, username, stockname, command):
    check = "SELECT count(stockname) FROM logs WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
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


def getQuoteFromLogs(mycursor, mydb, username, stockname, command):
    if checkCommandInLog(mycursor, mydb, username, stockname, "QUOTE") == 1:
        #quote,sym,userid,timestamp,cryptokey
        check = "SELECT stockprice,stockname,username,times,cryptokey FROM logs WHERE username = %s AND stockname = %s AND command = %s"
        mycursor.execute(check, (username, stockname, command,))
        result = mycursor.fetchall()[0]
        return result
    else:
        return 0


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


def getSummary(mycursor, mydb, username):
    transSummary = getLogUser(mycursor, mydb, username)
    accountSummary = getAccountSummary(mycursor, mydb, username)
    # triggerSummary = getTriggerSummary(mycursor, mydb, username)
    return ('Acount: '+accountSummary+'Transations: '+transSummary)


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
    getAmount =  getStockAmount(mycursor, mydb, username, stockname)
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
        oldShare = getStockAmount(mycursor, mydb, user[0], user[1])
        newShare = user[2] + oldShare
        updateStockAmount(mycursor, mydb, user[0], user[1], newShare)


def removeFromDB(mycursor, mydb, user): # remove the user funds from DB
    currFunds = getkAcountFunds(mycursor, mydb, user[0])
    if currFunds >= user[1]:
        newFunds = currFunds - user[1]
        updateFunds(mycursor, mydb, user[0], newFunds)
    else:
        print("Acount funds is not enough!")


#checks if the command has the correct Input for buy,sell,tirggers, and set
def check_valid_command_BSTS(list):
    if list[4] == '':
        dataToAudit = {'trans': list[0], 'command': list[1], 'username': list[2], 'stockname': list[3], 'funds': -1, 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'message' : 'No funds input', 'types': 'six'}
        logQueue.put(dataToAudit)
        return "Input error"


#checks if the given user exists in the database
def check_valid_user(mycursor, mydb, username):
    check = "Select count(username) From logs Where username = %s"
    mycursor.execute(check, (username,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0


def dbLogs(mycursor, mydb, logInfo):
    ##print('here')
    logFormula = "INSERT INTO logs (username, transnumber, command, stockname, stockprice, amount, funds, times, cryptokey) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    mycursor.execute(logFormula, logInfo)
    mydb.commit()


def red_Quete_HSET(redClient, key, stockprice, qouteTimestamp, cryptokey):
    redClient.hset(key, 'stockprice', stockprice)
    redClient.hset(key, 'qouteTimestamp', qouteTimestamp)
    redClient.hset(key, 'cryptokey', cryptokey)
    redClient.expire(key, 60)


def red_BSLog_HSET(redClient, key, trans, command, moneyAmount):
    redClient.hset(key, 'trans', trans)
    redClient.hset(key, 'command', command)
    redClient.hset(key, 'moneyAmount', moneyAmount)
    redClient.expire(key, 60)


def commandControl(mydb, mycursor, data, redClient):
    dl = data.split(',')
    dataList = [s.strip() for s in dl]

    if dataList[1] == "ADD":
        ##print("Data should be send direct to Aduit Server: " + data)
        addToDB(mycursor, mydb, (dataList[2], dataList[3]))
        dbLogs(mycursor, mydb, (dataList[2], dataList[0], dataList[1], None, None, None, dataList[3], getCurrTimestamp(), None))

        #trans,command,username,funds,server,types:userCommand-add(1)
        #dataToAudit = ",".join([data,"CLT1","one"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'funds': dataList[3], 'server': "CLT1", 'timestamp': getCurrTimestamp(), 'timestamp': getCurrTimestamp(), 'types': 'one'}
        logQueue.put(dataToAudit)
        #trans,command,username,funds,server,types:accountTransaction-add(11)
        #dataToAudit = ",".join([data,"HSD1","eleven"])
        dataToAudit = {'trans': dataList[0], 'action': 'add', 'username': dataList[2], 'funds': dataList[3], 'server': "CLT1", 'timestamp': getCurrTimestamp(), 'types': 'eleven'}
        logQueue.put(dataToAudit)

        return data

    elif dataList[1] == "QUOTE":
        key = ('Q_'+dataList[2]+'_'+dataList[3])
        dataFromRedis = redClient.hvals(key)
        # print(dataFromRedis)

        if  dataFromRedis != []:
            result = str(dataList[2])+','+str(dataList[3])+','+str(dataFromRedis[0])+','+str(dataFromRedis[2])
            #trans,command,userid,stockname,server,types:userCommand-quote(2)
            #dataToAudit = ",".join([data,"CLT1","two"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "CLT1", 'timestamp': getCurrTimestamp(), 'types': 'two'}
            logQueue.put(dataToAudit)

            return result

        else:
            newdata = dataList[3] + ',' + dataList[2] + '\r'
            dataFromQuote = sendToQuote(newdata).strip().split(',')

            dbLogs(mycursor, mydb, (dataList[2], dataList[0], dataList[1], dataList[3], dataFromQuote[0], None, None, getCurrTimestamp(), dataFromQuote[4]))

            #record in redix cache --stockprice, quoteServerTime, cryptokey
            red_Quete_HSET(redClient, key, dataFromQuote[0], dataFromQuote[3], dataFromQuote[4])

            # userid,stockname,stockprice,timestamp,cryptokey
            result = str(dataList[2])+','+str(dataList[3])+','+dataFromQuote[0]+','+dataFromQuote[3]

            #trans,command,userid,stockname,server,types:userCommand-quote(2)
            #dataToAudit = ",".join([data,"CLT1","two"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "CLT1", 'timestamp': getCurrTimestamp(), 'types': 'two'}
            logQueue.put(dataToAudit)
            #trans,command,userid,stockname,stockprice,timestamp,cryptokey,server,types:quoteServer(9)
            #dataToAudit = ",".join([data,dataFromQuote[0],dataFromQuote[3],dataFromQuote[4],"QSRV1","nine"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'price': dataFromQuote[0],'quoteServerTime': dataFromQuote[3],'cryptokey': (dataFromQuote[4]+'\n') , 'server': "QSRV1", 'timestamp': getCurrTimestamp(), 'types': 'nine'}
            logQueue.put(dataToAudit)

            return result

    elif dataList[1] == 'BUY':
        if check_valid_command_BSTS(dataList) == "Input error":
            return "Input error"

        #trans,command,username,stockname,funds,server,types:userCommand-buy(3)
        #dataToAudit = ",".join([data,"CLT2","three"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'types': 'three'}
        logQueue.put(dataToAudit)

        currFunds = getkAcountFunds(mycursor, mydb, dataList[2])
        if currFunds >= Decimal(dataList[4]):
            newdata = dataList[3] + ',' + dataList[2] + '\r'

            #record in the redis cache --trans, command, funds
            red_BSLog_HSET(redClient, ('B_'+dataList[2]+'_'+dataList[3]), dataList[0], dataList[1], dataList[4])
            #record the most recently BUY command
            redClient.rpush(('B_'+dataList[2]), dataList[3])

            #trans,command,username,stockname,funds,server,types:systemEvent-database(10)
            #dataToAudit = ",".join([data,"HSD2","ten"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD2", 'timestamp': getCurrTimestamp(), 'types': 'ten'}
            logQueue.put(dataToAudit)

            #userid,stockname,amount,qouteTimestamp
            result = str(dataList[1])+','+str(dataList[2])+','+str(dataList[3])+','+str(dataList[4])

            return result

        else:

            return "User Funds Not Enough!"

    elif dataList[1] == "COMMIT_BUY":
        #trans,command,username,server,types:userCommand-commitBuy(4)
        #dataToAudit = ",".join([data,"CLT2","four"])

        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'types': 'four'}
        logQueue.put(dataToAudit)

        #return the stockname
        stockname = redClient.rpop('B_'+dataList[2])
        buyDataFromRedis = redClient.hvals('B_'+dataList[2]+'_'+str(stockname)) #data --trans, command, moneyAmount
        quoteDataFromRedis = redClient.hvals('Q_'+dataList[2]+'_'+str(stockname)) #data --stockprice, quoteServerTime, crypto
        # print(stockname)
        # print(buyDataFromRedis)
        # print(quoteDataFromRedis)

        if buyDataFromRedis == [] or stockname == None:
            return "ERROR BUY COMMAND NOT FIND!"

        if quoteDataFromRedis != []:
            currFunds =  Decimal(getkAcountFunds(mycursor, mydb, dataList[2]))

            if currFunds >= Decimal(buyDataFromRedis[2]) and Decimal(quoteDataFromRedis[0]) <= Decimal(buyDataFromRedis[2]):
                userFundsLeft = (Decimal(buyDataFromRedis[2]) % Decimal(quoteDataFromRedis[0])) + (currFunds - Decimal(buyDataFromRedis[2]))
                stockAmount = int(Decimal(buyDataFromRedis[2]) / Decimal(quoteDataFromRedis[0]))

                addToStocksDB(mycursor, mydb, (dataList[2],stockname,stockAmount))
                dbLogs(mycursor, mydb, (dataList[2], buyDataFromRedis[0], dataList[1], stockname, quoteDataFromRedis[0], buyDataFromRedis[2], currFunds, getCurrTimestamp(), None))
                updateFunds(mycursor, mydb, dataList[2], userFundsLeft)

                #trans,command,username,funds,server,types:accountTransaction-remove(11)
                #dataToAudit = ",".join([dataList[0],'remove',dataList[2],str(snspba[2]),"CLT2","eleven"])
                dataToAudit = {'trans': dataList[0], 'action': 'remove', 'username': dataList[2], 'funds': buyDataFromRedis[2], 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'types': 'eleven'}
                logQueue.put(dataToAudit)

                #username,stockname,stockprice,amount,funds
                result = dataList[2]+','+stockname+','+quoteDataFromRedis[0]+','+buyDataFromRedis[2]+','+str(userFundsLeft)

                return result

            else:
                return "User Funds Not Enough!"

        else:
            newdata = stockname + ',' + dataList[2] + '\r'
            dataFromQuote = sendToQuote(newdata).strip().split(',')

            currFunds =  Decimal(getkAcountFunds(mycursor, mydb, dataList[2]))

            if currFunds >= Decimal(buyDataFromRedis[2]) and Decimal(dataFromQuote[0]) <= Decimal(buyDataFromRedis[2]):
                userFundsLeft = (Decimal(buyDataFromRedis[2]) % Decimal(dataFromQuote[0])) + (currFunds - Decimal(buyDataFromRedis[2]))
                stockAmount = int(Decimal(buyDataFromRedis[2]) / Decimal(dataFromQuote[0]))

                addToStocksDB(mycursor, mydb, (dataList[2],stockname,stockAmount))
                dbLogs(mycursor, mydb, (dataList[2], buyDataFromRedis[0], dataList[1], stockname, dataFromQuote[0], buyDataFromRedis[2], currFunds, getCurrTimestamp(), None))
                updateFunds(mycursor, mydb, dataList[2], userFundsLeft)

                #trans,command,username,funds,server,types:accountTransaction-remove(11)
                #dataToAudit = ",".join([dataList[0],'remove',dataList[2],str(snspba[2]),"CLT2","eleven"])
                dataToAudit = {'trans': dataList[0], 'action': 'remove', 'username': dataList[2], 'funds': str(buyDataFromRedis[2]), 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'types': 'eleven'}
                logQueue.put(dataToAudit)

                #username,stockname,stockprice,amount,funds
                result = dataList[2]+','+stockname+','+str(dataFromQuote[0])+','+str(buyDataFromRedis[2])+','+str(userFundsLeft)

                return result

            return "User Funds Not Enough!"

    elif dataList[1] == "CANCEL_BUY":
        stockname = redClient.rpop('B_'+dataList[2])
        buyDataFromRedis = redClient.hvals('B_'+dataList[2]+'_'+str(stockname)) #data --trans, command, moneyAmount

        if stockname != None or buyDataFromRedis != []:
            redClient.delete('B_'+dataList[2]+'_'+str(stockname))
            #trans,command,username,server,types:userCommand-cancelBuy(4)
            #dataToAudit = ",".join([data,"CLT2","four"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'types': 'four'}
            logQueue.put(dataToAudit)

            return "BUY Command has been caneled!"
        else:
            #trans,command,username,server,types:userCommand-cancelBuy(4)
            #dataToAudit = ",".join([data,"CLT2","four"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'types': 'four'}
            logQueue.put(dataToAudit)

            return "NO BUY COMMAN IN DB"

    elif dataList[1] == "SELL":
        if check_valid_command_BSTS(dataList) == "Input error":
            return "Input error"

        #trans,command,username,stockname,funds,server,types:userCommand-sell(3)
        #dataToAudit = ",".join([data,"CLT2","three"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'types': 'three'}
        logQueue.put(dataToAudit)

        stockAmount = getStockAmount(mycursor, mydb, dataList[2], dataList[3])

        if stockAmount > 0:
            quoteDataFromRedis = redClient.hvals('Q_'+dataList[2]+'_'+dataList[3]) #data --stockprice, quoteServerTime, crypto

            if quoteDataFromRedis != []:
                ownStockAmount = Decimal(quoteDataFromRedis[0]) * Decimal(stockAmount)

                if ownStockAmount < Decimal(dataList[4]):
                    return "User money is not enough!"

                #record in the redis cache --trans, command, funds
                red_BSLog_HSET(redClient, ('S_'+dataList[2]+'_'+dataList[3]), dataList[0], dataList[1], dataList[4])
                #record the most recently SELL command
                redClient.rpush(('S_'+dataList[2]), dataList[3])

                #trans,command,username,stockname,funds,server,types:systemEvent-database(10)
                #dataToAudit = ",".join([data,"HSD2","ten"])
                dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD2", 'timestamp': getCurrTimestamp(), 'types': 'ten'}
                logQueue.put(dataToAudit)

                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1])+','+str(dataList[2])+','+str(dataList[4])+','+str(quoteDataFromRedis[0])+','+str(quoteDataFromRedis[1])+','+quoteDataFromRedis[2]

                return result

            else:
                newdata = dataList[3] + ',' + dataList[2] + '\r'
                dataFromQuote = sendToQuote(newdata).split(',')
                ownStockAmount = Decimal(dataFromQuote[0]) * Decimal(stockAmount)

                if ownStockAmount < Decimal(dataList[4]):
                    return "User money is not enough!"

                #record in the redis cache --trans, command, funds
                red_BSLog_HSET(redClient, ('S_'+dataList[2]+'_'+dataList[3]), dataList[0], dataList[1], dataList[4])
                #record the most recently SELL command
                redClient.rpush(('S_'+dataList[2]), dataList[3])

                #trans,command,username,stockname,funds,server,types:systemEvent-database(10)
                #dataToAudit = ",".join([data,"HSD2","ten"])
                dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD2", 'timestamp': getCurrTimestamp(), 'types': 'ten'}
                logQueue.put(dataToAudit)

                #userid,stockname,amount,stockprice,qouteTimestamp,cryptokey
                result = str(dataList[1]+','+dataList[2]+','+dataList[4]+','+dataFromQuote[0]+','+dataFromQuote[3]+','+dataFromQuote[4])

                return result

        else:
            return "User dose not own the stocks!"

    elif dataList[1] == "COMMIT_SELL":
        #trans,command,username,server,types:userCommand-commitBuy(4)
        #dataToAudit = ",".join([data,"CLT2","four"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'types': 'four'}
        logQueue.put(dataToAudit)

        #return the stockname
        stockname = redClient.rpop('S_'+dataList[2])
        sellDataFromRedis = redClient.hvals('S_'+dataList[2]+'_'+str(stockname)) #data --trans, command, moneyAmount
        quoteDataFromRedis = redClient.hvals('Q_'+dataList[2]+'_'+str(stockname)) #data --stockprice, quoteServerTime, crypto
        # print(stockname)
        # print(sellDataFromRedis)
        # print(quoteDataFromRedis)

        stockAmount = getStockAmount(mycursor, mydb, dataList[2], stockname)

        if sellDataFromRedis == [] or stockname == None:
            return "ERROR BUY COMMAND NOT FIND!"

        if quoteDataFromRedis != []:
            currFunds =  Decimal(getkAcountFunds(mycursor, mydb, dataList[2]))
            ownStockAmount = Decimal(quoteDataFromRedis[0]) * Decimal(stockAmount)

            if ownStockAmount >= Decimal(sellDataFromRedis[2]):

                amountCanSell = int(Decimal(sellDataFromRedis[2]) / Decimal(quoteDataFromRedis[0]))
                moneyCanGet = amountCanSell * Decimal(quoteDataFromRedis[0])
                newFunds = currFunds + moneyCanGet
                shareLeft = stockAmount - amountCanSell

                updateStockAmount(mycursor, mydb, dataList[2], stockname, shareLeft)
                dbLogs(mycursor, mydb, (dataList[2], sellDataFromRedis[0], dataList[1], stockname, quoteDataFromRedis[0], sellDataFromRedis[2], currFunds, getCurrTimestamp(), None))
                updateFunds(mycursor, mydb, dataList[2], newFunds)

                #trans,command,username,funds,server,types:accountTransaction-add(11)
                #dataToAudit = ",".join([dataList[0],'add',dataList[2],str(snspfd[2]),"CLT2","eleven"])
                dataToAudit = {'trans': dataList[0], 'action': 'add', 'username': dataList[2], 'funds': sellDataFromRedis[2], 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'types': 'eleven'}
                logQueue.put(dataToAudit)

                result = dataList[2]+','+stockname+','+quoteDataFromRedis[0]+','+sellDataFromRedis[2]+','+str(newFunds)

                return result

            else:
                return "ERROR USER OWN AMOUNT NOT ENOUGH!"

        else:
            newdata = stockname + ',' + dataList[2] + '\r'
            dataFromQuote = sendToQuote(newdata).strip().split(',')

            currFunds =  Decimal(getkAcountFunds(mycursor, mydb, dataList[2]))
            ownStockAmount = Decimal(dataFromQuote[0]) * Decimal(stockAmount)

            if ownStockAmount >= Decimal(sellDataFromRedis[2]):

                amountCanSell = int(Decimal(sellDataFromRedis[2]) / Decimal(dataFromQuote[0]))
                moneyCanGet = amountCanSell * Decimal(dataFromQuote[0])
                newFunds = currFunds + moneyCanGet
                shareLeft = stockAmount - amountCanSell

                updateStockAmount(mycursor, mydb, dataList[2], stockname, shareLeft)
                dbLogs(mycursor, mydb, (dataList[2], sellDataFromRedis[0], dataList[1], stockname, dataFromQuote[0], sellDataFromRedis[2], currFunds, getCurrTimestamp(), None))
                updateFunds(mycursor, mydb, dataList[2], newFunds)

                #trans,command,username,funds,server,types:accountTransaction-add(11)
                #dataToAudit = ",".join([dataList[0],'add',dataList[2],str(snspfd[2]),"CLT2","eleven"])
                dataToAudit = {'trans': dataList[0], 'action': 'add', 'username': dataList[2], 'funds': sellDataFromRedis[2], 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'types': 'eleven'}
                logQueue.put(dataToAudit)

                result = dataList[2]+','+stockname+','+dataFromQuote[0]+','+sellDataFromRedis[2]+','+str(newFunds)

                return result

            else:
                return "ERROR USER OWN AMOUNT NOT ENOUGH!"

    elif dataList[1] == "CANCEL_SELL":
        stockname = redClient.rpop('S_'+dataList[2])
        sellDataFromRedis = redClient.hvals('S_'+dataList[2]+'_'+str(stockname)) #data --trans, command, moneyAmount

        if stockname != None or sellDataFromRedis != []:
            redClient.delete('S_'+dataList[2]+'_'+str(stockname))
            #trans,command,username,server,types:userCommand-cancelBuy(4)
            #dataToAudit = ",".join([data,"CLT2","four"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'types': 'four'}
            logQueue.put(dataToAudit)

            return "SELL Command has been caneled"
        else:
            #trans,command,username,server,types:userCommand-cancelBuy(4)
            #dataToAudit = ",".join([data,"CLT2","four"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT2", 'timestamp': getCurrTimestamp(), 'types': 'four'}
            logQueue.put(dataToAudit)

            return "NO SELL COMMAND IN DB"

    elif dataList[1] == "DUMPLOG" and len(dataList) == 4:
        #trans,command,username,filename,server,types:userCommand-dumplog1(7)
        #dataToAudit = ",".join([data,"CLT4","seven"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'filename': dataList[3], 'server': "CLT4", 'timestamp': getCurrTimestamp(), 'types': 'seven'}
        logQueue.put(dataToAudit)

        result = getLogUser(mycursor, mydb, dataList[2])
        #cSocket.sendall(result.encode())
        while True:
            if len(queueDic) == 1:
                break

        return (result + "the end")

    elif dataList[1] == "DUMPLOG" and len(dataList) == 3:
        #trans,command,filename,server,types:userCommand-dumplog2(8)
        #dataToAudit = ",".join([data,"CLT4","eight"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'filename': dataList[2], 'server': "CLT4", 'timestamp': getCurrTimestamp(), 'types': 'eight'}
        logQueue.put(dataToAudit)

        result = getLog(mycursor, mydb)
        #cSocket.sendall(result.encode())
        while True:
            if len(queueDic) == 1:
                break
            # else:
            #     print(queueDic)
            #     time.sleep(10)

        return (result + "the end")

    elif dataList[1] == "DISPLAY_SUMMARY":
        #trans,command,username,server,types:userCommand-dumplog1(5)
        #dataToAudit = ",".join([data,"CLT4","four"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'server': "CLT4", 'timestamp': getCurrTimestamp(), 'types': 'four'}
        logQueue.put(dataToAudit)

        result = getSummary(mycursor, mydb, dataList[2])
        #cSocket.sendall(result.encode())
        return (result + "the end")

    elif dataList[1] == "SET_BUY_AMOUNT":
        if check_valid_command_BSTS(dataList) == "Input error":
            return "Input error"

        #trans,command,username,stockname,funds,server,types:userCommand-setBuyAmount(3)
        #dataToAudit = ",".join([data,"CLT3","three"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "CLT3", 'timestamp': getCurrTimestamp(), 'types': 'three'}
        logQueue.put(dataToAudit)

        #trans,command,username,stockname,funds,server,types:systemEvent-setBuyAmount(10)
        #dataToAudit = ",".join([data,"HSD3","ten"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD3", 'timestamp': getCurrTimestamp(), 'types': 'ten'}
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
        key = 'Btri_'+dataList[2]+'_'+dataList[3]
        btriDataFromRedis = redClient.get(key)
        diName = dataList[2]+'-'+dataList[3]

        if btriDataFromRedis != None and diName in buyTriggerQueue:
            #trans,command,username,stockname,server,types:userCommand-cancelSetBuy(5)
            #dataToAudit = ",".join([data,"CLT3","five"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "CLT3", 'timestamp': getCurrTimestamp(), 'types': 'five'}
            logQueue.put(dataToAudit)

            #trans,command,username,stockname,server,types:systemEvent-cancelSetBuy(12)
            #dataToAudit = ",".join([data,"HSD3","twelve"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "HSD3", 'timestamp': getCurrTimestamp(), 'types': 'twelve'}
            logQueue.put(dataToAudit)

            try:
                buyTriggerQueue.get(diName).stop()
            except:
                pass

            return "CANCEL SET BUY!"
        else:
            #trans,command,username,stockname,server,types:userCommand-cancelSetBuy(5)
            #dataToAudit = ",".join([data,"CLT3","five"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "CLT3", 'timestamp': getCurrTimestamp(), 'types': 'five'}
            logQueue.put(dataToAudit)

            return "NO BUY TRIGGER"

    elif dataList[1] == "SET_BUY_TRIGGER":
        if check_valid_command_BSTS(dataList) == "Input error":
            return "Input error"

        #trans,command,username,stockname,stockprice,server,types:userCommand-setBuyTrigger(6)
        #dataToAudit = ",".join([data,"CLT3","six"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "CLT3", 'timestamp': getCurrTimestamp(), 'types': 'three'}
        logQueue.put(dataToAudit)

        #trans,command,username,stockname,stockprice,server,types:systemEvent-setBuyTrigger(13)
        #dataToAudit = ",".join([data,"HSD3","thirteen"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD3", 'timestamp': getCurrTimestamp(), 'types': 'ten'}
        logQueue.put(dataToAudit)

        triDataFromRedis = redClient.set(('Btri_'+dataList[2]+'_'+dataList[3]), dataList[4])

        return "SET BUY TRIGGER!"

    elif dataList[1] == "SET_SELL_AMOUNT":
        if check_valid_command_BSTS(dataList) == "Input error":
            return "Input error"

        #trans,command,username,stockname,funds,server,types:userCommand-setSellAmount(3)
        #dataToAudit = ",".join([data,"CLT3","three"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "CLT3", 'timestamp': getCurrTimestamp(), 'types': 'three'}
        logQueue.put(dataToAudit)

        #trans,command,username,stockname,funds,server,types:systemEvent-setSellAmount(10)
        #dataToAudit = ",".join([data,"HSD3","ten"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD3", 'timestamp': getCurrTimestamp(), 'types': 'ten'}
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
        if check_valid_command_BSTS(dataList) == "Input error":
            return "Input error"

        #trans,command,username,stockname,stockprice,server,types:userCommand-setSellTrigger(6)
        #dataToAudit = ",".join([data,"CLT3","three"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "CLT3", 'timestamp': getCurrTimestamp(), 'types': 'three'}
        logQueue.put(dataToAudit)

        #trans,command,username,stockname,stockprice,server,types:systemEvent-setSellTrigger(13)
        #dataToAudit = ",".join([data,"HSD3","thirteen"])
        dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'funds': dataList[4], 'server': "HSD3", 'timestamp': getCurrTimestamp(), 'types': 'ten'}
        logQueue.put(dataToAudit)

        triDataFromRedis = redClient.set(('Stri_'+dataList[2]+'_'+dataList[3]), dataList[4])

        return "SET SELL TRIGGER!"

    elif dataList[1] == "CANCEL_SET_SELL":
        key = 'Stri_'+dataList[2]+'_'+dataList[3]
        striDataFromRedis = redClient.get(key)
        diName = dataList[2]+'-'+dataList[3]

        if striDataFromRedis != None and diName in sellTriggerQueue:
            #trans,command,username,stockname,server,types:userCommand-cancelSetSell(5)
            #dataToAudit = ",".join([data,"CLT3","five"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "CLT3", 'timestamp': getCurrTimestamp(), 'types': 'five'}
            logQueue.put(dataToAudit)

            #trans,command,username,stockname,server,types:systemEvent-cancelSetSell(12)
            #dataToAudit = ",".join([data,"HSD3","twelve"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "HSD3", 'timestamp': getCurrTimestamp(), 'types': 'twelve'}
            logQueue.put(dataToAudit)
            try:
                sellTriggerQueue.get(diName).stop()
            except:
                pass

            return "CANCEL SET SELL!"
        else:
            #trans,command,username,stockname,server,types:userCommand-cancelSetSell(5)
            #dataToAudit = ",".join([data,"CLT3","five"])
            dataToAudit = {'trans': dataList[0], 'command': dataList[1], 'username': dataList[2], 'stockname': dataList[3], 'server': "CLT3", 'timestamp': getCurrTimestamp(), 'types': 'five'}
            logQueue.put(dataToAudit)

            return "NO SELL TRIGGER"
    else:
        return "ERROR COMMAND"


if __name__ == '__main__':
    global logQueue
    global jobQueue
    global finQueue
    global queueDic
    global threadDic

    global buyTriggerQueue
    global sellTriggerQueue

    #{username-stockname:buyTrigger}
    buyTriggerQueue = {}
    #{username-stockname:sellTrigger}
    sellTriggerQueue = {}

    queueDic = {}
    threadDic = {}

    #thread 2 only use to sent the log to AuditServer
    logQueue = queue.Queue(maxsize = 100000)
    jobQueue = queue.Queue(maxsize = 1000000)
    finQueue = queue.Queue(maxsize = 1000000)

    AuditServer = AuditServer(time, logQueue)
    AuditServer.start()

    # recvThread = threading.Thread(target = recvJob)
    # recvThread.start()
    sendThread = threading.Thread(target = sendJob)
    sendThread.start()

    pool = redis.ConnectionPool(host="myredis", port=6379, decode_responses=True)
    redClient = redis.Redis(connection_pool=pool)
    redClient.flushall()


    sSocket = socket(AF_INET, SOCK_STREAM)
    port = 50000
    sSocket.bind(('',port))
    sSocket.listen(10)

    executor = ThreadPoolExecutor(max_workers = 60)

    currName = ""
    threadCount = 0
    while True:
        cSocket, addr = sSocket.accept()
        data = ""
        while True:
            newData = cSocket.recv(10240).decode()
            data += newData
            #print ("the start")
            if newData[-7:] == "the end":
                #print(data)
                data = data.split('the end')[0]
                # cSocket.sendall(("OK").encode())
                break

        dList = data.split('\n')
        threadCount += 1
        future = executor.submit(recvFromHttp, redClient, dList, threadCount)
        cSocket.close()



    AuditServer.join()
    recvThread.join()
    sendThread.join()
