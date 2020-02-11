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
mycursor.execute("DROP TABLE IF EXISTS triggers")
mydb.commit()

mycursor.execute("CREATE TABLE acounts (username VARCHAR(255) PRIMARY KEY, funds DECIMAL(10,2))")
mycursor.execute("CREATE TABLE stocks (username VARCHAR(255), stockname VARCHAR(255), amount DECIMAL(10,2))")
mycursor.execute("CREATE TABLE logs (username VARCHAR(255), transnumber INTEGER(10), command VARCHAR(255), stockname VARCHAR(255), stockprice DECIMAL(10,2), amount DECIMAL(10,2), funds DECIMAL(10,2), times BIGINT(15), cryptokey VARCHAR(255))")
mycursor.execute("CREATE TABLE bslogs (username VARCHAR(255), transnumber INTEGER(10), command VARCHAR(255), stockname VARCHAR(255), stockprice DECIMAL(10,2), amount DECIMAL(10,2), times BIGINT(15), cryptokey VARCHAR(255))")
mycursor.execute("CREATE TABLE triggers (username VARCHAR(255), stockname VARCHAR(255), command VARCHAR(255), stockprice DECIMAL(10,2), times BIGINT(15))")
mycursor.execute("SHOW TABLES")
for db in mycursor:
    print(db)
