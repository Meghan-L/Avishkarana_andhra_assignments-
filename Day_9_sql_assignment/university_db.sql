CREATE DATABASE university_db;

USE university_db;

CREATE TABLE students (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(50),
    department VARCHAR(30),
    cgpa DECIMAL(3,2)
);

INSERT INTO students VALUES
(101,'Ananya','CSE',8.5),
(102,'Vikram','ECE',8.8),
(103,'Meghana','IT',9.0),
(104,'Karthik','AIML',7.8),
(105,'Nikhil','CSE',8.9);

SELECT * FROM students;