from socket import *
import threading
import mysql.connector
import sys
from datetime import datetime
from decimal import Decimal
import time
import Queue as queue
import json


def checkUserOwnStock(mycursor, username, stockname):
    try:
        check = "SELECT username FROM stocks WHERE username = %s and stockname = %s"
        mycursor.execute(check, (username, stockname,))
        result = mycursor.fetchall()[0][0]
        if result == username:
            return 1
        else:
            return 0
    except:
        return 0


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootpassword",
    database="dbone"
)
mycursor = mydb.cursor()


checkUserOwnStock(mycursor, 'CqOb5G0hB4', 'abc')
