# 依赖库 pycrypto ，request，pillow
import requests
import lxml
import os
import sys
import json
from PIL import Image
import sys
import getpass
from lxml import etree

loginurl = 'https://portal1.ecnu.edu.cn/cas/login?service=http%3A%2F%2Fapplicationnewjw.ecnu.edu.cn%2Feams%2Fhome.action%3Bjs'
headers = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
	'Refer': 'https://portal1.ecnu.edu.cn/cas/login?service=http%3A%2F%2Fapplicationnewjw.ecnu.edu.cn%2Feams%2Fhome.action%3Bjs'}
captachaurl = 'https://portal1.ecnu.edu.cn/cas/code'
s = requests.session()
r = s.get(loginurl)
username = input('请输入你的公共数据用户名（学号）：')
password = getpass.getpass('请输入你的公共数据库密码（直接输入即可，已关闭输入回显）：')
imgraw = s.post(captachaurl)
with open(sys.path[0] + '/temp.jpg', 'wb+') as f:
	f.write(imgraw.content)
img = Image.open(sys.path[0] + '/temp.jpg')
img.show()
captacha = input('请输入验证码：')
postData = {
	'code': captacha,
	'rsa': '6FFFB9BB7177A0615B393792498927EF49C2A150A80679A87CA1D42715D08E83F8DE3016E17697F062E5D4650E20E1F6EAEC2A3C6B17D765D7DEE981A1E0CA4D92CBE6DDFEE4C09833D7D154AAA231106EE85EC3117557AC07E33D3A895757F718309451A5EC1CAC206CD9C26FECCBE0EA47ACA0FD8BA8C08AB35967D5AA0BA7',
	'ul': '11',
	'pl': '9',
	'lt': 'LT-211100-OG7kcGcBAxSpyGub3FC9LU6BtINhGg-cas',
	'execution': 'e1s2',
	'_eventId': 'submit'
}	
if __name__ == '__main__':
	print ('请直接执行运行目录下的main.py。')
