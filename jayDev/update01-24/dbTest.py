import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootpassword",
    database="testdb"
)

mycursor = mydb.cursor()


# create a database named testdb
# mycursor.execute("CREATE DATABASE testdb")
# mycursor.execute("SHOW DATABASES")
# for db in mycursor:
#     print(db)


# create a table named students and caontains two elements
# mycursor.execute("CREATE TABLE students (name VARCHAR(255), age INTEGER(10))")
# mycursor.execute("SHOW TABLES")
# for db in mycursor:
#     print(db)


# insert data into the database
# sqlFormula = "INSERT INTO students (name, age) VALUES (%s, %s)"
# student1 = {("Rachel", 22)}
# students = [("Rachel", 22),("Amanda", 32),("Jacob", 21),("Avi", 28),("Michelle", 17)]
#
# mycursor.execute(sqlFormula, student1)
# mycursor.executemany(sqlFormula, students)
#
# mydb.commit()


# select data from the table
# mycursor.execute("SELECT age FROM students")
#
# # myresult = mycursor.fetchall()
# myresult = mycursor.fetchone()
#
# for row in myresult:
#     print(row)


# # use where to find right data and how to wildcards
# # sql = "SELECT * FROM students WHERE age = 17"
# # sql = "SELECT * FROM students WHERE name = 'Jacob'"
# # sql = "SELECT * FROM students WHERE name LIKE 'Mi%'"
# # sql = "SELECT * FROM students WHERE name LIKE '%ac%'"
# sql = "SELECT * FROM students WHERE name = %s"
#
# # mycursor.execute(sql)
# mycursor.execute(sql, ("Jacob",))
#
# myresult = mycursor.fetchall()
#
# for result in myresult:
#     print(result)


# # update the data from database and use limit to get first 5 data
# # sql = "UPDATE students SET age = 13 WHERE name = 'Avi'"
#
# # mycursor.execute(sql)
# #
# # mydb.commit()
#
# # mycursor.execute("SELECT * FROM students LIMIT 5")
# mycursor.execute("SELECT * FROM students LIMIT 5 OFFSET 2")
#
# myresult = mycursor.fetchall()
#
# for result in myresult:
#     print(result)


# # use order by asc or desc
# # sql = "SELECT * FROM students ORDER BY age"
# sql = "SELECT * FROM students ORDER BY age DESC"
#
# mycursor.execute(sql)
#
# myresult = mycursor.fetchall()
#
# for r in myresult:
#     print(r)


# # delete elements and drop table
# # sql = "DELETE FROM students WHERE name = 'Rachel'"
# sql = "DROP TABLE IF EXISTS students"
#
# mycursor.execute(sql)
#
# mydb.commit()
