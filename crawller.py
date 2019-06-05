###################################
# 依赖库 lxml ，requests，pyexecjs  #
###################################

import requests
import lxml
import re
import sys
import json
import sys
import getpass
import execjs
import platform
from lxml import etree

mainurl = 'https://portal1.ecnu.edu.cn/cas/login?service=http%3A%2F%2Fapplicationnewjw.ecnu.edu.cn%2Feams%2Fhome.action'
tabelurl = 'http://applicationnewjw.ecnu.edu.cn/eams/courseTableForStd!courseTable.action'
idsurl = 'http://applicationnewjw.ecnu.edu.cn/eams/courseTableForStd!index.action'
headers = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
	'Refer': 'https://portal1.ecnu.edu.cn/cas/login?service=http%3A%2F%2Fapplicationnewjw.ecnu.edu.cn%2Feams%2Fhome.action%3Bjs'}
captachaurl = 'https://portal1.ecnu.edu.cn/cas/code'
s = requests.session()
ids = 0
	

def GetCode():
	"发送一次新的 get 请求并获取验证码，让用户填写。"
	print('正在获取验证码...')
	r = s.get(mainurl, headers=headers)
	imgraw = s.get(captachaurl)
	with open(sys.path[0] + '/data/temp.jpg', 'wb+') as f:
		f.write(imgraw.content)
	OpenFile(sys.path[0] + '/data/temp.jpg')
	captacha = input('请输入验证码：')
	return captacha

def OpenFile(filedir):
	if (platform.system() == 'Windows'):
		import os
		os.startfile(filedir)
	elif (platform.system() == 'Darwin'):
		import subprocess
		subprocess.call(["open", filedir])
	elif (platform.system() == 'Linux'):
		import subprocess
		subprocess.call(["xdg-open", filedir])
	else:
		from PIL import Image
		img = Image.open(filedir)
		img.show()


def GetRSA(username, password):
	# 获取 des.js 里的内容
	with open(sys.path[0] + '/data/des.js') as f:
		line = f.readline()
		jsstr = ''
		while line:
			jsstr = jsstr + line
			line = f.readline()
	desJS = execjs.compile(jsstr)
	# 调用 strEnc 函数实现 rsa 加密
	try:
		rsa = desJS.call('strEnc', username + password, '1', '2', '3')
	except:
		ErrorExit(info='GetRSA()')
	return rsa

def LoginLooper(username='', password='', ifEnterPassword=False):
	"""
	返回值：
	0 - 成功登陆
	1 - 验证码错误
	2 - 密码错误
	3 - 未知错误
	"""
	if (ifEnterPassword == True):
		username = input('请输入你的公共数据用户名（学号）：')
		password = getpass.getpass('请输入你的公共数据库密码（直接输入即可，已关闭输入回显）：')
	code = GetCode()
	postData = {
		'code': code,
		'rsa': GetRSA(username, password),
		'ul': len(username),
		'pl': len(password),
		'lt': 'LT-211100-OG7kcGcBAxSpyGub3FC9LU6BtINhGg-cas',
		'execution': 'e1s1',
		'_eventId': 'submit'
	}
	print('正在尝试登录...')
	r = s.post(mainurl, data=postData)
	elements = etree.HTML(r.content)
	errors = elements.xpath('//*[@id="errormsg"]')
	if len(errors) == 0:
		realName = elements.xpath('//a[contains(@title, "查看登录记录")]/font/text()')[0]
		print('登录成功:', realName)
		return 0
	elif elements.xpath('//*[@id="errormsg"]/text()')[0] == "验证码有误":
		return 1
	elif elements.xpath('//*[@id="errormsg"]/text()')[0] == "用户名密码错误":
		return 2
	else:
		return 3

def DefineIDS():
	"获取用户标识 ids，改变全局变量"
	global ids
	r = s.get(idsurl)
	src = r.text
	rule = re.compile('bg\.form\.addInput\(form,"ids","(.*?)"\);', re.S)
	ids = re.findall(rule, src)
	if (len(ids) == 0):
		ErrorExit(info='DefineIDS()')
	print('ids:',ids[0])
	return ids[0]
	
def GetSemesterID():
	return 769

	"semester.id: 2018-2019学年度上学期为737，每向前/向后一个学期就增加/减少32."
	print('正在获取 semester.id...')
	web = requests.get('https://billc.io/conf-ecnu-class2ics/')
	elements = etree.HTML(web.content)
	id = elements.xpath('//strong/text()')
	if (len(id) == 0):
		ErrorExit('GetSemesterID()')
	print('semster.id:', id[0])
	return id[0]

def ErrorExit(info):
	print('在' + info + '出现异常，无法继续。')
	print('请删除这个东西，去干点其他让你快乐的事情。')
	sys.exit()

def TableSolver():
	tablePostData = {'ignoreHead': 1,
                  'setting.kind': 'std',
                  'startWeek': 1,
                  'semester.id': GetSemesterID(),
                  'ids': ids}
	semesterIDs = [705, 737, 769]
	print('正在连接数据库...')
	r = s.post(tabelurl, data=tablePostData)
	elements = etree.HTML(r.content)
	# 提取出具有课程的数据
	raws = elements.xpath('//*[@language="JavaScript"][3]/text()')
	if (len(raws) == 0):
		ErrorExit('TableSolver()')
	# 使用新的正则表达式匹配每一节课所在的时间
	rawClasses = re.findall('(.\*unitCount\+\d+)|new TaskActivity\((.*?),null', raws[0])
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
	# 	[教师名字，课程名，上课地点，起始周数，结束周数，单双周类型:1单周2双周3每周，星期, [每天要上的节数 n1, n2, ...],
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
	return processed

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
	pass

	return weekData



def DumpJson(classList):
	classInfo = {'classInfo': []}
	with open(sys.path[0] + '/conf_classTime.json', 'r') as f:
		classTime = json.load(f)
	classTimes = []
	# 获取 conf_classTime.json 中的配置文件，并和 classList 的配置匹配
	# 由于 classList 中的课程节数从 0 开始，所以需要从 json 中 - 1 匹配
	for oneTime in classTime['classTime']:
		temp = re.findall(r"\d+\.?\d*",oneTime['name'])
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
	with open(sys.path[0] + '/conf_classInfo.json', 'w+', encoding='utf8') as f:
		json.dump(classInfo, f, indent=4, ensure_ascii=False)
	pass

def Instruct():
	print("""
Welcome!
-----------------------------------------------------
该脚本可以登陆华东师范大学公共数据库，并根据课表数据生成
xjd1.0 标准的 json 课程表文件。
另外由于 Policy 原因，你可能时常需要准备好学校的 VPN.
-----------------------------------------------------
正在初始化...""")

def main():
	Instruct()
	username = input('请输入你的公共数据用户名（学号）：')
	password = getpass.getpass('请输入你的公共数据库密码（直接输入即可，已关闭输入回显）：')
	feedback = LoginLooper(username, password, ifEnterPassword=False)
	while feedback != 0:
		if feedback == 1:
			print('验证码错误，请重试。')
			feedback = LoginLooper(username, password,ifEnterPassword=False)
		elif feedback == 2:
			print('用户名或密码错误，请重试。')
			feedback = LoginLooper(ifEnterPassword=True)
		else:
			print('未知错误，输入 0 来继续重试，输入其他任何内容退出。')
			c = input()
			if (c == '0'):
				feedback = LoginLooper(ifEnterPassword=True)
			else:
				ErrorExit(info='LoginLooper()')
	print('正在获取用户 ids...')
	DefineIDS()
	print('正在公共数据库上获取课程数据...')
	classList = TableSolver()
	print('正在处理为 xjd 标准 json 文件...')
	DumpJson(classList)
	print('\n处理完成，课表信息已保存至 conf_classInfo.json 中。')
	print('接下来请运行 main.py 生成 ics。')


if __name__ == '__main__':
	main()
