# coding: utf-8
# !/usr/bin/python

import sys
import time, datetime
import json
from random import Random
from flask import session

from api.utils import Utils
from config import CONST
from config.CONST import *
__author__ = 'Xiejiadong'
__site__ = 'xiejiadong.com'

checkFirstWeekDate = 0
checkReminder = 1

YES = 0
NO = 1

DONE_firstWeekDate = time.time()
DONE_reminder = ""
DONE_EventUID = ""
DONE_UnitUID = ""
DONE_CreatedTime = ""
DONE_ALARMUID = ""

classTimeList = []
classInfoList = []
# reminderList = ["-PT10M", "-PT15M", "-PT20M", "-PT30M", "-PT1H", "-P1D"]

requestid = 0
obtainedClass = []


def GetClassCSV(semester, reminder):
	obtainedClass.clear()
	global requestid
	requestid = session.get("requestid")
	setReminder(reminder)
	setFirstWeekDate(CONST.FIRST_WEEK_DATE[semester])
	setClassInfo()
	setClassTime()
	uniteSetting();
	classInfoHandle();
	icsCreateAndSave();
	print('课程表已保存至脚本目录下的 class.ics 中，你现在可以导入了：）')
	result = {
		"link": "/output/class_" + requestid +".ics",
		"obtained_class": obtainedClass,
		"reminder": reminder
	}
	with open (DEPLOY_PATH + 'log/success.log', 'a+', encoding='utf-8') as f:
		f.write(Utils.getCurrentDateTime() + ',' + requestid + ',' + session.get('realname') + ',' + reminder + ',' + str(obtainedClass)+'\n')
		f.close()
	return result


def save(string):
	f = open(DEPLOY_PATH + "static/output/class_" + requestid + ".ics", 'wb+')
	f.write(string.encode("utf-8"))
	f.close()


def icsCreateAndSave():
	icsString = "BEGIN:VCALENDAR\nMETHOD:PUBLISH\nVERSION:2.0\nX-WR-CALNAME:课程表\nPRODID:-//Apple Inc.//Mac OS X 10.12//EN\nX-APPLE-CALENDAR-COLOR:#FC4208\nX-WR-TIMEZONE:Asia/Shanghai\nCALSCALE:GREGORIAN\nBEGIN:VTIMEZONE\nTZID:Asia/Shanghai\nBEGIN:STANDARD\nTZOFFSETFROM:+0900\nRRULE:FREQ=YEARLY;UNTIL=19910914T150000Z;BYMONTH=9;BYDAY=3SU\nDTSTART:19890917T000000\nTZNAME:GMT+8\nTZOFFSETTO:+0800\nEND:STANDARD\nBEGIN:DAYLIGHT\nTZOFFSETFROM:+0800\nDTSTART:19910414T000000\nTZNAME:GMT+8\nTZOFFSETTO:+0900\nRDATE:19910414T000000\nEND:DAYLIGHT\nEND:VTIMEZONE\n"
	global classTimeList, DONE_ALARMUID, DONE_UnitUID
	eventString = ""
	for classInfo in classInfoList:
		i = int(classInfo["classTime"] - 1)
		# className = classInfo["className"]+"|"+classTimeList[i]["name"]+"|"+classInfo["classroom"]
		className = classInfo["className"]
		obtainedClass.append(className)
		endTime = classTimeList[i]["endTime"]
		startTime = classTimeList[i]["startTime"]
		index = 0
		for date in classInfo["date"]:
			eventString = eventString + "BEGIN:VEVENT\nCREATED:" + classInfo["CREATED"]
			eventString = eventString + "\nUID:" + classInfo["UID"][index]
			eventString = eventString + "\nDTEND;TZID=Asia/Shanghai:" + date + "T" + endTime
			eventString = eventString + "00\nTRANSP:OPAQUE\nX-APPLE-TRAVEL-ADVISORY-BEHAVIOR:AUTOMATIC\nSUMMARY:" + className
			eventString = eventString + "\nDTSTART;TZID=Asia/Shanghai:" + date + "T" + startTime + "00"
			eventString = eventString + "\nDTSTAMP:" + DONE_CreatedTime
			eventString = eventString + "\nLOCATION:" + classInfo["classroom"]
			eventString = eventString + "\nSEQUENCE:0\nBEGIN:VALARM\nX-WR-ALARMUID:" + DONE_ALARMUID
			eventString = eventString + "\nUID:" + DONE_UnitUID
			eventString = eventString + "\nTRIGGER:" + DONE_reminder
			eventString = eventString + "\nDESCRIPTION:事件提醒\nACTION:DISPLAY\nEND:VALARM\nEND:VEVENT\n"
			index += 1
	icsString = icsString + eventString + "END:VCALENDAR"
	save(icsString)
	print("Now running: icsCreateAndSave()")


def classInfoHandle():
	global classInfoList
	global DONE_firstWeekDate
	i = 0

	for classInfo in classInfoList:
		# 具体日期计算出来

		startWeek = json.dumps(classInfo["week"]["startWeek"])
		endWeek = json.dumps(classInfo["week"]["endWeek"])
		weekday = float(json.dumps(classInfo["weekday"]))
		week = float(json.dumps(classInfo["weeks"]))
		dateLength = float((int(startWeek) - 1) * 7)
		startDate = datetime.datetime.fromtimestamp(int(time.mktime(DONE_firstWeekDate))) + datetime.timedelta(
			days=dateLength + weekday - 1)
		string = startDate.strftime('%Y%m%d')

		dateLength = float((int(endWeek) - 2) * 7)
		endDate = datetime.datetime.fromtimestamp(int(time.mktime(DONE_firstWeekDate))) + datetime.timedelta(
			days=dateLength + weekday - 1)

		date = startDate
		dateList = []
		if (week == 3): dateList.append(string)
		if ((week == 2) and (int(startWeek) % 2 == 0)): dateList.append(string)
		if ((week == 1) and (int(startWeek) % 2 == 1)): dateList.append(string)
		i = NO
		w = int(startWeek) + 1
		while (i):
			date = date + datetime.timedelta(days=7.0)
			if (date > endDate):
				i = YES
			if (week == 3):
				string = date.strftime('%Y%m%d')
				dateList.append(string)
			if ((week == 1) and (w % 2 == 1)):
				string = date.strftime('%Y%m%d')
				dateList.append(string)
			if ((week == 2) and (w % 2 == 0)):
				string = date.strftime('%Y%m%d')
				dateList.append(string)
			w = w + 1
		classInfo["date"] = dateList
		# 设置 UID
		global DONE_CreatedTime, DONE_EventUID
		CreateTime()
		classInfo["CREATED"] = DONE_CreatedTime
		classInfo["DTSTAMP"] = DONE_CreatedTime
		UID_List = []
		for date in dateList:
			UID_List.append(UID_Create())
		classInfo["UID"] = UID_List
	print("Now running: classInfoHandle()")


def UID_Create():
	return random_str(20) + "&xiejiadong.com"


def CreateTime():
	# 生成 CREATED
	global DONE_CreatedTime
	date = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
	DONE_CreatedTime = date + "Z"
	# 生成 UID
	# global DONE_EventUID
	# DONE_EventUID = random_str(20) + "&xiejiadong.com"

	print("Now running: CreateTime()")


def uniteSetting():
	#
	global DONE_ALARMUID
	DONE_ALARMUID = random_str(30) + "&xiejiadong.com"
	#
	global DONE_UnitUID
	DONE_UnitUID = random_str(20) + "&xiejiadong.com"
	print("Now running: uniteSetting()")


def setClassTime():
	data = []
	with open(DEPLOY_PATH + 'config/conf_classTime.json', 'r', encoding='utf-8') as f:
		data = json.load(f)
	global classTimeList
	classTimeList = data["classTime"]
	print("Now running: setclassTime()")


def setClassInfo():
	data = []
	with open(DEPLOY_PATH + 'static/temp/json/classInfo_'+requestid+'.json', 'r', encoding='utf-8') as f:
		data = json.load(f)
	global classInfoList
	classInfoList = data["classInfo"]
	print("Now running: setClassInfo()")


def setFirstWeekDate(firstWeekDate):
	global DONE_firstWeekDate
	DONE_firstWeekDate = time.strptime(firstWeekDate, '%Y%m%d')
	print("Now running: setFirstWeekDate():", DONE_firstWeekDate)


def setReminder(reminder):
	global DONE_reminder
	# global reminderList
	# DONE_reminder = reminderList[int(reminder) - 1]
	if(reminder == "0"):
		DONE_reminder = "NULL"
	else:
		DONE_reminder = "-PT" + reminder + "M"
	print("setReminder", reminder)

def random_str(randomlength):
	str = ''
	chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
	length = len(chars) - 1
	random = Random()
	for i in range(randomlength):
		str += chars[random.randint(0, length)]
	return str
