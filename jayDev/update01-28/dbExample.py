import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootpassword",
    database="testdb"
)

mycursor = mydb.cursor()


# mycursor.execute("CREATE TABLE acounts (username VARCHAR(255) PRIMARY KEY, funds DECIMAL(10,2))")
# mycursor.execute("CREATE TABLE stocks (username VARCHAR(255), stockname VARCHAR(255), stockprice DECIMAL(10,2), amount DECIMAL(10,2))")
# mycursor.execute("SHOW TABLES")
# for db in mycursor:
#     print(db)

# addFormula = "INSERT INTO acounts (username, funds) VALUES (%s, %s)"
# user1 = ('jay', 100.00)
# mycursor.execute(addFormula, user1)
# mydb.commit()

# buyFormula = "INSERT INTO stocks (username, stockname, amount) VALUES (%s, %s, %s)"
# users = [('jay', 'abc', 200.00), ('jay', 'efg', 500.50), ('jay', 'xyz', 750.45)]
# mycursor.executemany(buyFormula, users)
# mydb.commit()

# checkAcountFunds = "SELECT funds FROM acounts WHERE username = %s"
# name = 'jay'
# mycursor.execute(checkAcountFunds, (name,))
# result = (mycursor.fetchall()[0][0])
# print(result)

# checkStockAmount = "SELECT amount FROM stocks WHERE username = %s and stockname = %s "
# username = 'jay'
# stockname = 'abc'
# mycursor.execute(checkStockAmount, (username, stockname,))
# result = mycursor.fetchall()[0][0]
# print(result)

# removeFormula = "UPDATE acounts SET funds = %s WHERE username = %s"
# username = 'jay'
# funds = 200.55
# mycursor.execute(removeFormula, (funds, username,))
# mydb.commit()
