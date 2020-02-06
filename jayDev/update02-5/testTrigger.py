from socket import *
import threading
import mysql.connector
import sys
from datetime import datetime
from decimal import Decimal
import time


def getTriggerStockPrice(username, stockname, command):
    check = "SELECT stockprice FROM bslogs WHERE username = %s AND stockname = %s AND command = %s"
    mycursor.execute(check, (username, stockname, command,))
    return mycursor.fetchall()[0][0]


def run(cond):
    #cond.acquire()
    #run2(cond)
    command = ''
    if dataList[0] == 'SET_BUY_AMOUNT':
        command = 'SET_BUY_TRIGGER'
    else:
        command = 'SET_SELL_TRIGGER'

    #while command == 'SET_SELL_TRIGGER':
    with cond:
        trigPrice = getTriggerStockPrice('oY01WVirLr','S', 'BUY')
        print("sell: " + str(trigPrice))

        time.sleep(1)
        cond.notify()
    # cond.release()
    # cond.notify()

    #while command == 'SET_BUY_TRIGGER':

    # buyStockPrice = getTriggerStockPrice('oY01WVirLr', 'S', 'BUY')
    # print("buy: " + str(buyStockPrice))

def run2(cond, ts):
    with cond:
        ts.start()
        cond.wait()


if __name__ == '__main__':
    logQueue = []
    abc = False

    cond = threading.Condition()
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="rootpassword",
        database="dbone"
    )
    mycursor = mydb.cursor()
    global dataList
    dataList = []
    dataList.append('SET_BUY_AMOUNT')

    ts = threading.Thread(target=run, args=(cond,))
    #ts2 = threading.Thread(target=run2, args=(cond,))
    #ts2.start()


    run2(cond,ts)
    #run2(cond)

    print('fjdfkdjkfjkfjkjfkjfdkkdfjkdjkdfj')

    #while True:
