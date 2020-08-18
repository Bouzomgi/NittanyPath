import pandas as pd
import sqlite3 as sql

connection = sql.connect("projectDatabase.db")

studentTA_Table = pd.read_csv("Students_TA.csv")
professors_Table = pd.read_csv("Professors.csv")
forum_table = pd.read_csv("Posts_Comments.csv")

def convert(newTable, oldTable, connection):
	connection.execute(f'INSERT OR REPLACE INTO {newTable} SELECT * FROM {oldTable};')
	connection.execute(f'DROP TABLE {oldTable};')
	connection.commit()


#Students
connection.execute('CREATE TABLE IF NOT EXISTS Students(email TEXT PRIMARY KEY, password TEXT, name TEXT, age INT, gender TEXT, major TEXT, \
 	street TEXT, zipcode INT, phone INT);')

content = studentTA_Table[["Email", "Password", "Full Name", "Age", "Gender", "Major", "Street", "Zip", "Phone"]]
content = content.rename(columns={"Email": "email", "Password": "password", "Full Name": "name", "Age": "age", "Gender": "gender", \
	"Major": "major", "Street": "street", "Zip": "zipcode", "Phone": "phone"})
content.to_sql("StudentsTool", con=connection, if_exists='replace', index=False)
convert("Students", "StudentsTool", connection)



#Zipcodes
connection.execute('CREATE TABLE IF NOT EXISTS Zipcodes(zipcode INT PRIMARY KEY, city TEXT, state TEXT);')

content = studentTA_Table[["Zip", "City", "State"]]
content = content.rename(columns={"Zip": "zipcode", "City": "city", "State": "state"})

content.to_sql("ZipcodesTool", con=connection, if_exists='replace', index=False)
convert("Zipcodes", "ZipcodesTool", connection)



#Professors
connection.execute('CREATE TABLE IF NOT EXISTS Professors(email TEXT PRIMARY KEY, password TEXT, name TEXT, age INT, gender TEXT, \
	office_address TEXT, department TEXT, title TEXT);')

content = professors_Table[["Email", "Password", "Name", "Age", "Gender", "Office", "Department Name", "Title"]]
content = content.rename(columns={"Email": "email", "Password": "password", "Name": "name", "Age": "age", "Gender": "gender", \
	"Office": "office_address", "Department Name": "department", "Title": "title"})
content.to_sql("ProfessorsTool", con=connection, if_exists='replace', index=False)
convert("Professors", "ProfessorsTool", connection)



#Departments
connection.execute('CREATE TABLE IF NOT EXISTS Departments(dept_id TEXT PRIMARY KEY, dept_name TEXT, dept_head TEXT);')

content = professors_Table[["Department", "Department Name", "Email", "Title"]]
content = content.rename(columns={"Department": "dept_id", "Department Name": "dept_name", "Email" : "dept_head", "Title": "title"})

content.to_sql("DepartmentsTool", con=connection, if_exists='replace', index=False)

connection.execute('DELETE FROM DepartmentsTool WHERE title <> "Head";')
connection.execute(f'INSERT OR REPLACE INTO Departments SELECT dept_id, dept_name, dept_head FROM DepartmentsTool;')
connection.execute(f'DROP TABLE DepartmentsTool;')
connection.commit()



#Courses
connection.execute('CREATE TABLE IF NOT EXISTS Courses(course_id TEXT PRIMARY KEY, course_name TEXT, course_description TEXT, \
	late_drop_deadline TEXT);')

content = forum_table[["Courses", "Drop Deadline"]]
content = content.rename(columns={"Courses": "course_id", "Drop Deadline" : "late_drop_deadline"})
content.to_sql(f"CoursesTool", con=connection, if_exists='replace', index=False)

for i in range(1, 4):
	content = studentTA_Table[[f"Courses {i}", f"Course {i} Name", f"Course {i} Details"]]
	content = content.rename(columns={f"Courses {i}": "course_id", f"Course {i} Name": "course_name", f"Course {i} Details": "course_description"})
	content.to_sql(f"Courses{i}", con=connection, if_exists='replace', index=False)
	connection.execute(f'INSERT OR REPLACE INTO Courses SELECT \
		Courses{i}.course_id, Courses{i}.course_name, Courses{i}.course_description, CoursesTool.late_drop_deadline FROM Courses{i} \
		LEFT JOIN CoursesTool ON Courses{i}.course_id=CoursesTool.course_id;')
	connection.execute(f'DROP TABLE Courses{i};')
	connection.commit()

connection.execute(f'INSERT OR REPLACE INTO Courses (course_id, late_drop_deadline) SELECT course_id, late_drop_deadline FROM CoursesTool \
	WHERE course_id NOT IN (SELECT course_id FROM Courses);')

connection.execute(f'DROP TABLE CoursesTool;')
connection.commit()



#Sections
connection.execute('CREATE TABLE IF NOT EXISTS Sections(course_id TEXT, sec_no INT, limit_ INT, teaching_team_id INT, \
	PRIMARY KEY (course_id, sec_no));')

content = professors_Table[["Teaching", "Teaching Team ID"]]
content = content.rename(columns={"Teaching": "course_id", "Teaching Team ID" : "teaching_team_id"})
content.to_sql(f"SectionsTool", con=connection, if_exists='replace', index=False)

for i in range(1, 4):
	content = studentTA_Table[[f"Courses {i}", f"Course {i} Section", f"Course {i} Section Limit"]]
	content = content.rename(columns={f"Courses {i}": "course_id", f"Course {i} Section": "sec_no", \
		f"Course {i} Section Limit": "limit_"})
	content.to_sql(f"Sections{i}", con=connection, if_exists='replace', index=False)

	connection.execute(f'INSERT OR REPLACE INTO Sections SELECT \
		Sections{i}.course_id, Sections{i}.sec_no, Sections{i}.limit_, SectionsTool.teaching_team_id FROM Sections{i}\
		INNER JOIN SectionsTool ON Sections{i}.course_id=SectionsTool.course_id;')
	connection.execute(f'DROP TABLE Sections{i};')
	connection.commit()

connection.execute(f'DROP TABLE SectionsTool;')
connection.commit()




#Enrolls
connection.execute('CREATE TABLE IF NOT EXISTS Enrolls(student_email TEXT, course_id TEXT, sec_no INT, \
	PRIMARY KEY (student_email, course_id));')

for i in range(1, 4):
	content = studentTA_Table[["Email", f"Courses {i}", f"Course {i} Section"]]
	content = content.rename(columns={"Email" : "email", f"Courses {i}": "course_id", f"Course {i} Section": "sec_no"})
	content.to_sql(f"Enrolls{i}", con=connection, if_exists='replace', index=False)
	convert("Enrolls", f"Enrolls{i}", connection)



#Prof_teaching_teams
connection.execute('CREATE TABLE IF NOT EXISTS Prof_teaching_teams(prof_email TEXT PRIMARY KEY, teaching_team_id INT);')

content = professors_Table[["Email", "Teaching Team ID"]]
content = content.rename(columns={"Email": "email", "Teaching Team ID" : "teaching_team_id"})
content.to_sql(f"Prof_teaching_teamsTool", con=connection, if_exists='replace', index=False)
convert("Prof_teaching_teams", "Prof_teaching_teamsTool", connection)



#TA_teaching_teams
connection.execute('CREATE TABLE IF NOT EXISTS TA_teaching_teams(student_email TEXT PRIMARY KEY, teaching_team_id INT);')

content = studentTA_Table[["Email", "Teaching Team ID"]]
content = content.rename(columns={"Email": "email", "Teaching Team ID" : "teaching_team_id"})
content.to_sql(f"TA_teaching_teamsTool", con=connection, if_exists='replace', index=False)
connection.execute('DELETE FROM TA_teaching_teamsTool WHERE teaching_team_id IS NULL;')
convert("TA_teaching_teams", "TA_teaching_teamsTool", connection)



#Homeworks
connection.execute('CREATE TABLE IF NOT EXISTS Homeworks(course_id TEXT, sec_no INT, hw_no INT, hw_details TEXT, \
	PRIMARY KEY (course_id, sec_no, hw_no));')

for i in range(1, 4):
	content = studentTA_Table[[f"Courses {i}", f"Course {i} Section", f"Course {i} HW_No", f"Course {i} HW_Details"]]
	content = content.rename(columns={f"Courses {i}": "course_id", f"Course {i} Section": "sec_no", \
		f"Course {i} HW_No": "hw_no", f"Course {i} HW_Details": "hw_details"})
	content.to_sql(f"Homeworks{i}", con=connection, if_exists='replace', index=False)
	convert("Homeworks", f"Homeworks{i}", connection)



#Homework_grades
connection.execute('CREATE TABLE IF NOT EXISTS Homework_grades(student_email TEXT, course_id TEXT, sec_no INT, hw_no INT, grade TEXT, \
	PRIMARY KEY (student_email, course_id, sec_no, hw_no));')

for i in range(1, 4):
	content = studentTA_Table[["Email", f"Courses {i}", f"Course {i} Section", f"Course {i} HW_No", f"Course {i} HW_Grade"]]
	content = content.rename(columns={"Email" : "email", f"Course {i}": "course_id", f"Course {i} Section": "sec_no", \
		f"Course {i} HW_No": "hw_no", f"Course {i} HW_Grade" : "grade"})
	content.to_sql(f"Homework_grades{i}", con=connection, if_exists='replace', index=False)
	convert("Homework_grades", f"Homework_grades{i}", connection)



#Exams
connection.execute('CREATE TABLE IF NOT EXISTS Exams(course_id TEXT, sec_no INT, exam_no INT, exam_details TEXT, \
	PRIMARY KEY (course_id, sec_no, exam_no));')

for i in range(1, 4):
	content = studentTA_Table[[f"Courses {i}", f"Course {i} Section", f"Course {i} EXAM_No", f"Course {i} Exam_Details"]]
	content = content.rename(columns={f"Courses {i}": "course_id", f"Course {i} Section": "sec_no", \
		f"Course {i} EXAM_No": "exam_no", f"Course {i} Exam_Details" : "exam_details"})
	content.to_sql(f"Exams{i}", con=connection, if_exists='replace', index=False)
	connection.execute(f'DELETE FROM Exams{i} WHERE exam_no IS NULL;')
	convert("Exams", f"Exams{i}", connection)



#Exam_grades
connection.execute('CREATE TABLE IF NOT EXISTS Exam_grades(student_email TEXT, course_id TEXT, sec_no INT, exam_no INT, grade TEXT, \
	PRIMARY KEY (student_email, course_id, sec_no, exam_no));')

for i in range(1, 4):
	content = studentTA_Table[["Email", f"Courses {i}", f"Course {i} Section", f"Course {i} EXAM_No", f"Course {i} EXAM_Grade"]]
	content = content.rename(columns={"Email" : "email", f"Course {i}": "course_id", f"Course {i} Section": "sec_no", \
		f"Course {i} EXAM_No": "exam_no", f"Course {i} EXAM_Grade" : "grade"})
	content.to_sql(f"Exam_grades{i}", con=connection, if_exists='replace', index=False)
	connection.execute(f'DELETE FROM Exam_grades{i} WHERE exam_no IS NULL;')
	convert("Exam_grades", f"Exam_grades{i}", connection)



#Posts
connection.execute('CREATE TABLE IF NOT EXISTS Posts(course_id TEXT, post_no INT, student_email TEXT, post_info INT, \
	FOREIGN KEY (course_id, student_email) REFERENCES Enrolls (course_id, student_email) ON DELETE CASCADE, \
	PRIMARY KEY (course_id, post_no));')

content = forum_table[["Courses", "Post 1 By", "Post 1"]]
content = content.rename(columns={"Courses" : "course_id", "Post 1 By": "student_email", "Post 1" : "post_info"})
content.to_sql("PostsTool", con=connection, if_exists='replace', index=False)
connection.execute('DELETE FROM PostsTool WHERE post_info IS NULL;')
connection.execute('ALTER TABLE PostsTool ADD post_no INT;')
connection.execute('UPDATE PostsTool SET post_no = 1')
connection.execute('INSERT OR REPLACE INTO Posts SELECT course_id, post_no, student_email, post_info FROM PostsTool;')
connection.execute('DROP TABLE PostsTool;')
connection.commit()


#Comments
connection.execute('CREATE TABLE IF NOT EXISTS Comments(course_id TEXT, post_no INT, comment_no INT, student_email TEXT, \
	comment_info TEXT, \
	FOREIGN KEY (course_id, post_no) REFERENCES Posts (course_id, post_no) ON DELETE CASCADE, \
	FOREIGN KEY (course_id, student_email) REFERENCES Enrolls (course_id, student_email) ON DELETE CASCADE, \
	PRIMARY KEY (course_id, post_no, comment_no));')


content = forum_table[["Courses", "Comment 1 By", "Comment 1"]]
content = content.rename(columns={"Courses" : "course_id", "Comment 1 By": "student_email", "Comment 1" : "comment_info"})
content.to_sql("CommentsTool", con=connection, if_exists='replace', index=False)
connection.execute('DELETE FROM CommentsTool WHERE comment_info IS NULL;')
connection.execute('ALTER TABLE CommentsTool ADD post_no INT;')
connection.execute('ALTER TABLE CommentsTool ADD comment_no INT;')
connection.execute('UPDATE CommentsTool SET post_no = 1')
connection.execute('UPDATE CommentsTool SET comment_no = 1')
connection.execute('INSERT OR REPLACE INTO Comments SELECT course_id, post_no, comment_no, student_email, comment_info FROM CommentsTool;')
connection.execute('DROP TABLE CommentsTool;')
connection.commit()


connection.close()





