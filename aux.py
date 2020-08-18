import random
import os
import collections
import numpy as np
import datetime

imageDirectory = "./static/photos/"

def parseURLforEmail(url):
  email = url[url.find("=")+1:]
  if email[-1] == '#': email = email[:-1]
  email = email.replace("%40", "@")
  return email

def getAvatar(userinfo):
  maleAvatars = [file for file in os.listdir(imageDirectory) if (("male" in file) and not ("female" in file))]
  femaleAvatars = [file for file in os.listdir(imageDirectory) if "female" in file]
  return f'photos/{random.choice(maleAvatars) if userinfo["gender"] == "M" else random.choice(femaleAvatars)}'

def rowsToList(SQLFunctionCall):
  return list(map(lambda a: dict(a), SQLFunctionCall))

def flattenDicts(lst):
  returnDict = {}
  courseList = [courseSection['course_id'] for courseSection in lst]
  for course in courseList:
    returnDict[course] = sorted([courseSection['sec_no'] for courseSection in lst if courseSection['course_id'] == course])
  return returnDict

def constructTable(courseSectionsDict, hwDict, examDict):
    viewerList = []
    for course in courseSectionsDict:
        for section in courseSectionsDict[course]:
            for hw in hwDict[(course, section)]:
                viewerList.append({'course_id': course, 'sec_no': section, 'assignment_no': hw['hw_no'], 'assignment_details': hw['hw_details'], 'type': 'hw'})
            for exam in examDict[(course, section)]:
                viewerList.append({'course_id': course, 'sec_no': section, 'assignment_no': exam['exam_no'], 'assignment_details': exam['exam_details'], 'type': 'exam'})

    return viewerList

def constructUngradedTable(courseSectionsDict, hwDict, examDict):
    viewerList = []
    for course in courseSectionsDict:
        for section in courseSectionsDict[course]:
            for hw in hwDict[(course, section)]:
            	if hw['numberUngraded'] != 0: 
                	viewerList.append({'course_id': course, 'sec_no': section, 'assignment_no': hw['hw_no'], 'numberUngraded': hw['numberUngraded'], 'type': 'hw'})
            for exam in examDict[(course, section)]:
                if exam['numberUngraded'] != 0: 
                	viewerList.append({'course_id': course, 'sec_no': section, 'assignment_no': exam['exam_no'], 'numberUngraded': exam['numberUngraded'], 'type': 'exam'})

    return viewerList


def reduceTable(table):
	existingVals = {}
	for i in ['course_id', 'sec_no']:
		for j in table:
			if j[i] in existingVals:
				j[i] = ''
			else: 
				existingVals[j[i]] = 1
	return table


def validateAllAdjustedGrades(allAdjustedGrades):
	errorDict = {}
	erroneousIndexList = []
	for i in range(len(allAdjustedGrades)):
		if (allAdjustedGrades[i]['grade']).isspace() or (allAdjustedGrades[i]['grade'] == ''): 
			continue
		try: 
			float(allAdjustedGrades[i]['grade'])

		except:
			errorDict[f'error{i+1}'] = 1
			erroneousIndexList.append(i)
			continue

		if not (0 <= float(allAdjustedGrades[i]['grade']) <= 100):
			errorDict[f'error{i+1}'] = 1
			erroneousIndexList.append(i)			

	errorDict = errorDict if errorDict else False
	return errorDict, erroneousIndexList


def removeElements(inputLst, removeLst):
	return [inputLst[i] for i in range(len(inputLst)) if i not in removeLst]

def reduceDict(inputDict):
	toolDict, cleanDict = {}, {}
	for key in inputDict:
		for elem in inputDict[key]:
			if elem not in toolDict:
				toolDict[elem] = 1
				if key in cleanDict:
					cleanDict[key] += [elem]
				else: 
					cleanDict[key] = [elem]
				
	return cleanDict

def reduceCombinedDicts(hwDict, examDict):
	returnList, toolDict = [], {}
	for dictionary in [hwDict, examDict]:
		mode = 'hw' if dictionary == hwDict else 'exam'
		for key in dictionary:
			for elem in dictionary[key]:
				if elem[f'{mode}_no'] not in toolDict: 
					toolDict[elem[f'{mode}_no']] = 1
					returnList.append(elem[f'{mode}_no'])

	return sorted(returnList)

def simplifyDict(inputDict, mode):
	returnDict = {}
	for key in inputDict.keys():
		for assignmentDict in inputDict[key]:
			if key in returnDict:
				returnDict[key] += [assignmentDict[f'{mode}_no']]
			else:
				returnDict[key] = [assignmentDict[f'{mode}_no']]
	return returnDict

#max, min, average, median, mode, standard deviation, 
def gradeStatistics(gradeList):
	gradeList = list(filter(lambda a: a != '' and a != None, gradeList))
	gradeList = list(map(lambda a: float(a), gradeList))
	if not gradeList: return []
	statisticsList = []
	statisticsList.append(max(gradeList))
	statisticsList.append(min(gradeList))
	statisticsList.append(sum(gradeList)/len(gradeList))
	statisticsList.append(gradeList[len(gradeList)//2] if len(gradeList)%2==1 else ((gradeList[len(gradeList)//2] + gradeList[len(gradeList)//2 - 1])/2))
	statisticsList.append(collections.Counter(gradeList).most_common(1)[0][0])
	statisticsList.append(np.std(gradeList))
	return statisticsList

def flat(aList):
    if not aList:
        return []
    elif type(aList[0]) == list:
        return flat(aList[0]) + flat(aList[1:])
    else:
        return [aList[0]] + flat(aList[1:])

def simplifyPosts(posts):
	postsDict = {}
	for post in posts:
		if post['course_id'] in postsDict.keys():
			postsDict[post['course_id']] += [post]
		else:
			postsDict[post['course_id']] = [post]
	return postsDict	


def simplifyComments(comments):
	commentsDict = {}
	for comment in comments:
		if (comment['course_id'],comment['post_no']) in commentsDict.keys():
			commentsDict[(comment['course_id'],comment['post_no'])] += [comment]
		else:
			commentsDict[(comment['course_id'],comment['post_no'])] = [comment]
	return commentsDict

def removeDuplicates(lst):
	dupDict = {}
	returnLst = []
	for elem in lst:
		if elem not in dupDict:
			dupDict.update({elem:1})
			returnLst.append(elem)
	return returnLst

def beforeDate(date):
	currentDate = datetime.datetime.now()
	month = int(date[:2])
	day = int(date[3:5])
	year = int(date[6:]) + 2000
	deadlineDate = datetime.datetime(year, month, day)
	print(currentDate, deadlineDate)
	print(currentDate <= deadlineDate)
	return currentDate <= deadlineDate


