




import mysql.connector

# Connect to the database
connection = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="System_security"
)




# Create a cursor
cursor2 = connection.cursor()
# Execute a query to get all the users from the database
cursor2.execute("SELECT * FROM users")


# Get the results
users = cursor2.fetchall()
# Close the cursor and the connection

cursor2.execute("SHOW COLUMNS FROM users")
columns_names_all = cursor2.fetchall()

#cursor.close()
#connection.close()

# Create a list of the users
users_names = []
for user in users:
  users_names.append(user[1])
  

# Print the column names, skipping the first column,last column 
column_names=[]
for column_name in columns_names_all[1:-1]:
    column_names.append(column_name[0])





'''
            <label for="input_text">Input Text:</label>
            <textarea name="input_text" id="input_text" rows="6" placeholder="Enter text" ></textarea>
            <input type="text" name="key" id="key" placeholder="Enter Key">
            <input type="submit" value="Process">'''