import requests
import pytesseract
import config.CONST as CONST
from config.CONST import *
from PIL import Image
from lxml import etree
from api.utils import RSA
from api.utils import Utils
from flask import session
import server

def logIn(username, password):
    requestid = username + "_" + Utils.getFormattedDateTime();
    session["requestid"] = requestid
    s = requests.session()
    r = s.get(CONST.PORTAL_URL, headers=CONST.headers)
    imgraw = s.get(CONST.CAPTACHA_URL)
    with open(DEPLOY_PATH + 'static/temp/captacha/captacha_' + requestid + '.jpg', 'wb+') as f:
        f.write(imgraw.content)
    img = Image.open(DEPLOY_PATH + 'static/temp/captacha/captacha_' + requestid + '.jpg')
    code = pytesseract.image_to_string(img)
    print('pytesseract.image_to_string() result:', code)
    postData = {
        'code':code,
        'rsa': RSA.GetRSA(username,password),
        'ul': len(username),
        'pl': len(password),
        'lt': 'LT-211100-OG7kcGcBAxSpyGub3FC9LU6BtINhGg-cas',
        'execution': 'e1s1',
        '_eventId': 'submit'
    }
    r = s.post(CONST.PORTAL_URL, data=postData)
    elements = etree.HTML(r.content)
    errors = elements.xpath('//*[@id="errormsg"]')
    if len(errors) == 0:
        realName = elements.xpath('//a[contains(@title, "查看登录记录")]/font/text()')[0]
        print('Login Success - ', realName, 'Session ID:', requestid)
        # server.sessions[requestid] = s.cookies
        session["usercookie"] = requests.utils.dict_from_cookiejar(s.cookies)
        # session["usercookie"] = s.cookies
        session["uid"] = username
        session["realname"] = realName
        return 0
    elif elements.xpath('//*[@id="errormsg"]/text()')[0] == "验证码有误":
        return -1
    elif elements.xpath('//*[@id="errormsg"]/text()')[0] == "用户名密码错误":
        return -2
    else:
        return -3
    cookie = ""