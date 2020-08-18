from flask import Flask, render_template, request
from aux import *
from SQLtool import *

app = Flask(__name__)
host = 'http://127.0.0.1:5000/'

#Start page, NOTE: usertype 0: student, 1: TA, 2: Professor
@app.route('/', methods=['POST', 'GET'])
def index():
  error = None
  if request.method == 'POST':

    email = request.form['email']
    password = pullPassword(email)
    print(password)
    if password and (hash(password) == hash(request.form['pwd'])): #pulls password from database and compares with hashed input
      userinfo, usertype = pullUserInfoType(email)
      avatar = getAvatar(userinfo) #grants the user a random avatar in accordance to their gender
      if usertype in ['0','1']: 
        return render_template('studentTAProfile.html', error=error, userinfo=userinfo, usertype=usertype, avatar=avatar)
      return render_template('professorProfile.html', error=error, userinfo=userinfo, usertype=usertype, avatar=avatar)
    else:
      error = "error"
  return render_template('homepage.html', error=error)
  

@app.route('/profile', methods=['POST', 'GET'])
def userProfile():
    error = None
    if request.method == 'POST':
        userinfo, usertype, avatar, currentpassword, newpassword = request.form['userinfo'], request.form['usertype'], \
            request.form["avatar"], request.form['currentpassword'], request.form['newpassword']
        userinfo = eval(userinfo)
        error = passwordChange(userinfo, usertype, currentpassword, newpassword) #checks if the current password is actually the users current password
        if usertype in ['0', '1']:
            return render_template('studentTAProfile.html', error=error, userinfo=userinfo, usertype=usertype, avatar=avatar)
        return render_template('professorProfile.html', error=error, userinfo=userinfo, usertype=usertype, avatar=avatar)
   
    url = request.url
    email = parseURLforEmail(url)
    userinfo, usertype = pullUserInfoType(email)
    avatar = getAvatar(userinfo)
    if usertype in ['0','1']: #Different profile styles for either a student/TA or a Professor
        return render_template('studentTAProfile.html', error=error, userinfo=userinfo, usertype=usertype, avatar=avatar)
    return render_template('professorProfile.html', error=error, userinfo=userinfo, usertype=usertype, avatar=avatar)    


@app.route('/enrolled', methods=['POST', 'GET'])
def userEnrolled():
  dropped = None
  url = request.url
  email = parseURLforEmail(url)

  if request.method == 'POST': #for dropping a course
    if request.form['mode'] == 'dropCourse':  
      course_id = request.form['course_selection']
      deadline = pullDeadline(course_id)[0]
      if beforeDate(deadline): #checks if the deadline has been passed
        dropCourse(email, course_id)
        dropped = 1
      else:
        dropped = -1

  name, usertype = pullNameType(email)
  courseProfessorInfoList = rowsToList(pullCourseProfessorInfo(email))
  courseIDs = [infoDict['course_id'] for infoDict in courseProfessorInfoList]
  homeworks = [rowsToList(pullHWbyCourse(email, course)) for course in courseIDs]
  exams = [rowsToList(pullExambyCourse(email, course)) for course in courseIDs]
  zippedInformation = list(zip(courseProfessorInfoList, homeworks, exams)) #combines courses, sections, hws, and exams into an easily iteratible list

  if usertype == "1": #A TA will also have a view of the classes they teach
    TACourseList = rowsToList(pullTACourses(email))
    return render_template('enrollment.html', zippedInformation = zippedInformation, TACourseList = TACourseList, \
        name = name, email = email, usertype = usertype, dropped = dropped)

  return render_template('enrollment.html', zippedInformation = zippedInformation, name = name, email = email, \
    usertype = usertype, dropped = dropped)


@app.route('/manageAssignments', methods=['POST', 'GET'])
def manageAssignments():
    createQuery, deleteQuery = None, None

    if request.method == 'POST':
        if request.form['mode'] == 'create': #Creating an assignment requires creation via the section as well as to hw and exam grades
            course_id, sec_no, assignmentType, description = request.form["course_id"], request.form["sec_no"], \
            request.form["assignmentType"], request.form["description"]

            assignment_no = pushNewAssignment(course_id, sec_no, assignmentType, description)
            studentLst = pullAllStudentsInCourseSection(course_id, sec_no)
            pushAssignmentToStudentGrades(course_id, sec_no, assignment_no, studentLst, assignmentType)
            createQuery = {"course_id": course_id, "sec_no": sec_no, "assignmentType": assignmentType}

    url = request.url #The following lines assemble all courses, sections, and assignments the Professor has issued in a clean list to be iterated over
    email = parseURLforEmail(url)
    courseSectionsTaught = rowsToList(pullCoursesandSectionsTaught(email))
    courseSectionsDict = flattenDicts(courseSectionsTaught)
    hwDict, examDict = {}, {}
    for course in courseSectionsDict:
        for section in courseSectionsDict[course]:
            hwDict[course,section] = rowsToList(pullHWbyCourseSection(course, section))
            examDict[course,section] = rowsToList(pullExambyCourseSection(course, section))

    table = constructTable(courseSectionsDict, hwDict, examDict) #Combines all elements to a clean table format
    reducedTable = reduceTable(table) #Removes redundant labels in the table

    reducedCourseSectionsDict, reducedAssignmentList = reduceDict(courseSectionsDict), reduceCombinedDicts(hwDict, examDict)
    simpleHW, simpleExam = simplifyDict(hwDict, 'hw'), simplifyDict(examDict, 'exam')


    if request.method == 'POST': #Removing an assignment likewise requires destruction via the section as well as to hw and exam grades
        if request.form['mode'] == 'delete':
            course_id, sec_no, assignmentType, assignment_no = request.form["course_id"], request.form["sec_no"], \
            request.form["assignmentType"], request.form["assignment_no"]

            killAssignment(course_id, sec_no, assignmentType, assignment_no)
            studentLst = pullAllStudentsInCourseSection(course_id, sec_no)
            killAssignmentFromStudentGrades(course_id, sec_no, assignment_no, studentLst, assignmentType)
            deleteQuery = {"course_id": course_id, "sec_no": sec_no, "assignmentType": assignmentType, "assignment_no": assignment_no}

    return render_template('manageAssignments.html', email = email, courseSectionsDict = courseSectionsDict, reducedTable = reducedTable, \
        hwDict = hwDict, examDict = examDict, reducedCourseSectionsDict = reducedCourseSectionsDict, reducedAssignmentList = reducedAssignmentList,
        createQuery = createQuery, deleteQuery = deleteQuery, simpleHW = simpleHW, simpleExam = simpleExam)


@app.route('/gradeAssignments', methods=['POST', 'GET'])
def gradeAssignments():
    gradeList, query, studentIndexList, errorDict = None, None, None, None
    if request.method == 'POST':
        if request.form['mode'] == 'query': #Pulls all relevant students from a grading query
            course_id, sec_no, assignmentType, assignment_no, subset = request.form["course_id"], request.form["sec_no"], \
                request.form["assignmentType"], request.form["assignment_no"], request.form["subset"]
            query = {"course_id": course_id, "sec_no": sec_no, "assignmentType": assignmentType, "assignment_no": assignment_no, "subset": subset}

        elif request.form['mode'] == 'modify': #Allows for modification of student's grades
            gradeList, query = eval(request.form['gradeList']), eval(request.form['query'])

            course_id, sec_no, assignmentType, assignment_no, subset = query["course_id"], query["sec_no"], \
                query["assignmentType"], query["assignment_no"], query["subset"]
            
            auxGradeList = [(request.form[f'student{i+1}'], request.form[f'grade{i+1}']) for i in range(len(gradeList))] #All of the grades

            if query['assignmentType'] == 'hw':
                allAdjustedGrades = [{'student_email': student[0], 'course_id': course_id, 'sec_no': int(sec_no), \
                'hw_no': int(assignment_no), 'grade': student[1]} for student in auxGradeList]
            else: 
                allAdjustedGrades = [{'student_email': student[0], 'course_id': course_id, 'sec_no': int(sec_no), \
                'exam_no': int(assignment_no), 'grade': student[1]} for student in auxGradeList]

            errorDict, erroneousIndexList = validateAllAdjustedGrades(allAdjustedGrades) #Checks for improper grades (>0, <100, strings)
            gradeList = removeElements(gradeList, erroneousIndexList)
            allAdjustedGrades = removeElements(allAdjustedGrades, erroneousIndexList)

            adjustedGrades = [allAdjustedGrades[i] for i in range(len(gradeList)) if gradeList[i] != allAdjustedGrades[i]] #just the valid grades

            if query['assignmentType'] == 'hw': #reassigns each of the grades to the student's end as well
                [updateGrade(student['student_email'], student['course_id'], student['sec_no'], student['hw_no'], \
                    'hw', student['grade']) for student in adjustedGrades]
            else:
                [updateGrade(student['student_email'], student['course_id'], student['sec_no'], student['exam_no'], \
                    'exam', student['grade']) for student in adjustedGrades]

        gradeList = rowsToList(pullStudentsGrades(course_id, sec_no, assignment_no, assignmentType, subset))
        studentIndexList = [(f'student{i+1}', f'grade{i+1}', f'error{i+1}') for i in range(len(gradeList))]
        onlyGrades = [student['grade'] for student in gradeList]
        stats = gradeStatistics(onlyGrades) #Statistics about the student grades. I never ended up using this due to time constraints.

    url = request.url
    email = parseURLforEmail(url)
    courseSectionsTaught = rowsToList(pullCoursesandSectionsTaught(email)) 
    courseSectionsDict = flattenDicts(courseSectionsTaught)
    hwDict, examDict = {}, {}
    for course in courseSectionsDict:
        for section in courseSectionsDict[course]:
            hwDict[course,section] = rowsToList(pullHWbyCourseSection(course, section))
            examDict[course,section] = rowsToList(pullExambyCourseSection(course, section))

    ungradedHWDict, ungradedExamDict = {}, {}
    for course in courseSectionsDict:
        for section in courseSectionsDict[course]:    
            ungradedHWDict[course,section] = pullAssignmentCountbyCourseSection(course, section, 'hw')
            ungradedExamDict[course,section] = pullAssignmentCountbyCourseSection(course, section, 'exam')

    table = constructUngradedTable(courseSectionsDict, ungradedHWDict, ungradedExamDict) #All student grades for the given selection organized neatly
    reducedUngradedTable = reduceTable(table) 

    reducedCourseSectionsDict, reducedAssignmentList = reduceDict(courseSectionsDict), reduceCombinedDicts(hwDict, examDict) #Combines elements with similar keys

    simpleHW, simpleExam = simplifyDict(hwDict, 'hw'), simplifyDict(examDict, 'exam')

    return render_template('gradeAssignments.html', email = email, courseSectionsDict = courseSectionsDict, reducedTable = reducedUngradedTable, \
        hwDict = hwDict, examDict = examDict, gradeList = gradeList, query = query, studentIndexList = studentIndexList, errorDict = errorDict, \
        reducedCourseSectionsDict = reducedCourseSectionsDict, reducedAssignmentList = reducedAssignmentList, simpleHW = simpleHW, \
        simpleExam = simpleExam)


@app.route('/forums', methods=['POST', 'GET'])
def courseForums():
    url = request.url
    email = parseURLforEmail(url)
    name, usertype = pullNameType(email)

    if request.method == 'POST': 
        if request.form['mode'] == 'addPost': #For adding a post. Finds a unique post number and adds to the database
            course_id, content = request.form["course_selection"], request.form["content"]
            maxPostNo = pullMaxPostNo(course_id)
            if not maxPostNo: maxPostNo = 1
            pushNewPost(course_id, maxPostNo + 1, email, content)

        if request.form['mode'] == 'addComment': #For adding a comment. Finds a unique comment number and adds to the database
            course_id, post_no, content = request.form["course_id"],request.form["post_no"], request.form["content"]
            maxCommentNo = pullMaxCommentNo(course_id, post_no)
            if not maxCommentNo: maxCommentNo = 1
            pushNewComment(course_id, post_no, maxCommentNo + 1, email, content)

        if request.form['mode'] == 'deletePost': #For deleting a post
            postDict = eval(request.form['postToDelete'])
            deletePost(postDict['course_id'], postDict['post_no'])

        if request.form['mode'] == 'deleteComment': #For deleting a comment
            commentDict = eval(request.form['commentToDelete'])
            deleteComment(commentDict['course_id'], commentDict['post_no'], commentDict['comment_no'])

    courseProfessorInfoList = rowsToList(pullCourseProfessorInfo(email))
    courseIDs, posts = [], {}
    courseIDs = [infoDict['course_id'] for infoDict in courseProfessorInfoList]
    posts = simplifyPosts(flat([rowsToList(pullPostInfo(courseID)) for courseID in courseIDs]))
    
    teachingCourseIDs, teachingPosts = [], {}
    teachingCourseIDs = removeDuplicates([course['course_id'] for course in rowsToList(pullTACourses(email))] + \
        [course['course_id'] for course in pullCoursesTaught(email)])
    teachingPosts = simplifyPosts(flat([rowsToList(pullPostInfo(courseID)) for courseID in teachingCourseIDs]))

    comments = {} #Grabs lists of comments with the post as a key
    for course_id in courseIDs:
        if course_id not in posts.keys():
            posts.update({course_id:[]})
            continue
        for post in posts[course_id]:
            comments[(course_id, post['post_no'])] = rowsToList(pullCommentInfo(course_id, post['post_no']))

    teachingComments = {} #Grabs lists of comments for classes the user is teaching with the post as a key
    for course_id in teachingCourseIDs:
        if course_id not in teachingPosts.keys():
            teachingPosts.update({course_id:[]})
            continue
        for post in teachingPosts[course_id]:
            teachingComments[(course_id, post['post_no'])] = rowsToList(pullCommentInfo(course_id, post['post_no']))

    return render_template('forums.html', usertype = usertype, name = name, email = email, posts = posts, comments = comments,
        teachingPosts = teachingPosts, teachingComments = teachingComments)


if __name__ == "__main__":
  app.run()

