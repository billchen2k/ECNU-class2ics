# coding: utf-8
#!/usr/bin/python

import sys
import json
import xlrd

__author__ = 'Xiejiadong'
__site__ = 'xiejiadong.com'

# 引用自 ~~官方文档~~ 的特别注意：
# className：课程名称，老师信息也可以一起写在这里
# startWeek：课程起始周数
# endWeek：课程结束周数
# weekday：课程在星期几，比如输入1代表周一，7代表周日
# week：代表单双周。输入1代表单周的课，2代表双周的课，3代表每周都有的课
# classTime：课程的时间，与步骤1定义对应，比如输入1代表“第1、2节课”，4代表“第5、6、7节课”
# classroom：上课所在的教室

# 指定信息在 xls 表格内的列数
_colOfClassName = 0
_colOfStartWeek = 1
_colOfEndWeek = 2
_colOfWeekday = 3
_colOfWeeks = 4
_colOfClassTime = 5
_colOfClassroom = 6

def main():
	# 读取 excel 文件
	data = xlrd.open_workbook(sys.path[0] + '/config/classInfo.xlsx')
	table = data.sheets()[0]
	# print table.cell(1,0).value
	# 基础信息
	numOfRow = table.nrows  #获取行数,即课程数
	numOfCol = table.ncols  #获取列数,即信息量
	headStr = '{\n"classInfo":[\n'
	tailStr = ']\n}'
	classInfoStr = ''
	classInfoArray = []
	# 信息列表
	# lengthOfList = numOfRow-1
	classNameList = []
	startWeekList = []
	endWeekList = []
	weekdayList = []
	weeksList = []
	classTimeList = []
	classroomList = []

	# 确定配置内容
	info = "\n欢迎使用课程表生成工具·Excel 解析器。\n这是你 Excel 列信息配置，请检查。\n\n如若有误，请自行编辑 excelReader 文件第 12～17 行\n\n"
	info += "ClassName: " + str(_colOfClassName) + "列\n"
	info += "StartWeek: " + str(_colOfStartWeek) + "列\n"
	info += "EndWeek: " + str(_colOfEndWeek) + "列\n"
	info += "Weekday: " + str(_colOfWeekday) + "列\n"
	info += "Weeks: " + str(_colOfWeeks) + "列\n"
	info += "ClassTime: " + str(_colOfClassTime) + "列\n"
	info += "Classroom: " + str(_colOfClassroom) + "列\n"
	print (info)
	# info += "输入 0 继续，输入 1 退出："
	option = input("输入 y 继续，输入其他内容退出：")
	if option != "y":
		sys.exit(0)
	

	# 开始操作
	# 将信息加载到列表
	i = 1
	while i < numOfRow :
		index = i-1

		classNameList.append(((table.cell(i, _colOfClassName).value)))
		startWeekList.append(str(int((table.cell(i, _colOfStartWeek).value))))
		endWeekList.append(str(int((table.cell(i, _colOfEndWeek).value))))
		weekdayList.append(str(int((table.cell(i, _colOfWeekday).value))))
		weeksList.append(str(int((table.cell(i, _colOfWeeks).value))))
		classTimeList.append(str(int((table.cell(i, _colOfClassTime).value))))
		classroomList.append(str(((table.cell(i, _colOfClassroom).value))))
		
		i += 1
	i = 0
	itemHeadStr = '{\n'
	itemTailStr = '\n}'

	classInfoStr += headStr
	for className in classNameList:
		itemClassInfoStr = ""
		itemClassInfoStr  = itemHeadStr + '"className":"' + className + '",'
		itemClassInfoStr += '"week":{\n"startWeek":' + startWeekList[i] + ',\n'
		itemClassInfoStr += '"endWeek":' + endWeekList[i] + '\n},\n'
		itemClassInfoStr += '"weekday":' + weekdayList[i] + ',\n'
		itemClassInfoStr += '"weeks":' + weeksList[i] + ',\n'
		itemClassInfoStr += '"classTime":' + classTimeList[i] + ',\n'
		itemClassInfoStr += '"classroom":"' + classroomList[i] + '"\n'
		itemClassInfoStr += itemTailStr
		classInfoStr += itemClassInfoStr
		if i!=len(classNameList)-1 :
			classInfoStr += ","
		i += 1
	classInfoStr += tailStr
	# print classInfoStr
	with open(sys.path[0] + '/conf_classInfo.json','w') as f:

		f.write(classInfoStr)
		f.close()
	print("\nALL DONE !")

main()
