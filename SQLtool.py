import sqlite3 as sql
from aux import *

database = 'projectdatabase.db'

def pullUserInfoType(email):
  usertype = None
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  student = connection.execute(f'SELECT email, name, age, gender, major, street, zipcode, phone FROM Students \
    WHERE email="{email}";')
  if (userinfo := student.fetchone()):
    usertype = '0'
    if connection.execute(f'SELECT * FROM TA_teaching_teams WHERE student_email="{email}";').fetchone():
      usertype = '1'

    return (dict(userinfo), usertype)

  professor = connection.execute(f'SELECT email, name, age, gender, office_address, department, title FROM Professors \
    WHERE email="{email}";')
  if (userinfo := professor.fetchone()):
    usertype = '2'
  
  return (dict(userinfo), usertype) if usertype != None else None

#Student: 0, TA: 1, Professor: 2
def pullPassword(email):
  usertype = None
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  
  studentPassword = connection.execute(f'SELECT password FROM Students \
    WHERE email="{email}";').fetchone()
    
  professorPassword = connection.execute(f'SELECT password FROM Professors \
    WHERE email="{email}";').fetchone()

  returnPassword = studentPassword or professorPassword

  return dict(returnPassword)['password'] if returnPassword else None
 

#Returns user information as a dictionary and an error value: 0 if password has successfully been changed, 1 if the current password is incorrect
def passwordChange(userinfo, usertype, currentpassword, newpassword):
  connection = sql.connect(database)
  usertypeWord = "Professors" if usertype == "2" else "Students"
  check = connection.execute(f'SELECT email FROM {usertypeWord} WHERE email="{userinfo["email"]}" AND password="{currentpassword}";')
  if check.fetchone():
    connection.execute(f'UPDATE {usertypeWord} SET password="{newpassword}" WHERE email="{userinfo["email"]}";')
    connection.commit()
    return "passwordSuccess"
  return "curPasswordIncorrect"


def pullCourseProfessorInfo(email):
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  cur = connection.cursor()
  courseProfessorInfo = connection.execute(f'SELECT B.course_id, B.sec_no, Courses.course_name, Courses.course_description, \
    Courses.late_drop_deadline, Professors.name, Professors.email, Professors.office_address \
    FROM Professors, Prof_teaching_teams, Courses,  \
    (SELECT A.course_id, A.sec_no, Sections.teaching_team_id \
        FROM Sections, \
        (SELECT Enrolls.course_id, Enrolls.sec_no \
          FROM Enrolls \
          INNER JOIN Courses \
          ON Enrolls.course_id = Courses.course_id \
          WHERE student_email="{email}") as A \
        WHERE A.course_id = Sections.course_id \
        AND A.sec_no = Sections.sec_no) as B \
    WHERE B.teaching_team_id = Prof_teaching_teams.teaching_team_id \
    AND Prof_teaching_teams.prof_email = Professors.email \
    AND Courses.course_id = B.course_id;')
  rows = courseProfessorInfo.fetchall()
  return rows 


def pullTACourses(email):
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  cur = connection.cursor()
  TACourseInfo = connection.execute(f'SELECT TA_teaching_teams.teaching_team_id, Courses.course_id, Sections.sec_no, Professors.email, \
    Professors.name, Professors.office_address \
    FROM TA_teaching_teams, Prof_teaching_teams, Professors, Courses, Sections \
    WHERE student_email = "{email}" \
    AND Prof_teaching_teams.teaching_team_id = TA_teaching_teams.teaching_team_id \
    AND Prof_teaching_teams.prof_email = Professors.email \
    AND Sections.teaching_team_id = Prof_teaching_teams.teaching_team_id \
    AND Sections.course_id = Courses.course_id;')
  rows = TACourseInfo.fetchall()
  return rows 


def pullHWbyCourse(email, course_id):
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  cur = connection.cursor()
  hwinfo = connection.execute(f'SELECT Homework_grades.hw_no, Homework_grades.grade, Homeworks.hw_details \
    FROM Enrolls, Homeworks, Homework_grades \
    WHERE Enrolls.student_email = "{email}" \
    AND Enrolls.course_id = "{course_id}" \
    AND Homeworks.hw_no = Homework_grades.hw_no \
    AND Enrolls.course_id = Homeworks.course_id \
    AND Homeworks.course_id = Homework_grades.course_id \
    AND Enrolls.sec_no =  Homeworks.sec_no \
    AND Homework_grades.student_email = Enrolls.student_email;')
  rows = hwinfo.fetchall()
  return rows 

def pullExambyCourse(email, course_id):
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  cur = connection.cursor()
  examinfo = connection.execute(f'SELECT Exam_grades.exam_no, Exam_grades.grade, Exams.exam_details \
    FROM Enrolls, Exams, Exam_grades \
    WHERE Enrolls.student_email = "{email}" \
    AND Enrolls.course_id = "{course_id}" \
    AND Exams.exam_no = Exam_grades.exam_no \
    AND Enrolls.course_id = Exams.course_id \
    AND Exams.course_id = Exam_grades.course_id \
    AND Enrolls.sec_no =  Exams.sec_no \
    AND Exam_grades.student_email = Enrolls.student_email;')
  rows = examinfo.fetchall()
  return rows 


def pullNameType(email):
  usertype = None
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  student = connection.execute(f'SELECT name FROM Students \
    WHERE email="{email}";')
  if (userinfo := student.fetchone()):
    usertype = '0'
    if connection.execute(f'SELECT * FROM TA_teaching_teams WHERE student_email="{email}";').fetchone():
      usertype = '1'
    return (dict(userinfo)["name"], usertype)

  professor = connection.execute(f'SELECT name FROM Professors \
    WHERE email="{email}";')
  if (userinfo := professor.fetchone()):
    usertype = '2'

  return (dict(userinfo)["name"], usertype) if usertype != None else None


def pullCoursesandSectionsTaught(email):
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  cur = connection.cursor()
  courseSectionsTaught = connection.execute(f'SELECT Sections.course_id, Sections.sec_no \
    FROM Prof_teaching_teams, Sections \
    WHERE Prof_teaching_teams.prof_email = "{email}" \
    AND Prof_teaching_teams.teaching_team_id = Sections.teaching_team_id;')
  rows = courseSectionsTaught.fetchall()
  return rows 

def pullCoursesTaught(email):
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  cur = connection.cursor()
  courseSectionsTaught = connection.execute(f'SELECT DISTINCT Sections.course_id \
    FROM Prof_teaching_teams, Sections \
    WHERE Prof_teaching_teams.prof_email = "{email}" \
    AND Prof_teaching_teams.teaching_team_id = Sections.teaching_team_id;')
  rows = courseSectionsTaught.fetchall()
  return rows 


def pullHWbyCourseSection(course, section):
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  cur = connection.cursor()
  courseHWs = connection.execute(f'SELECT hw_no, hw_details \
    FROM Homeworks \
    WHERE Homeworks.course_id = "{course}" \
    AND Homeworks.sec_no = "{section}";')
  rows = courseHWs.fetchall()
  return rows 

def pullExambyCourseSection(course, section):
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  cur = connection.cursor()
  courseExams = connection.execute(f'SELECT exam_no, exam_details \
    FROM Exams \
    WHERE Exams.course_id = "{course}" \
    AND Exams.sec_no = "{section}";')
  rows = courseExams.fetchall()
  return rows 

def pushNewAssignment(course_id, sec_no, assignmentType, description):
  connection = sql.connect(database)
  if assignmentType == 'hw':
    maxNumber = connection.execute(f'SELECT MAX(hw_no) \
      FROM Homeworks \
      WHERE Homeworks.course_id = "{course_id}" \
      AND Homeworks.sec_no = "{sec_no}";').fetchone()
  else:
    maxNumber = connection.execute(f'SELECT MAX(exam_no) \
      FROM Exams \
      WHERE Exams.course_id = "{course_id}" \
      AND Exams.sec_no = "{sec_no}";').fetchone() 
  maxNumber = 0 if maxNumber == None else maxNumber[0]
  insertNo = maxNumber + 1

  if assignmentType == 'hw':
    connection.execute(f'INSERT INTO Homeworks (course_id, sec_no, hw_no, hw_details) \
      VALUES ("{course_id}", {sec_no}, {insertNo}, "{description}");')

  else: 
    connection.execute(f'INSERT INTO Exams (course_id, sec_no, exam_no, exam_details) \
      VALUES ("{course_id}", {sec_no}, {insertNo}, "{description}");')

  connection.commit()
  return insertNo

def killAssignment(course_id, sec_no, assignmentType, assignment_no):
  connection = sql.connect(database)
  if assignmentType == 'hw':
    connection.execute(f'DELETE FROM Homeworks \
      WHERE course_id = "{course_id}" \
      AND sec_no = "{sec_no}" \
      AND hw_no = "{assignment_no}";')
  else:
    connection.execute(f'DELETE FROM Exams \
      WHERE course_id = "{course_id}" \
      AND sec_no = "{sec_no}" \
      AND exam_no = "{assignment_no}";') 
  connection.commit()   
  
def pullAllStudentsInCourseSection(course_id, sec_no):
  connection = sql.connect(database)
  cur = connection.cursor()
  totalCount = connection.execute(f'SELECT student_email \
    FROM Enrolls \
    WHERE course_id = "{course_id}" \
    AND sec_no = {sec_no};')
  totalRow = totalCount.fetchall()  
  return([elem[0] for elem in totalRow]) 

def pushAssignmentToStudentGrades(course_id, sec_no, assignment_no, studentLst, assignmentType):
  connection = sql.connect(database)
  for student in studentLst:
    if assignmentType == "hw":
      totalCount = connection.execute(f' INSERT INTO Homework_grades (student_email, course_id, sec_no, hw_no, grade) \
        VALUES ("{student}", "{course_id}", {sec_no}, {assignment_no}, NULL);')
    else: 
      totalCount = connection.execute(f' INSERT INTO Exam_grades (student_email, course_id, sec_no, exam_no, grade) \
        VALUES ("{student}", "{course_id}", {sec_no}, {assignment_no}, NULL);')

  connection.commit()

def killAssignmentFromStudentGrades(course_id, sec_no, assignment_no, studentLst, assignmentType):
  connection = sql.connect(database)
  for student in studentLst:
    if assignmentType == "hw":
      totalCount = connection.execute(f'DELETE FROM Homework_grades \
        WHERE student_email = "{student}" \
        AND course_id = "{course_id}" \
        AND sec_no = {sec_no} \
        AND hw_no = {assignment_no};')
    else: 
      totalCount = connection.execute(f'DELETE FROM Exam_grades \
        WHERE student_email = "{student}" \
        AND course_id = "{course_id}" \
        AND sec_no = {sec_no} \
        AND exam_no = {assignment_no};')

  connection.commit()


def pullAssignmentCountbyCourseSection(course_id, sec_no, assignmentType):
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  cur = connection.cursor()
  if assignmentType == 'hw':
    totalCount = connection.execute(f'SELECT hw_no, COUNT(*) as numberGraded \
      FROM Homework_grades \
      WHERE course_id = "{course_id}" \
      AND sec_no = "{sec_no}" \
      GROUP BY hw_no;')
    
    gradedCount = connection.execute(f'SELECT hw_no, COUNT(grade) as numberGraded \
      FROM Homework_grades \
      WHERE course_id = "{course_id}" \
      AND sec_no = "{sec_no}" \
      GROUP BY hw_no;')

  else: 
    totalCount = connection.execute(f'SELECT exam_no, COUNT(*) as numberGraded \
    FROM Exam_grades \
    WHERE course_id = "{course_id}" \
    AND sec_no = "{sec_no}" \
    GROUP BY exam_no;')
  
    gradedCount = connection.execute(f'SELECT exam_no, COUNT(grade) as numberGraded \
    FROM Exam_grades \
    WHERE course_id = "{course_id}" \
    AND sec_no = "{sec_no}" \
    GROUP BY exam_no;')  
    
  totalList = rowsToList(totalCount.fetchall())
  gradedList = rowsToList(gradedCount.fetchall())
  ungradedList = []
  
  if assignmentType == 'hw':
    for i in range(len(totalList)):
      ungradedList.append({'hw_no': totalList[i]['hw_no'], 'numberUngraded': (totalList[i]['numberGraded'] - gradedList[i]['numberGraded'])})

  else: 
    for i in range(len(totalList)):
      ungradedList.append({'exam_no': totalList[i]['exam_no'], 'numberUngraded': (totalList[i]['numberGraded'] - gradedList[i]['numberGraded'])})
 
  return ungradedList

def pullStudentsGrades(course_id, sec_no, assignment_no, assignmentType, style):
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  cur = connection.cursor()
  filler = ' AND grade IS NULL' if style == 'ungraded' else ''
  if assignmentType == 'hw':
    rows = connection.execute(f'SELECT * \
      FROM Homework_grades \
      WHERE course_id = "{course_id}" \
      AND sec_no = "{sec_no}" \
      AND hw_no = "{assignment_no}"{filler};')
  else:  
    rows = connection.execute(f'SELECT * \
      FROM Exam_grades \
      WHERE course_id = "{course_id}" \
      AND sec_no = "{sec_no}" \
      AND exam_no = "{assignment_no}"{filler};')

  return rows


def updateGrade(student_email, course_id, sec_no, assignment_no, assignmentType, newGrade):
  connection = sql.connect(database)
  newGrade = 'NULL' if (newGrade.isspace() or newGrade == '') else float(newGrade)

  if assignmentType == 'hw':
    connection.execute(f'UPDATE Homework_grades \
      SET student_email = "{student_email}", course_id = "{course_id}", sec_no = {sec_no}, hw_no = {assignment_no}, grade = {newGrade} \
      WHERE student_email = "{student_email}" \
      AND course_id = "{course_id}" \
      AND sec_no = {sec_no} \
      AND hw_no = {assignment_no};')
  else:
    connection.execute(f'UPDATE Exam_grades \
      SET student_email = "{student_email}", course_id = "{course_id}", sec_no = {sec_no}, exam_no = {assignment_no}, grade = {newGrade} \
      WHERE student_email = "{student_email}" \
      AND course_id = "{course_id}" \
      AND sec_no = {sec_no} \
      AND exam_no = {assignment_no};')

  connection.commit()

def pullPostInfo(course_id):
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  cur = connection.cursor()  
  posts = connection.execute(f'SELECT course_id, name, post_no, post_info \
    FROM Posts, Students \
    WHERE Students.email = Posts.student_email \
    AND course_id = "{course_id}" \
    UNION \
    SELECT course_id, name, post_no, post_info \
    FROM Posts, Professors \
    WHERE Professors.email = Posts.student_email \
    AND course_id = "{course_id}";')
  rows = posts.fetchall()
  return rows

def pullCommentInfo(course_id, post_no):
  connection = sql.connect(database)
  connection.row_factory = sql.Row
  cur = connection.cursor()  
  comments = connection.execute(f'SELECT course_id, post_no, comment_no, name, comment_info \
    FROM Comments, Students \
    WHERE Students.email = Comments.student_email \
    AND course_id = "{course_id}" \
    AND post_no = {post_no} \
    UNION \
    SELECT course_id, post_no, comment_no, name, comment_info \
    FROM Comments, Professors \
    WHERE Professors.email = Comments.student_email \
    AND course_id = "{course_id}" \
    AND post_no = {post_no};')
  rows = comments.fetchall()
  return rows

def pullMaxPostNo(course_id):
  connection = sql.connect(database) 
  num = connection.execute(f'SELECT MAX(post_no) \
    FROM Posts \
    WHERE Posts.course_id = "{course_id}";')
  return num.fetchone()[0]

def pushNewPost(course_id, post_no, email, content): 
  connection = sql.connect(database)
  connection.execute(f'INSERT INTO Posts (course_id, post_no, student_email, post_info) \
    VALUES ("{course_id}", {post_no}, "{email}", "{content}");')
  connection.commit()

def pullMaxCommentNo(course_id, post_no):
  connection = sql.connect(database) 
  num = connection.execute(f'SELECT MAX(post_no) \
    FROM Comments \
    WHERE Comments.course_id = "{course_id}" \
    AND Comments.post_no = "{post_no}";')
  return num.fetchone()[0]

def pushNewComment(course_id, post_no, comment_no, email, content):
  connection = sql.connect(database)
  connection.execute(f'INSERT INTO Comments (course_id, post_no, comment_no, student_email, comment_info) \
    VALUES ("{course_id}", {post_no}, "{comment_no}", "{email}", "{content}");')
  connection.commit()

def deletePost(course_id, post_no):
  connection = sql.connect(database)
  cur = connection.cursor()
  cur.executescript(f'PRAGMA foreign_keys = ON; \
    DELETE FROM Posts \
    WHERE course_id = "{course_id}" \
    AND post_no = {post_no};')
  connection.commit()

def deleteComment(course_id, post_no, comment_no):
  connection = sql.connect(database)
  connection.execute(f'DELETE FROM Comments \
    WHERE course_id = "{course_id}" \
    AND post_no = {post_no} \
    AND comment_no = {comment_no};')
  connection.commit()

def dropCourse(email, course_id):
  connection = sql.connect(database)
  cur = connection.cursor()
  cur.executescript(f'PRAGMA foreign_keys = ON; \
    DELETE FROM Enrolls \
    WHERE student_email = "{email}" \
    AND course_id = "{course_id}";')
  connection.commit()

def pullDeadline(course_id):
  connection = sql.connect(database)
  deadline = connection.execute(f'SELECT late_drop_deadline \
    FROM Courses \
    WHERE course_id = "{course_id}";')
  return deadline.fetchone()




