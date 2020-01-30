import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootpassword",
    database="dbone"
)

mycursor = mydb.cursor()
mycursor.execute("DROP TABLE IF EXISTS acounts")
mycursor.execute("DROP TABLE IF EXISTS stocks")
mycursor.execute("DROP TABLE IF EXISTS logs")
mycursor.execute("DROP TABLE IF EXISTS bslogs")
mydb.commit()
