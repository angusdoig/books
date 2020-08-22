def add_countries():
  # Import MySQL Connector/Python library, and specific functions required
  import mysql.connector
  from mysql.connector import errorcode

  try:
      cnx = mysql.connector.connect(user='books', 
                                    password='towerofbabel', 
                                    host='Anguss-MacBook-Air.local', 
                                    database='books')
  except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
          print("Incorrect username or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
          print("Egads, the database is gone!")
      else:
          print(err)

  # Define the cursor
  cursor = cnx.cursor()

  country_tuples = []
  f = open("countries.txt", "r")
  for line in f:
    a = line.split("|")[0]
    b = line.split("|")[1]
    c = b.replace("\n", "")
    country_tuples.append((a,c))

  for (a,b) in country_tuples:
    insert_country = "INSERT INTO country (code, name) VALUES ('" + a + "', '" + b + "');"
    cursor.execute(insert_country)

  cnx.commit()
  cursor.close()
  cnx.close()

add_countries()