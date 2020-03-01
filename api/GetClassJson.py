import json
import re
import sys
import time

import requests
from lxml import etree
from config.CONST import *
import config.CONST as CONST
import server
from flask import session



def getSmID(source):
	"""
	Pre: yyyymmdd
	Post: 获得学期id。当前学期为769，每向前一个学期减少/增加32。
	"""
	if(len(str(source)) != 5):
		return CONST.BASE_SMID

	year = int(source[0:4])
	sem = int(source[4:5])
	id = 705 + (int(year) - 2018) * 96 + (int(sem) - 1) * 32
	return id

def getIDS(requestid):
	s = requests.session()
	# s.cookies.update(server.sessions[requestid])
	s.cookies.update(requests.utils.cookiejar_from_dict(session.get("usercookie")))
	r = s.get(CONST.IDS_URL)
	src = r.text
	rule = re.compile('bg\.form\.addInput\(form,"ids","(.*?)"\);', re.S)
	ids = re.findall(rule, src)
	if (len(ids) == 0):
		return -1
	return ids[0]

def dumpClassJson(raw):
	"""
	:param raw: 原始的列表数据格式：
	# processed 数据结构：
	# 	[教师名字，课程名，上课地点，起始周数，结束周数，从第一周开始的上课信息，星期, [每天要上的节数 n1, n2, ...],
	# 	[第二门课],
	# 	[第三门课]...
	# ]
	:return: 返回Json格式的课程信息
	"""
	final = {"classes":[]}
	for one in raw:
		newone = {
			"name": re.sub('\([\.A-Z0-9]*?\)', '', one[1]),
			"teacher": one[0],
			"classroom": one[2],
			"weekdata": one[3],
			"weekday": int(one[4]) + 1,	# [

			"classtime": one[5]
		}
		final["classes"].append(newone)
	# return json.dumps(final, ensure_ascii=False, indent=4)
	return final


def WeekProcessor(raw):
	"""
	输入：类似于 0111111111111111111000000000000000000000 的周数信息
	返回值：一个列表[起始周数, 结束周数, 1单周2双周3每周]
	"""
	weekData = []
	begin = 0
	end = 30
	typeFlag = 0
	beginFixed = False
	endFixed = False
	for i in range(len(raw)):
		if (raw[i] == '1' and beginFixed == False):
			beginFixed = True
			begin = i
			if (i % 2 == 1 and raw[i + 1] == '0'):
				typeFlag = 1
			elif (i % 2 == 0 and raw[i + 1] == '0'):
				typeFlag = 2
			elif (raw[i + 1] == '1' and raw[i+2] == '1'):
				typeFlag = 3
			else:
				typeFlag = 3
		if (raw[i] == '0' and raw[i + 1] == '0' and beginFixed == True and endFixed == False):
			endFixed = True
			end = i - 1
		if (beginFixed == True and endFixed == True):
			break
	return [begin, end, typeFlag]

def dumpXJDJson(classList):
	requestid = session.get("requestid")
	classInfo = {'classInfo': []}
	with open(DEPLOY_PATH + 'config/conf_classTime.json', 'r', encoding='utf-8') as f:
		classTime = json.load(f)
	classTimes = []
	# 获取 conf_classTime.json 中的配置文件，并和 classList 的配置匹配
	# 由于 classList 中的课程节数从 0 开始，所以需要从 json 中 - 1 匹配
	for oneTime in classTime['classTime']:
		temp = re.findall(r"\d+\.?\d*", oneTime['name'])
		temp = list(map(int, temp))
		for i in range(len(temp)):
			temp[i] = temp[i] - 1
		classTimes.append(temp)
	for aClass in classList:
		nameRaw = aClass[1]
		nameNew = re.sub('\([\.A-Z0-9]*?\)', '', nameRaw)
		try:
			source = classTimes.index(aClass[7]) + 1
		except:
			print('出现未在 conf_classTime.json 中配置过的课程时间，请检查。')
		classData = {'className': nameNew,
		             'week': {'startWeek': aClass[3], 'endWeek': aClass[4]},
		             'weekday': aClass[6] + 1,
		             'weeks': aClass[5],
		             'classTime': classTimes.index(aClass[7]) + 1,
		             'classroom': aClass[2]}
		classInfo['classInfo'].append(classData)
	with open(DEPLOY_PATH + 'static/temp/json/classInfo_' + requestid + '.json', 'w+', encoding='utf8') as f:
		json.dump(classInfo, f, indent=4, ensure_ascii=False)


def getClass(requestid, src):
	"""
	:param requestid: Session id
	:param src: Semester data
	:return: 课程数据或者：
		-1 未知错误
		-6 会话过期
	"""
	requestid = session.get('requestid')
	smid = getSmID(src);
	ids = getIDS(requestid)
	tablePostData = {'ignoreHead': 1,
	                 'setting.kind': 'std',
	                 'startWeek': 1,
	                 'semester.id': smid,
	                 'ids': ids}
	s = requests.session()
	# s.cookies.update(server.sessions[requestid])
	s.cookies.update(requests.utils.cookiejar_from_dict(session.get("usercookie")))
	r = s.post(CONST.TABLE_URL, data=tablePostData)
	elements = etree.HTML(r.content)

	if (r.text == 'This session has been expired (possibly due to multiple concurrent logins being attempted as the same user).'):
		return -6

	# 提取出具有课程的数据
	raws = elements.xpath('//*[@language="JavaScript"][3]/text()')
	if (len(raws) == 0):
		return -1
	# 使用新的正则表达式匹配每一节课所在的时间
	rawClasses = re.findall(
		'(.\*unitCount\+\d+)|new TaskActivity\((.*?),null', raws[0])
	processing = []
	processed = []
	i = 0
	dynaLen = len(rawClasses)
	# 第一次处理混乱的数据
	# processing 数据结构:
	# [
	# 	[杂糅在一起的课程名教师地点和上课周等等, [每周上课的星期, [每天要上的节数 n1, n2, ...]]],
	# 	[第二门课],
	# 	[第三门课]...
	# ]
	while i < dynaLen - 2:
		temp = []
		if (len(rawClasses[i][0]) == 0):
			temp.append(rawClasses[i][1])
			whichDay = 0
			allUnits = []
			while (len(rawClasses[i + 1][0]) != 0):
				whichDay = int(rawClasses[i + 1][0][0])
				unit = rawClasses[i + 1][0][12:]
				allUnits.append(unit)
				# 将截取出来的 str 类型转换成 int 方便计算
				allUnits = list(map(int, allUnits))
				if (i == len(rawClasses) - 2):
					break
				del rawClasses[i + 1]
			temp.append([whichDay, allUnits])
			processing.append(temp)
		i = i + 1
		dynaLen = len(rawClasses)
	# 第二次整理数据
	# processed 数据结构：
	# [
	# 	[教师名字，课程名，上课地点，起始周数，结束周数，从第一周开始的上课信息，星期, [每天要上的节数 n1, n2, ...],
	# 	[第二门课],
	# 	[第三门课]...
	# ]
	print('已获取课程:')
	for one in processing:
		temp = []
		temp.extend(one[0].replace('"', '').split(','))
		del temp[4], temp[2], temp[0]
		weekData = WeekProcessor(temp[3])
		del temp[3]
		temp.extend(weekData)
		temp.extend(one[1])
		processed.append(temp)
		print(temp[1])

	# 生成供转换的 json 文件
	dumpXJDJson(processed)

	# 返回详细的自定义格式
	return dumpClassJson(processed)