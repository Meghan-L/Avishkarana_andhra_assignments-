-- Create Database
CREATE DATABASE IF NOT EXISTS studentsdb;
USE studentsdb;

-- Drop tables if they already exist
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;

-- Create Students Table
CREATE TABLE students (
    StudentID INT PRIMARY KEY,
    StudentName VARCHAR(50),
    Branch VARCHAR(30),
    Semester INT,
    Marks INT
);

-- Insert ECE Student Data
INSERT INTO students VALUES
(401,'Aarav','ECE',2,86),
(402,'Saanvi','ECE',4,91),
(403,'Ishaan','ECE',3,78),
(404,'Diya','ECE',5,88),
(405,'Rudra','ECE',6,82),
(406,'Anika','ECE',4,95);

-- Create Courses Table
CREATE TABLE courses (
    CourseID INT PRIMARY KEY,
    StudentID INT,
    CourseName VARCHAR(50)
);

-- Insert Course Data
INSERT INTO courses VALUES
(501,401,'Digital Electronics'),
(502,402,'Signals and Systems'),
(503,403,'Microprocessors'),
(504,404,'Analog Communication'),
(505,407,'VLSI Design');

-- GROUP BY SINGLE COLUMN
SELECT Branch, COUNT(*) AS Student_Count
FROM students
GROUP BY Branch;

-- GROUP BY MULTIPLE COLUMNS
SELECT Branch, Semester, COUNT(*) AS Student_Count
FROM students
GROUP BY Branch, Semester;

-- HAVING WITH COUNT
SELECT Branch, COUNT(*) AS Student_Count
FROM students
GROUP BY Branch
HAVING COUNT(*) > 1;

-- HAVING WITH AVG
SELECT Branch, AVG(Marks) AS Avg_Marks
FROM students
GROUP BY Branch
HAVING AVG(Marks) > 80;

-- HAVING WITH SUM
SELECT Branch, SUM(Marks) AS Total_Marks
FROM students
GROUP BY Branch
HAVING SUM(Marks) > 300;

-- INNER JOIN
SELECT students.StudentName, courses.CourseName
FROM students
INNER JOIN courses
ON students.StudentID = courses.StudentID;

-- LEFT JOIN
SELECT students.StudentName, courses.CourseName
FROM students
LEFT JOIN courses
ON students.StudentID = courses.StudentID;

-- RIGHT JOIN
SELECT students.StudentName, courses.CourseName
FROM students
RIGHT JOIN courses
ON students.StudentID = courses.StudentID;

-- FULL JOIN (Using UNION)
SELECT students.StudentName, courses.CourseName
FROM students
LEFT JOIN courses
ON students.StudentID = courses.StudentID

UNION

SELECT students.StudentName, courses.CourseName
FROM students
RIGHT JOIN courses
ON students.StudentID = courses.StudentID;

-- Display Data
SELECT * FROM students;
SELECT * FROM courses;