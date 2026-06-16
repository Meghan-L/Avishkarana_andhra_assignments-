# Student Database Management using SQL and Python

## Project Overview

This project demonstrates the use of SQL concepts such as **GROUP BY, HAVING clauses, and JOIN operations** using a student database. Python is used to connect to the MySQL database and execute the SQL queries.

## Tools and Technologies

* Python
* MySQL
* MySQL Connector for Python
* VS Code

## Database Description

### Students Table

The `students` table stores student information.

Columns:

* StudentID
* StudentName
* Branch
* Semester
* Marks

### Courses Table

The `courses` table stores course details assigned to students.

Columns:

* CourseID
* StudentID
* CourseName

## SQL Concepts Implemented

### GROUP BY Operations

* Group students by Branch.
* Group students by Branch and Semester.

### HAVING Clause

* Display branches having more than one student.
* Display branches with average marks greater than 80.
* Display branches with total marks greater than 300.

### JOIN Operations

* INNER JOIN
* LEFT JOIN
* RIGHT JOIN
* FULL JOIN using UNION

## Python Implementation

Python connects to the MySQL database using `mysql.connector` and executes all SQL queries. The results are displayed in the console in a formatted manner.

## How to Run the Project

1. Execute the SQL script in MySQL to create the database and tables.

2. Insert the sample records.

3. Install MySQL Connector:

   pip install mysql-connector-python

4. Update the database credentials in the Python file if required.

5. Run the Python program.

## Output

The program displays:

* GROUP BY results
* HAVING clause results
* JOIN operation results
* Student and course-related information

## Conclusion

This project helps in understanding how SQL aggregation and JOIN operations work and how Python can be integrated with MySQL to retrieve and display database records efficiently.
