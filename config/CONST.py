# Consts here.
# Do not modifiy.
import os

FIRST_WEEK_DATE = {
	"20181": "20180910",
	"20182": "20190218",
	"20183": "20190701",
	"20191": "20190902",
	"20192": "20200309",
	"20193": "20200706",
	"20201": "20200914"
}

SERVER_ADDRESS = "class2ics.billc.io"
DEPLOY_PATH = os.path.realpath(os.path.dirname(__file__))[:-6]

# 反馈相关

# token 未提交在 Git 上，反馈功能会无法使用。
BOT_TOKEN = ""
RECIEVERS = ["886018984"]
#RECIEVERS LIST: Ho "38724011"

CODE_SUCCESS = 200
CODE_ERROR = 500

MAIN_URL = "http://idc.ecnu.edu.cn"
PORTAL_URL = 'https://portal1.ecnu.edu.cn/cas/login?service=http%3A%2F%2Fapplicationnewjw.ecnu.edu.cn%2Feams%2Fhome.action'
CAPTACHA_URL = 'https://portal1.ecnu.edu.cn/cas/code'
DETAIL_URL = 'http://applicationnewjw.ecnu.edu.cn/eams/stdDetail.action'
IDS_URL = 'http://applicationnewjw.ecnu.edu.cn/eams/courseTableForStd!index.action'
TABLE_URL = 'http://applicationnewjw.ecnu.edu.cn/eams/courseTableForStd!courseTable.action'
GRADES_URL = 'http://applicationnewjw.ecnu.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action?projectType=MAJOR'
BASE_SMID = 769
headers = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
	'Refer': 'https://portaal1.ecnu.edu.cn/cas/login?service=http%3A%2F%2Fapplicationnewjw.ecnu.edu.cn%2Feams%2Fhome.action%3Bjs'}