# -*- coding: UTF-8 -*-

import os

from api import LogIn
from api import GetClassJson
from api import GetClassCSV
from api import Feedback
from api.utils import Utils
from api.utils.Utils import getResult
from api.utils.Utils import makeJsonResponse
from config.CONST import *
from flask import session
from werkzeug.utils import secure_filename

from flask import Flask, redirect, render_template, request
from flask import *
app = Flask(__name__, static_url_path="", static_folder="static")


@app.route('/')
def apiIndex():
	return redirect("/index.html")

# 参数用户名和密码
@app.route('/logIn', methods=['POST', 'GET'])
def userLogin():
	username = request.args.get('username')
	password = request.args.get('password')
	resultDic = {
		-1: "验证码识别失败，请重试",
		-2: "用户名或密码错误",
		-3:"未知错误",
		0:"登录成功"
	}
	loginResult = LogIn.logIn(username, password)
	return makeJsonResponse(CODE_SUCCESS if loginResult == 0 else CODE_ERROR,
	                         {
		                         "realname":  session.get("realname")
	                         },
	                         resultDic[loginResult])

# 参数 semester ：5位数，前4位为学年的开头年份，第5位为学期代码：[1] 第一学期 [2] 第二学期 [3] 暑假小学期
@app.route('/getClass', methods=['POST', 'GET'])
def getClassJson():
	requestid = session.get("requestid")
	if(requestid is None):
		return makeJsonResponse(CODE_ERROR, "", "User not logined.")
	semester = request.args.get('semester')
	classJson = GetClassJson.getClass(requestid, semester)
	if classJson == -1:
		return makeJsonResponse(CODE_ERROR, "", "Session expired.")
	return makeJsonResponse(CODE_SUCCESS, classJson)


@app.route('/getCSV', methods=['POST', 'GET'])
def getClassCSV():
	requestid = session.get("requestid")
	if(requestid is None):
		return makeJsonResponse(CODE_ERROR, "", "User not logined.")
	if(not os.path.isfile(DEPLOY_PATH + '/static/temp/json/classInfo_' + requestid + '.json')):
		return makeJsonResponse(CODE_ERROR, "", "You haven'r run /getClass yet.")
	# 配置学期参数，学期格式同 getClass
	semester = request.args.get('semester')
	# 提醒配置参数
	# 以分钟数为单位，参数为几则提前多少分钟提醒， 为 0 则不提醒
	reminder = request.args.get('reminder')
	csvResult = GetClassCSV.GetClassCSV(semester, reminder)
	Feedback.SendResult(csvResult)
	return makeJsonResponse(CODE_SUCCESS, csvResult)

@app.route('/sendFeedback', methods=['POST'])
def sendFeedback():
	files = request.files.getlist("file")
	message = request.form['message']
	contact = request.form['contact']
	requestid = session.get("requestid")
	if requestid is None:
		requestid = Utils.getFormattedDateTime();
	withFile = False
	if(len(files) > 0):
		withFile = True
		for one in files:
			one.save(os.path.join(DEPLOY_PATH + 'static/temp/upload', requestid + secure_filename(one.filename)))
		filePath = '/temp/upload/' + requestid + '.' + secure_filename(one.filename)
		Feedback.SendPhoto(filePath)
	feedbackResult = Feedback.Send(message, contact, withFile)
	if not(feedbackResult["ok"] == True):
		return makeJsonResponse(CODE_ERROR, feedbackResult)
	return makeJsonResponse(CODE_SUCCESS, feedbackResult)

if __name__ == '__main__':
	app.config['JSON_AS_ASCII'] = False
	app.config['SECRET_KEY'] = os.urandom(24)
	print(DEPLOY_PATH)
	app.run(host='0.0.0.0')
