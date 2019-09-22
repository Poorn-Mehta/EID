# https://stackoverflow.com/questions/454854/no-module-named-mysqldb
# https://www.jeremymorgan.com/tutorials/python-tutorials/how-to-connect-to-mysql-with-python/
# https://stackoverflow.com/questions/5687718/how-can-i-insert-data-into-a-mysql-database
# https://pimylifeup.com/raspberry-pi-mysql/
# https://pythonspot.com/mysql-with-python/

import MySQLdb

db = MySQLdb.connect("localhost","poorn","root","EID_Project1_DB")

cursor = db.cursor()

#cursor.execute("DROP TABLE IF EXISTS Test")

#sql = """CREATE TABLE Test (
#         Temperature FLOAT,  
#          Humiditiy FLOAT )"""

#cursor.execute(sql)

try:
    cursor.execute("""INSERT INTO Test VALUES (%s,%s)""",(26.25,35.17))
    db.commit()
except:
    db.rollback()
    
cursor.execute("""SELECT * FROM Test;""")
    
print (cursor.fetchall())

# To delete all data in the Table
cursor.execute("TRUNCATE TABLE Test")

cursor.execute("""SELECT * FROM Test;""")
    
print (cursor.fetchall())

db.close()