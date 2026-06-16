import mysql.connector

# Database Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Bharani@20",
    database="studentsdb"
)

cursor = conn.cursor()

queries = [

    (
        "Group By Branch",
        """
        SELECT Branch, COUNT(*) AS Student_Count
        FROM students
        GROUP BY Branch
        """
    ),

    (
        "Group By Branch and Semester",
        """
        SELECT Branch, Semester, COUNT(*) AS Student_Count
        FROM students
        GROUP BY Branch, Semester
        """
    ),

    (
        "Having Count",
        """
        SELECT Branch, COUNT(*) AS Student_Count
        FROM students
        GROUP BY Branch
        HAVING COUNT(*) > 1
        """
    ),

    (
        "Having Average Marks",
        """
        SELECT Branch, AVG(Marks) AS Avg_Marks
        FROM students
        GROUP BY Branch
        HAVING AVG(Marks) > 80
        """
    ),

    (
        "Having Total Marks",
        """
        SELECT Branch, SUM(Marks) AS Total_Marks
        FROM students
        GROUP BY Branch
        HAVING SUM(Marks) > 300
        """
    ),

    (
        "Inner Join",
        """
        SELECT students.StudentName, courses.CourseName
        FROM students
        INNER JOIN courses
        ON students.StudentID = courses.StudentID
        """
    ),

    (
        "Left Join",
        """
        SELECT students.StudentName, courses.CourseName
        FROM students
        LEFT JOIN courses
        ON students.StudentID = courses.StudentID
        """
    ),

    (
        "Right Join",
        """
        SELECT students.StudentName, courses.CourseName
        FROM students
        RIGHT JOIN courses
        ON students.StudentID = courses.StudentID
        """
    ),

    (
        "Full Join",
        """
        SELECT students.StudentName, courses.CourseName
        FROM students
        LEFT JOIN courses
        ON students.StudentID = courses.StudentID

        UNION

        SELECT students.StudentName, courses.CourseName
        FROM students
        RIGHT JOIN courses
        ON students.StudentID = courses.StudentID
        """
    )

]

for title, query in queries:

    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)

    cursor.execute(query)
    results = cursor.fetchall()

    if results:
        for row in results:
            print(row)
    else:
        print("No records found")

cursor.close()
conn.close()