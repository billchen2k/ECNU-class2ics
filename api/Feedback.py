import json

import requests
from flask import session

from api.utils import Utils
from config.CONST import *
import urllib.parse

# 和反馈有关的文件


def Send(msg, contact, withFile):
	global RECIEVERS
	requestid = session.get("requestid") if session.get("requestid") is not None else "N/A"
	realname = session.get("realname") if session.get("realname") is not None else "N/A"
	if (msg is None):
		msg = ""
	if (contact is None or contact == ''):
		contact = "匿名用户"
	if (withFile):
		contact = contact + " 📎"
	for one in RECIEVERS:
		text = "`<ECNU-class2ics>`\n收到来自 *"+contact+"* 的反馈：\n\n"+msg+"\n\n`requestid: "+ requestid + "`"
		postUrl = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage?parse_mode=markdown&chat_id=" + one + "&text=" + text;
		result = requests.post(postUrl)
		print(result.content)
	with open (DEPLOY_PATH + 'log/feedback.log', 'a+', encoding='utf-8') as f:
		f.write(Utils.getCurrentDateTime() + ',' + requestid + ',' + realname + ',' + contact + ','+ msg+ '\n')
		f.close()
	return json.loads(result.content, encoding="unicode")

def SendResult(result):
	global RECIEVERS
	requestid = session.get("requestid") if session.get("requestid") is not None else "N/A"
	for one in RECIEVERS:
		text = "`<ECNU-class2ics>`\n *"+ session.get("realname") +"* 导出了一份课程表。包含以下内容：\n\n"
		text = text + str(result["obtained_class"]) + ' (Reminder = ' + result["reminder"] + ' min)'
		text = text +"\n\n`requestid: "+ requestid + "`"
		postUrl = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage?parse_mode=markdown&chat_id=" + one + "&text=" + text;
		result = requests.post(postUrl)
		pass

def SendPhoto(filePath):
	photoURL = "http://" + SERVER_ADDRESS + filePath
	requestid = session.get("requestid") if session.get("requestid") is not None else "N/A"
	global RECIEVERS
	for one in RECIEVERS:
		caption = "`<ECNU-class2ics>`\n`requestid: "+ requestid + "` 📎"
		postUrl = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendPhoto?parse_mode=markdown&chat_id=" + one + "&photo=" + photoURL + "&caption=" + caption;
		print(postUrl)
		result = requests.post(postUrl)
		print(result.content)