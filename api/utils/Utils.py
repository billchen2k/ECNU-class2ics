import time
import json
from flask import session, Response

def getCurrentDateTime():
	return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def getFormattedDateTime():
	return time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())

def getResult(code, data, message = ""):
	result = {
		"success": True if code == 200 else False,
		"code": code,
		"message": message,
		"data": data,
		"requestid": session.get("requestid")
	}
	return result

def makeJsonResponse(code, data, message = ""):
	result = {
		"success": True if code == 200 else False,
		"code": code,
		"message": message,
		"data": data,
		"requestid": session.get("requestid")
	}
	resultJson = json.dumps(result, ensure_ascii=False)
	response = Response(resultJson, content_type="application/json; charset=utf-8")
	return response