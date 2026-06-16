# Day 9 SQL Assignment

## Introduction

Databases are used to store, organize, and manage data efficiently. MySQL is one of the most widely used relational database management systems (RDBMS). Python provides libraries that allow developers to connect to MySQL databases and perform various database operations.

In this assignment, a MySQL database was created to store student information. Python was then used to establish a connection with the database, retrieve the stored records, and display them using the Pandas library.

## Objective

The main objective of this assignment is to understand how Python can interact with MySQL databases and how data can be retrieved and represented in a structured format using Pandas.

## Concepts Covered

### MySQL Database
MySQL is an open-source relational database management system used to store and manage structured data using SQL (Structured Query Language).

### SQL Operations
The following SQL operations were performed in this assignment:
- Creating a database.
- Creating a table.
- Inserting records into the table.
- Retrieving records using the `SELECT` statement.

### Python–MySQL Connectivity
Python connects to MySQL using the `mysql-connector-python` library. This library enables Python programs to communicate with the MySQL server and execute SQL queries.

### Pandas DataFrame
Pandas is a powerful Python library used for data manipulation and analysis. The retrieved database records were converted into a DataFrame for better readability and structured presentation.

## Procedure

1. A database named `university_db` was created.
2. A table named `students` was created to store student details.
3. Sample student records were inserted into the table.
4. Python was connected to the MySQL database using the MySQL connector.
5. An SQL query was executed to retrieve all records from the table.
6. The retrieved data was displayed using a Pandas DataFrame.

## Outcome

This assignment helped in understanding the integration of MySQL with Python. It demonstrated how database records can be accessed, processed, and displayed efficiently using Python libraries.

## Conclusion

The assignment provided practical knowledge of database connectivity and data retrieval techniques. It strengthened the understanding of SQL fundamentals, Python database operations, and the use of Pandas for presenting data in an organized manner.