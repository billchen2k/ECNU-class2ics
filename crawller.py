##############################################
# 依赖库 pycrypto ，request，pillow，pyexecjs  #
##############################################

import requests
import lxml
import re
import sys
import json
import sys
import getpass
import execjs
from PIL import Image
from lxml import etree

mainurl = 'https://portal1.ecnu.edu.cn/cas/login?service=http%3A%2F%2Fapplicationnewjw.ecnu.edu.cn%2Feams%2Fhome.action'
tabelurl = 'http://applicationnewjw.ecnu.edu.cn/eams/courseTableForStd!courseTable.action'
headers = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
	'Refer': 'https://portal1.ecnu.edu.cn/cas/login?service=http%3A%2F%2Fapplicationnewjw.ecnu.edu.cn%2Feams%2Fhome.action%3Bjs'}
captachaurl = 'https://portal1.ecnu.edu.cn/cas/code'
s = requests.session()

	

def GetCode():
	r = s.get(mainurl, headers=headers)
	imgraw = s.get(captachaurl)
	with open(sys.path[0] + '/data/temp.jpg', 'wb+') as f:
		f.write(imgraw.content)
	img = Image.open(sys.path[0] + '/data/temp.jpg')
	img.show()
	captacha = input('请输入验证码：')
	return captacha

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
	rsa = desJS.call('strEnc', username + password, '1', '2', '3')
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
	code=GetCode()
	postData = {
		'code': code,
		'rsa': GetRSA(username, password),
		'ul': len(username),
		'pl': len(password),
		'lt': 'LT-211100-OG7kcGcBAxSpyGub3FC9LU6BtINhGg-cas',
		'execution': 'e1s1',
		'_eventId': 'submit'
	}
	r = s.post(mainurl, data=postData)
	elements = etree.HTML(r.content)
	errors = elements.xpath('//*[@id="errormsg"]')
	if len(errors) == 0:
		realName = elements.xpath('//a[contains(@title, "查看登录记录")]/font/text()')[0]
		print('登陆成功:', realName)
		return 0
	elif elements.xpath('//*[@id="errormsg"]/text()')[0] == "验证码有误":
		return 1
	elif elements.xpath('//*[@id="errormsg"]/text()')[0] == "用户名密码错误":
		return 2
	else:
		return 3

def TableSolver():
	tablePostData = {'ignoreHead': 1,
                  'setting.kind': 'std',
                  'startWeek': 1,
                  'semester.id': 737,
                  'ids': 567403}
	# semester.id：2018-2019学年度上学期为737，每向前/向后一个学期就增加/减少32.
	semesterIDs = [705, 737, 769]
	r = s.post(tabelurl, data=tablePostData)
	elements = etree.HTML(r.content)
	# 提取出具有课程的数据
	raws = elements.xpath('//*[@language="JavaScript"][3]/text()')[0]
	rule = re.compile('new TaskActivity\((.*?)\);', re.S)
	classes = re.findall(rule, raws)
	print(classes)
	processedClass = []
	for one in classes:
		temp = one.split(',')
		for i in range(len(temp)):
			temp[i] = temp[i].replace('"', '')
		processedClass.append(temp)
	
	pass

def DumpJson():
	pass
def main():
	print('这个脚本可以直接登陆网站，爬取课程表，并生成一个 xjd 标准的 json 课程表文件。')
	print('另外由于 Policy 原因，你可能时常需要准备好学校的 VPN.')
	print('正在初始化...')
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
				sys.exit()
	TableSolver()

if __name__ == '__main__':
	main()
