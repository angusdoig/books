###############################################################################
###                 Import necessary modules and functions                  ###
###############################################################################

# Import MySQL Connector/Python library, and specific functions required
import mysql.connector

# Import datetime module for processing dates
from datetime import date

# Import sys for japes
import sys

# Import my country script for rebuilding the database upon a reset
import countries

###############################################################################
###  Connect to the database with the credentials below, initialise cursor  ###
###############################################################################

# Attempt database connection as specified below, throw errors if something goes wrong
try:
    
    cnx = mysql.connector.connect(user='bookprogram', 
                                  password='ltox1w-br4hye', 
                                  host='Anguss-MacBook-Air.local')

except mysql.connector.Error as err:

    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Incorrect username or password")

    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Egads, the database is gone!")

    else:
        print(err)

# Define the cursor
cursor = cnx.cursor()


# Check to see if the database exists - if it does, use it, if not, source it from the schema file
print("\nConnecting to database...")

cursor.execute("SHOW databases;")
databases = cursor.fetchall()

if ('books',) in databases:
    
    print("Database found")
    cursor.execute("USE books;")

else:
    
    print("Database not found")
    rebuild = input("Enter any key to rebuild database from schema file")
    countries.add_countries()
    cursor.execute("SOURCE /Users/angus/Documents/book_database/book_schema.sql")

###############################################################################
### Functions that interact with the MySQL database to insert or query data ###
###############################################################################

# Select a result from the given table where the data column matches the datum
def SELECT(result_column, table, data_column, datum):
    
    select = "SELECT %s FROM %s WHERE %s = %s;" % (result_column, table, data_column, datum)
    cursor.execute(select)
    result = cursor.fetchall()
    
    if result != []:
            return result
    
    else: 
        return False

# Insert into the given table at the given column the given data
def INSERT(table, columns, data):
    
    insert = "INSERT INTO %s (%s) VALUES (%s);" % (table, columns, data)
    cursor.execute(insert)

# Update the given columns to the given data in the given table
def UPDATE(table, columns_list, values_list):
    
    update = "UPDATE %s SET " % (table)
    
    for (column, value) in zip(columns_list[1:-1], values_list[1:-1]):
        update += (column + " = " + value + ", ")
    
    update += (columns_list[-1] + " = " + values_list[-1])
    update += " WHERE %s = %s;" % (columns_list[0], values_list[0])
    cursor.execute(update)

# Check a table to see if a given datum has an entry
def check_for_entry_insert(datum, column, table, insert):
    
    datum = format_given_data([datum])[0]
    check_list_bool = SELECT(column, table, column, datum)
    
    if check_list_bool:
        check = check_list_bool[0][0]
    
    if not check_list_bool and not insert:
        return False
    
    elif not check_list_bool and insert:
        INSERT(table, column, datum)
    
    else:
        return True

# Format the given data for entry into the given columns in the given table, then insert them
def insert_given_data(data, columns, table):

    formatted_values_list = format_given_data(data)

    # Now we have a list containing all the values, formatted correctly, so we need to make the string that will be used in the insertion
    formatted_values_string = ""
    formatted_values_string += formatted_values_list[0]

    for datum in formatted_values_list[1:]:
        formatted_values_string += (", " + datum)
    
    columns_string = ""
    columns_string += str(columns[0])
    
    for column in columns[1:]:
        columns_string += (", " + str(column))
    
    INSERT(table, columns_string, formatted_values_string)

###############################################################################
###                   Functions that deal with user input                   ###
###############################################################################

# Don't be like Bobby's school, sanitise your data inputs!
def sanitise(user_input):
    
    user_input = user_input.replace("'", "\'").replace("\\", "\\\\")
    SQL_injections = ["; DROP", "; SELECT", "; CREATE", "; INSERT"]
    
    for injection in SQL_injections:
        
        if injection in user_input:
            print("Take your SQL injection somewhere else, foul cur!")
            sys.exit()
    
    return user_input

# Format the given data for use in SQL statements, return as a list of formatted data
def format_given_data(data):
    formatted_values_list = []

    for datum in data:

        # Try converting the datum into a date, if it works format it appropriately and add it to the values list
        try:
            year, month, day = map(int, datum.split('-'))
            date_from_datum = str(date(year, month, day))
            formatted_date = "'" + date_from_datum + "'"
            formatted_values_list.append(formatted_date)
        
        except (ValueError, AttributeError):
            
            # Next, try converting the datum into a number, if it works add it to the values list
            try:
                formatted_int = str(int(datum))
                formatted_values_list.append(formatted_int)
            
            except (ValueError, AttributeError):
                # Lastly, the data must already be a string (something's very wrong if not), so format it and add it to the values list
                if datum[0] == "'" and datum[-1] == "'":
                    formatted_values_list.append(datum)
                else:
                    formatted_string = "'" + datum + "'"
                    formatted_values_list.append(formatted_string)
    
    return formatted_values_list

# Ask user for input with a given prompt, force it to be y/n
def get_input_y_n(prompt):
    
    while True:
        user_input = input(prompt)
        
        if user_input == "y":
            return True
            break
        
        elif user_input == "n":
            return False
            break
        
        else:
            print("Please enter y or n to continue")

# Get the user's input according to the provided restrictions
def get_user_input(prompt, desired_format, required):
    
    while True:
        
        user_input = sanitise(input(prompt))
        
        if required and not user_input:
            print("Required field, please try again")
        
        elif not required and not user_input:
            return False
            break
        
        if user_input:
            # If the desired format is a date, check if the input is a date, reject if not
            if desired_format == "date":
                
                try:
                    year, month, day = map(int, user_input.split('-'))
                    str(date(year, month, day))
                    return user_input
                    break
                
                except (ValueError, AttributeError):
                    print("The date you have entered appears to be invalid, please try again")
            
            # If the desired format is a number, check if the input is a number, rejecy if not
            elif desired_format == "number":
                try:
                    int(user_input)
                    return user_input
                    break
                except (ValueError, AttributeError):
                    print("You must enter a number, please try again")
            # If the desired format is neither a date nor a number, it must be a string, which we have, so return the input
            else:
                return user_input

# Get the user's input, query the given table and find the id needed
def get_id_from_user_input(prompt, foreign_column, table, foreign_key, required):
    
    while True:
        
        user_input = sanitise(input(prompt))
        
        if required and not user_input:
            print("Required field, please try again")
        
        elif not required and not user_input:
            return False
            break

        elif user_input:
            user_input = format_given_data([user_input])[0]
            exists_check = check_for_entry_insert(user_input, foreign_column, table, True)
            if exists_check:
                id_from_input = SELECT(foreign_key, table, foreign_column, user_input)[0][0]
                return id_from_input
            else:
                return False
        


# Ask the user for a valid country code, return the country_id
def get_country_id(prompt):
    
    while True:
        country_code = sanitise(input(prompt))
        
        if country_code:
            if country_code == "?":
                with open("countries.txt", "r") as f:
                    for line in f:
                        print(line.replace("\n", ""))
            else:
                country_code = format_given_data([country_code])[0]
                result = SELECT("country_id", "country", "code", country_code)[0][0]
                
                if result:
                    return result
                    break
                
                else:
                    print("There is no country matching that code, please try again")
        
        else:
            return False
            break

# Ask for ISBN, if given repeat until valid ISBN given, if 10-digit ISBN given convert to 13-digit ISBN behind the scenes
def get_ISBN():
    
    while True:
        
        user_input = input("Enter the book's 10 or 13-digit ISBN: ").replace("-", "")
        
        if user_input:
            
            if len(user_input) != 10 and len(user_input) != 13:
                print("ISBN must be 10 or 13 digits")
            # Check a 13-digit ISBN for validity
            elif len(user_input) == 13:
                try:
                    int(user_input)
                    ISBN_list = list(map(int,str(user_input)))
                    zipped_ISBN = zip(ISBN_list, [1,3,1,3,1,3,1,3,1,3,1,3,1])
                    multiplied_zip = []
                    
                    for (a,b) in zipped_ISBN:
                        multiplied_zip.append(a*b)
                        result = sum(multiplied_zip)
                    
                    if result % 10 != 0:
                        print("The ISBN you have entered is invalid, please try again")
                    
                    else:
                        return user_input
                        break
                
                except ValueError:
                    print("For a 13-digit ISBN, only numbers and dashes may be entered. Please try again")
            # Check if a 10-digit ISBN is valid, convert to 13-digit ISBN if so
            else:
                
                if user_input[-1] == "X":
                    
                    try:
                        int(user_input[:-1])
                        ISBN_list = list(map(int,str(user_input[:-1])))
                        ISBN_list_ten = ISBN_list.append(10)
                        zipped_ISBN = zip(ISBN_list_ten, [10,9,8,7,6,5,4,3,2,1])
                        multiplied_zip = []
                       
                        for (a,b) in zipped_ISBN:
                            multiplied_zip.append(a*b)
                            result = sum(multiplied_zip)
                       
                        if result % 11 != 0:
                            print("The ISBN you have entered is invalid, pleae try again")
                       
                        else:
                            ISBN_convert_list = [9,7,8] + ISBN_list
                           
                            for i in range(10):
                                ISBN_list_try = ISBN_convert_list.append(i)
                                zipped_ISBN = zip(ISBN_list_try, [1,3,1,3,1,3,1,3,1,3,1,3,1])
                                multiplied_zip = []
                              
                                for (a,b) in zipped_ISBN:
                                    multiplied_zip.append(a*b)
                                    result = sum(multiplied_zip)
                              
                                if result % 10 == 0:
                                    return ("978" + user_input[:-1] + str(i))
                                    break
                    
                    except ValueError:
                        print("Only enter numbers and dashes, except for the last character, which may be an 'X'")
                
                else:
                    
                    try:
                        int(user_input)
                        ISBN_list = list(map(int,str(user_input)))
                        zipped_ISBN = zip(ISBN_list, [10,9,8,7,6,5,4,3,2,1])
                        multiplied_zip = []
                       
                        for (a,b) in zipped_ISBN:
                            multiplied_zip.append(a*b)
                            result = sum(multiplied_zip)
                       
                        if result % 11 != 0:
                            print("The ISBN you have entered is invalid, pleae try again")
                       
                        else:
                            ISBN_convert_list = [9,7,8] + ISBN_list[:-1]
                           
                            for i in range(10):
                                ISBN_list_try = ISBN_convert_list + [i]
                                zipped_ISBN = zip(ISBN_list_try, [1,3,1,3,1,3,1,3,1,3,1,3,1])
                                multiplied_zip = []
                              
                                for (a,b) in zipped_ISBN:
                                    multiplied_zip.append(a*b)
                                    result = sum(multiplied_zip)
                              
                                if result % 10 == 0:
                                    return ("978" + user_input[:-1] + str(i))
                                    break
                    
                    except ValueError:
                        print("Only enter numbers and dashes, except for the last character, which may be an 'X'")
        else:
           
            return False
            break

###############################################################################
###        Getting data from the user and adding it to the database         ###
###############################################################################

# Get book data from user, add to database
def add_book_data():

    print("\nInput the book's data here; to skip an optional field, press enter")

    # Create empty lists to populate and then pass to the insert_given_data() function
    received_data = []
    received_columns = []
    
    # Get book data from the user
    book_title = get_user_input(" (*) Enter the book's title: ", "string", True)
    received_data.append(book_title)
    received_columns.append("title")

    author_id = get_id_from_user_input(" (*) Enter the author's name: ", "name", "author", "author_id", True)
    received_data.append(author_id)
    received_columns.append("author_id")

    series_id = get_id_from_user_input("     Enter the series' name: ", "name", "series", "series_id", False)
    if series_id:
        received_data.append(series_id)
        received_columns.append("series_id")

        series_location = get_user_input(" (*) Enter the book's position in the series: ", "number", True)
        received_data.append(series_location)
        received_columns.append("series_location")

    # Ask if the user wants to add more data about the book
    extended_data = get_input_y_n("Add more data (e.g. release date, ISBN, etc)? (y/n): ")
    if extended_data:

        publisher_id = get_id_from_user_input("     Enter the publisher's name: " , "name", "publisher", "publisher_id", False)
        if publisher_id:
            received_data.append(publisher_id)
            received_columns.append("publisher_id")

        release_date = get_user_input("     Enter the book's release date (formatted like '2000-11-06'): ", "date", False)
        if release_date:
            received_data.append(release_date)
            received_columns.append("release_date")

        page_count = get_user_input("     Enter the book's page count: ", "number", False)
        if page_count:
            received_data.append(page_count)
            received_columns.append("page_count")

        ISBN = get_ISBN()
        if ISBN:
            received_data.append(ISBN)
            received_columns.append("ISBN")

    # Check if the book already has an entry in the database and update that if so, otherwise insert the book
    book_exists = check_for_entry_insert(book_title, "title", "books", False)
    
    if book_exists:
        print("Book exists, updating")
        UPDATE("books", received_columns, format_given_data(received_data))
    
    else:
        print("New book, adding")
        insert_given_data(received_data, received_columns, "books")
    
    user_repeat = get_input_y_n("\nWould you like to add another book? (y/n): ")
    
    if user_repeat:
        add_book_data()
    
    else:
        root()

# Function for adding author data
def add_author_data():
    received_data = []
    received_columns = []

    author_name = get_user_input(" (*) Enter the author's name: ", "string", True)
    received_data.append(author_name)
    received_columns.append("name")

    author_dob = get_user_input("     Enter the author's date of birth (formatted like '2000-11-06'): ", "date", False)
    if author_dob:
        received_data.append(author_dob)
        received_columns.append("date_of_birth")

    country_id = get_country_id("     Enter the two-letter code for the author's home country (e.g. GB for United Kingdom, FR for France, etc, or ? for help): ")
    if country_id:
        received_data.append(country_id)
        received_columns.append("country_id")

    wikipedia_url = get_user_input("     Enter the author's wikipedia URL: ", "string", False)
    if wikipedia_url:
        received_data.append(wikipedia_url)
        received_columns.append("wikipedia_url")

    # Determine whether the author's entry already exists, 
    author_exists = check_for_entry_insert(author_name, "name", "author", False)
    
    if author_exists:
        UPDATE("author", received_columns, format_given_data(received_data))
    
    else:
        insert_given_data(received_data, received_columns, "author")

    user_repeat = get_input_y_n("\nWould you like to add another author? (y/n): ")
    
    if user_repeat:
        add_author_data()
    
    else:
        root()

# Function for adding publisher data
def add_publisher_data():
    received_data = []
    received_columns = []

    publisher_name = get_user_input(" (*) Enter the publisher's name: ", "string", True)
    received_data.append(publisher_name)
    received_columns.append("name")

    founding_date = get_user_input("     Enter the year the publisher was founded in: ", "number", False)
    if founding_date:
        received_data.append(founding_date)
        received_columns.append("founding_date")

    country_id = get_country_id("     Enter the two-letter code for the country the publisher is based in (e.g. GB for United Kingdom, FR for France, etc, or ? for help): ")
    if country_id:
        received_data.append(country_id)
        received_columns.append("country_id")

    publisher_exists = check_for_entry_insert(publisher_name, "name", "publisher", False)
    
    if publisher_exists:
        UPDATE("publisher", received_columns, format_given_data(received_data))
    
    else:
        insert_given_data(received_data, received_columns, "publisher")

    user_repeat = get_input_y_n("\nWould you like to add another publisher? (y/n): ")
    
    if user_repeat:
        add_publisher_data()
    
    else:
        root()

###############################################################################
###   Querying the database for all the books that satisfy some condition   ###
###############################################################################

# Function for querying the database
def query_data():
    while True:
        user_input = sanitise(input("Find all the books by a given author (a), in a given series (s), or from a given publisher (p)? \n   > "))
        if user_input:
            # Find all the books by a given author
            if user_input in ["author", "a"]:
                author_id = get_id_from_user_input(" (*) Enter the author's name: ", "name", "author", "author_id", True)
                if author_id:    
                    author_name = SELECT("name", "author", "author_id", author_id)[0][0]
                    books_list = SELECT("title", "books", "author_id", (str(author_id) + " ORDER BY series_location"))
                    if books_list:
                        print("%s has the following book(s) in the database: " % (author_name))
                        for i in books_list:
                            for (a) in i:
                                print(" *  " + str(a))
                        break
                    else:
                        print("%s has no books in the database" % (author_name))
                        break
                else:
                    print("No author by that name in the database, please try again\n")
                    break
            # Find all the books in a given series
            elif user_input in ["series", "s"]:
                series_id = get_id_from_user_input(" (*) Enter the series' name: ", "name", "series", "series_id", True)
                if series_id:  
                    series_name = SELECT("name", "series", "series_id", series_id)[0][0]  
                    books_list = SELECT("title", "books", "series_id", (str(series_id) + " ORDER BY series_location"))
                    print("The following book(s) in the database are in the series: %s: " % (series_name))
                    for i in books_list:
                        for (a) in i:
                            print(" *  " + str(a))
                    break
                else:
                    print("No series by that name in the database, please try again")
                    break
            # Find all the books published by a given publisher
            elif user_input in ["publisher", "p"]:
                publisher_id = get_id_from_user_input(" (*) Enter the publisher's name: ", "name", "publisher", "publisher_id", True)
                if publisher_id:
                    publisher_name = SELECT("name", "publisher", "publisher_id", publisher_id)[0][0]
                    books_list = SELECT("title", "books", "publisher_id", (str(publisher_id) + " ORDER BY series_location"))
                    if books_list:
                        print("The following book(s) in the database are listed as published by %s:" % (publisher_name))
                        for i in books_list:
                            for (a) in i:
                                print(" *  " + str(a))
                        break
                    else:
                        print("There are no books in the database published by %s" % (publisher_name))
                        break
                else:
                    print("There is no publisher by that name in the database")
                    break
    user_repeat = get_input_y_n("Would you like to query the database again? (y/n): ")
    
    if user_repeat:
        query_data()
    
    else:
        root()

###############################################################################
###                  Root function and opening statements                   ###
###############################################################################

# Print welcome statement
print("\nWelcome to Angus' Book Database Program, v0.4.1")
print("\nUses MySQL Server v8.0.21, Python v3.8.5, and MySQL Connector/Python")

# Determine which of the main paths to take
def root():
    root_choice = input("\nWould you like to add to the database (a), make a query (q), or exit (e)? \n   > ")
    
    if root_choice in ["add", "a"]:
        
        add_choice = input("Would you like to add information on a book (b), author (a), or publisher (p)?\n   > ")
        
        if add_choice in ["book", "b"]:
            add_book_data()
        
        elif add_choice in ["author", "a"]:
            add_author_data()
        
        elif add_choice in ["publisher", "p"]:
            add_publisher_data()
        
        else:
            root()
    
    elif root_choice in ["query", "q"]:
        query_data()
    
    elif root_choice in ["exit", "e"]:
        pass
    
    else:
        print("Enter 'add' or 'a' to add data, 'query' or 'q' to query the database, 'exit' or 'e' to exit the program")
        root()

# Run the root function
root()

###############################################################################
###        End the transaction and close database connection safely         ###
###############################################################################

# Commit changes to database
commit = get_input_y_n("ONLY FOR TESTING: Commit changes? \n > ")

if commit:
    cnx.commit()

# Close down the database connection before ending the program
print("Bye")

cursor.close()

cnx.close()