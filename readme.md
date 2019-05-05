# ECNU-class2ics

## What's this

ics 是国际通用的最为流行的日历文件之一，受到几乎所有日历软件的支持。对于华东师范大学的学生，这个程序会登陆华东师范大学公共数据库，获取你的课程表，并根据指定的日期和提醒策略，生成一个可以导入到各个日历软件中的 ics 文件。对于其他高校的学生，可以手动输入信息。

## Why we made this

- 使用日历软件管理课程表可以让你不再把丑陋的课程表设置成桌面壁纸。
- 每节课上课前都会收到关于下一节课的提醒。（美观程度取决于系统和日历软件）
- 对于 iOS 和 macOS，系统会自动为你查找上课地点并接入苹果地图。
- 不想每学期都手动添加。~~（懒）~~
  
## How to use this

需 Python 3 环境，依赖以下运行库：

**lxml, request, pillow, pyexecjs**

如果运行的时候还缺了什么，请 pip 上。

对于华东师范大学的学生，请先后运行 crawller.py （用于获取课程 json）和 main.py （用于生成 ics 文件）。对于其他高校的学生，请先在`conf_classTime.json`中配置每节课的启示时间，然后手动填写`classinfo.xlsx`。具体操作可以参照文末的[官方文档]("http://xiejiadong.com/?p=419")。

最后生成的文件为同目录下的 class.ics。

## About this

Contributor|Website
---|---
Bill Chen|https://billc.io
Xiejiadong|http://xiejiadong.com/

> Old Doc:

Want to know how to make the timetable? 
http://xiejiadong.com/?p=419
