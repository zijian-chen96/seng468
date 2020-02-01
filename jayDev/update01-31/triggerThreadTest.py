from socket import *
import threading
import mysql.connector
import sys
from datetime import datetime
from decimal import Decimal

def checkIsTrigger(username, stockname, command):
    check = "SELECT count(command) FROM triggers WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
    result = mycursor.fetchall()[0][0]
    if result > 0:
        return 1
    else:
        return 0

def getTriggerStockPrice(username, stockname, command):
    check = "SELECT stockprice FROM triggers WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
    return mycursor.fetchall()[0][0]
    

class TriggerServer(threading.Thread):
    def __init__(self, mydb, dataList):
        threading.Thread.__init__(self)
        self.logQueue = logQueue
        self.mydb = mydb
        self.dataList = dataList



    def run(self):
        mycursor = mydb.cursor()
        print('I am in the triggers function')
        #while True:
        if checkIsTrigger(dataList[2], dataList[3], dataList[1]) == 1:
            print('triggers server is working...')



if __name__ == '__main__':
    logQueue = []
    dataList = ['1','SET_BUY_AMOUNT','jiosesdo','aaa','20.00']
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

    TriggerServer = TriggerServer(mydb, dataList)
    TriggerServer.start()
