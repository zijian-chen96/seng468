from socket import *
import sys
from xml.dom import minidom
from datetime import datetime
import json
import queue
import threading
import mysql.connector
#xmllint --schema logfile.xsd --noout logsfile.xml


class logServer(threading.Thread):
    def __init__(self, logQueue):
        threading.Thread.__init__(self)
        self.logQueue = logQueue

    def run(self):
        sSocket = socket(AF_INET, SOCK_STREAM)
        #print('this is the audit server')

        sSocket.bind(("", 51000))
        sSocket.listen(10)
        #print('listening for connection')

        #print('accepted')

        try:
            while True:
                connection, addr = sSocket.accept()
                transactions = ""
                transactions = connection.recv(1024).decode()
                if transactions != "":
                    #print(str(transactions))
                    transactionsDic = json.loads(transactions)
                    self.logQueue.put(transactionsDic)
                connection.close()
        except:
            print('error 11')
            connection.send("error")
            connection.close()
        print('error 22')
        connection.close()
        sSocket.close()


def DBGood():
    mydb = mysql.connector.connect(
        host="mysqldb",
        port=3306,
        user="root",
        password="rootpassword",
        database="dbone"
    )

    mycursor = mydb.cursor()
    mycursor.execute("DROP TABLE IF EXISTS acounts")
    mycursor.execute("DROP TABLE IF EXISTS stocks")
    mycursor.execute("DROP TABLE IF EXISTS logs")
    mydb.commit()

    mycursor.execute("CREATE TABLE acounts (username VARCHAR(255) PRIMARY KEY, funds DECIMAL(10,2))")
    mycursor.execute("CREATE TABLE stocks (username VARCHAR(255), stockname VARCHAR(255), amount DECIMAL(10,2))")
    mycursor.execute("CREATE TABLE logs (username VARCHAR(255), transnumber INTEGER(10), command VARCHAR(255), stockname VARCHAR(255), stockprice DECIMAL(10,2), amount DECIMAL(10,2), funds DECIMAL(10,2), times BIGINT(15), cryptokey VARCHAR(255))")
    mycursor.execute("SHOW TABLES")
    for db in mycursor:
        print(db)
    mycursor.close()
    mydb.close()


def main():
    #xml_str = root.toprettyxml()
    DBGood()

    save_path_file = "logsfile.xml"

    with open(save_path_file, 'ab') as f:
        f.write(("<?xml version=\"1.0\" ?>\n").encode())
        f.write(("<log>\n").encode())

    while True:
        if logQueue.empty() != True:
            #sb = transactions.split("")
            #transactionsList = [s.strip() for s in sb]
            transactionsDic = logQueue.get()
            print("Total jobs left: " + str(logQueue.qsize()))
            node = detTag(transactionsDic)
            with open('logsfile.xml', 'ab') as f:
                f.write(node.encode())


def detTag(data): #determine the tag of the input
    tag = ''
    if data['types'] == "one":
        #types:userCommand-add(1)
        return ("<userCommand>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<command>{}</command>\n"
                "\t\t<username>{}</username>\n"
                "\t\t<funds>{}</funds>\n"
                "</userCommand>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['command'],
                data['username'],
                data['funds']))

    elif data['types'] == "two":
        #types:userCommand-quote(2)
        return ("<userCommand>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<command>{}</command>\n"
                "\t\t<username>{}</username>\n"
                "\t\t<stockSymbol>{}</stockSymbol>\n"
                "</userCommand>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['command'],
                data['username'],
                data['stockname']))

    elif data['types'] == "three":
        #types:userCommand-buy(3)-sell(3)-setBuyAmount(3)-setSellAmount(3)
        return ("<userCommand>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<command>{}</command>\n"
                "\t\t<username>{}</username>\n"
                "\t\t<stockSymbol>{}</stockSymbol>\n"
                "\t\t<funds>{}</funds>\n"
                "</userCommand>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['command'],
                data['username'],
                data['stockname'],
                data['funds']))

    elif data['types'] == "four":
        #types:userCommand-commitBuy(4)-commitSell(4)-cancelBuy(4)-cancelSell(4)
        return ("<userCommand>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<command>{}</command>\n"
                "\t\t<username>{}</username>\n"
                "</userCommand>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['command'],
                data['username']))

    elif data['types'] == "five":
        #types:userCommand-cancelSetBuy(5)-cancelSetSell(5)
        return ("<userCommand>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<command>{}</command>\n"
                "\t\t<username>{}</username>\n"
                "\t\t<stockSymbol>{}</stockSymbol>\n"
                "</userCommand>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['command'],
                data['username'],
                data['stockname']))

    elif data['types'] == "six":
        #types:userCommand-setBuyTrigger(6)-setSellTrigger(6)
        return ("<userCommand>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<command>{}</command>\n"
                "\t\t<username>{}</username>\n"
                "\t\t<stockSymbol>{}</stockSymbol>\n"
                "\t\t<funds>{}</funds>\n"
                "</userCommand>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['command'],
                data['username'],
                data['stockname'],
                data['funds']))

    elif data['types'] == "seven":
        #types:userCommand-dumplog1(7)
        return ("<userCommand>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<command>{}</command>\n"
                "\t\t<username>{}</username>\n"
                "\t\t<filename>{}</filename>\n"
                "</userCommand>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['command'],
                data['username'],
                data['filename']))

    elif data['types'] == "eight":
        #types:userCommand-dumplog2(8)
        return ("<userCommand>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<command>{}</command>\n"
                "\t\t<filename>{}</filename>\n"
                "</userCommand>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['command'],
                data['filename']))
    elif data['types'] == "nine":
        #types:quoteServer(9)
        return ("<quoteServer>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<quoteServerTime>{}</quoteServerTime>\n"
                "\t\t<username>{}</username>\n"
                "\t\t<stockSymbol>{}</stockSymbol>\n"
                "\t\t<price>{}</price>\n"
                "\t\t<cryptokey>{}</cryptokey>\n"
                "</quoteServer>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['quoteServerTime'],
                data['username'],
                data['stockname'],
                data['price'],
                data['cryptokey']))

    elif data['types'] == "ten":
        #types:systemEvent-database(10)-setBuyAmount(10)-setSellAmount(10)
        return ("<systemEvent>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<command>{}</command>\n"
                "\t\t<username>{}</username>\n"
                "\t\t<stockSymbol>{}</stockSymbol>\n"
                "\t\t<funds>{}</funds>\n"
                "</systemEvent>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['command'],
                data['username'],
                data['stockname'],
                data['funds']))

    elif data['types'] == "eleven":
        #types:accountTransaction-add(11)-remove(11)
        return ("<accountTransaction>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<action>{}</action>\n"
                "\t\t<username>{}</username>\n"
                "\t\t<funds>{}</funds>\n"
                "</accountTransaction>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['action'],
                data['username'],
                data['funds']))

    elif data['types'] == "twelve":
        #types:systemEvent-cancelSetBuy(12)-cancelSetSell(12)
        return ("<systemEvent>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<command>{}</command>\n"
                "\t\t<username>{}</username>\n"
                "\t\t<stockSymbol>{}</stockSymbol>\n"
                "</systemEvent>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['command'],
                data['username'],
                data['stockname']))

    elif data['types'] == "thirteen":
        #types:systemEvent-setBuyTrigger(13)-setSellTrigger(13)
        return ("<systemEvent>\n"
                "\t\t<timestamp>{}</timestamp>\n"
                "\t\t<server>{}</server>\n"
                "\t\t<transactionNum>{}</transactionNum>\n"
                "\t\t<command>{}</command>\n"
                "\t\t<username>{}</username>\n"
                "\t\t<stockSymbol>{}</stockSymbol>\n"
                "\t\t<funds>{}</funds>\n"
                "</systemEvent>\n"
                .format(data['timestamp'],
                data['server'],
                data['trans'],
                data['command'],
                data['username'],
                data['stockname'],
                data['funds']))
    else:
        tag = "errorEvent"

def getCurrTimestamp():
    dateTimeObj = datetime.now()
    #print(dateTimeObj)

    timestampStr = dateTimeObj.strptime(str(dateTimeObj), '%Y-%m-%d %H:%M:%S.%f').strftime('%s.%f')
    return str(int(float(timestampStr) * 1000))

if __name__=="__main__":
    logQueue = queue.Queue(maxsize = 100000)

    logServer = logServer(logQueue)
    logServer.start()

    main()
