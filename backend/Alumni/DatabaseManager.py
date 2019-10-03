'''
处理数据库操作的函数集合

1：用户列表：存储用户除了教育信息外的信息
2：教育信息表：存储教育信息
3：历史记录表：存储历史记录
4：活动列表：存储活动信息
'''

from django.http import HttpResponse
from django.http import JsonResponse
from django.http import FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import numpy as np
from PIL import Image
from io import BytesIO
import random
import sqlite3
import sys
import os
import time
import configparser
import urllib.request
import base64
import json
import imageio
import scipy.misc as misc
import traceback

def TimeStringToTimeStamp(TimeString):
	'''
	描述：时间字符串转化为时间戳（秒）
	参数：时间字符串
	返回：时间戳（秒）（int）
	'''
	TimeArray = time.strptime(TimeString, "%Y-%m-%d %H:%M:%S")
	TimeStamp = int(time.mktime(TimeArray))
	return TimeStamp

def TimeStampToTimeString(TimeStamp):
	'''
	描述：时间戳（秒）转化为时间字符串
	参数：时间戳（秒）（int）
	返回：时间字符串
	'''
	TimeArray = time.localtime(TimeStamp) 
	TimeString = time.strftime("%Y-%m-%d %H:%M:%S", TimeArray)
	return TimeString

def GetCurrentTime():
	'''
	功能：获取当前时间戳
	参数：无
	返回：int类型，时间戳（秒）
    '''
	CurTime = int(time.time())
	return CurTime

def InitializeDatabase():
	'''
	描述：数据库初始化函数，负责初始化数据库和列表
	参数：无
	返回：成功True失败False
	'''
	Success = True

	#确定路径名和文件名
	TheName = "Database.db"

	#创建数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Create database fail.")
			Success = False

	#创建数据库表
	try:
		UserCursor = DataBase.cursor()
		UserCursor.execute(
			'''
			CREATE TABLE USER_LIST
			(OPENID 	CHAR(32) NOT NULL PRIMARY KEY UNIQUE,
			 NAME 	    CHAR(32)					NOT NULL,
			 GENDER     CHAR(32)                    NOT NULL,
			 FLAG       CHAR(32)                    NOT NULL					
			);
			'''
			)


		ActivityCursor = DataBase.cursor()
		ActivityCursor.execute(
			'''
			CREATE TABLE ACTIVITY_LIST
			(ID 	INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
			 NAME 	CHAR(32)					NOT NULL,
			 PLACE 	CHAR(64)  					NOT NULL,
			 START  CHAR(32)                	NOT NULL,
			 END    CHAR(32)                	NOT NULL,
			 MAXUSER INT						NOT NULL,
			 CURUSER INT						NOT NULL,
			 CREATOR CHAR(32)					NOT NULL,
			 FOREIGN KEY(CREATOR) REFERENCES USER_LIST(OPENID)
			);
			'''
			)


		EducationCursor = DataBase.cursor()
		EducationCursor.execute(
			'''
			CREATE TABLE EDUCATION_LIST
			(ID 			INTEGER		NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
			 TYPE 			CHAR(32)					NOT NULL,
			 STUDENTID      INT                    		NOT NULL,
			 START       	INT                    		NOT NULL,
			 END			INT							NOT NULL,
			 DEPARTMENTID	CHAR(32)					NOT NULL,
			 DEPARTMENT		CHAR(32)					NOT NULL,
			 CLASS			CHAR(32)					NOT NULL,
			 OPENID			CHAR(32)					NOT NULL,
			 FOREIGN KEY(OPENID) REFERENCES USER_LIST(OPENID)
			);
			'''
			)

		HistoryCursor = DataBase.cursor()
		#todo:付款，参加状态等记录
		HistoryCursor.execute(
			'''
			CREATE TABLE HISTORY_LIST
			(ID 		INTEGER  	NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
			 OPENID		CHAR(32)				NOT NULL,
			 ACTIVITYID	INTEGER						NOT NULL,
			 TIME		CHAR(32)				NOT NULL,			
			 FOREIGN KEY (OPENID) REFERENCES USER_LIST (OPENID),
			 FOREIGN KEY (ACTIVITYID) REFERENCES ACTIVITY_LIST (ID) 
			);
			'''
			)
		DataBase.commit()
		DataBase.close()

	except:
		Success = True
	return Success

def AddUser(OpenID, Name, Gender, Flag, Education):
	'''
	描述：添加一个用户到数据库	
	参数：用户OpenID，用户名，性别，状态，教育信息（字典数组）
	返回：成功True，失败False
	''' 
	Success = True

	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False

	#print(OpenID, Name, Gender, Flag, Education)

	#把教育信息以外的东西插入数据库
	if Success:
		try:
			Cursor = DataBase.cursor()
			Cursor.execute("INSERT INTO USER_LIST (OPENID, NAME, GENDER, FLAG)\
			VALUES (?,?,?,?)",(OpenID, Name, Gender, Flag))
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	#print(Success)
	#把教育信息插入数据库
	if Success:
		try:
			for item in Education:
				AddEducation(item, OpenID)
		except:
			Success = False
	return Success

def AddEducation(Education, OpenID):
	'''
	描述：添加一条教育信息到数据库
	参数：一条教育信息(字典),用户openid
	返回：成功True，失败False
	'''
	Success = True

	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False

	#把教育信息以外的东西插入数据库
	if Success:
		try:
			Cursor = DataBase.cursor()
			Cursor.execute("INSERT INTO EDUCATION_LIST (ID, TYPE, STUDENTID, START, END, DEPARTMENTID, DEPARTMENT, CLASS, OPENID)\
			VALUES (?,?,?,?,?,?,?,?,?)",(None, Education["type"], int(Education["id"]), int(Education["start"]),
			int(Education["end"]), Education["departmentId"], Education["department"], Education["class"], OpenID))
			DataBase.commit()
			DataBase.close()
		except:
			Success = False

def QueryUser(OpenID):
	'''
	描述：给定用户id，查询用户具体信息
	参数：用户id
	返回：一个字典，里面有用户id，名字，性别，状态，教育信息（数组）
	如果没有就返回空字典
	{openid:"6094852",name:"沈冠霖",gender:"MALE"，flag：”valid“，education：[{
	"type": "undergraduate | master | doctor",
	"id": 2019013569,
	"start": 2019,
	"end": 2023,
	"departmentId": "00210",
	"department": "清华大学软件学院",
	"class": "软73"
	},
	{
	"type": "master",
	"id": 2021013569,
	"start": 2023,
	"end": 2028,
	"departmentId": "00207",
	"department": "清华大学精仪系",
	"class": "软博211"
	}]}
	'''
	Success = True

	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
	
	#查询
	if Success:
		try:
			Cursor = DataBase.cursor()
			#Query = "SELECT * FROM ACTIVITY_LIST WHERE ID = ?",(Activity)
			#Params = [Activity]
			Info = []
			Cursor.execute("SELECT * FROM USER_LIST WHERE OPENID = ?",(OpenID,))
			Info = Cursor.fetchall()
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	#print(Info)
	#处理教育信息以外的数据并且返回
	Result = {}
	if Success:
		try:
			Result["openid"] = Info[0][0]
			Result["name"] = Info[0][1]
			Result["gender"] = Info[0][2]
			Result["flag"] = Info[0][3]
		except:
			Success = False
	#print(Result)
	#处理教育信息数据
	if Success:
		try:
			Result["education"] = QueryEducation(OpenID)
		except:
			Success = False
	return Result

def QueryEducation(OpenID):
	'''
	描述：查询用户的所有教育信息
	参数：用户openid
	返回：全部教育信息
	'''
	Success = True

	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
	
	#查询
	if Success:
		try:
			Cursor = DataBase.cursor()
			#Query = "SELECT * FROM ACTIVITY_LIST WHERE ID = ?",(Activity)
			#Params = [Activity]
			Info = []
			Cursor.execute("SELECT * FROM EDUCATION_LIST WHERE OPENID = ?",(OpenID,))
			Info = Cursor.fetchall()
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	#print(Info)
	#处理教育信息以外的数据并且返回
	Result = []
	if Success:
		try:
			for item in Info:
				OneResult = {}
				OneResult["type"] = item[1]
				OneResult["id"] = item[2]
				OneResult["start"] = item[3]
				OneResult["end"] = item[4]
				OneResult["departmentId"] = item[5]
				OneResult["department"] = item[6]
				OneResult["class"] = item[7]
				Result.append(OneResult)
		except:
			Success = False
	
	return Result

def ChangeUser(OpenID, Name, Gender, Flag, Education):
	'''
	描述：修改用户信息
	参数：Openid（必须有），用户的姓名，性别，状态，教育情况
	返回：成功{Success：True}，失败{Success：False，Reason：xxx}
	notfound：找不到用户，invalid：修改不合法返回：成功True，失败False
	'''
	Success = True
	#确定路径名和文件名
	TheName = "Database.db"
	Return = {}
	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
			Return["Reason"] = "other"
	
	#判断是否能找到这个用户
	if Success:
		try:
			Dictionary = {}
			Dictionary = QueryUser(OpenID)
			if Dictionary == False:
				Success = False
				Return["Reason"] = "notfound"
		except:
			Success = False
			Return["Reason"] = "notfound"

	print(Success)
	#修改数据库(教育信息之外)
	if Success:
		try:
			Cursor = DataBase.cursor()
			#Query = "UPDATE HISTORY_LIST SET CURUSER = ? WHERE ID = ?",(CurUser, Activity)
			#Params = [str(CurUser), Activity]
			Cursor.execute("UPDATE USER_LIST SET NAME = ?, GENDER = ?, FLAG = ? WHERE OPENID = ?",
			(Name, Gender, Flag, OpenID))

			DataBase.commit()
			DataBase.close()
		except:
			Success = False
			Return["Reason"] = "other"
	print(Success)
	#修改数据库（教育信息）
	if Success:
		try:
			if ChangeEducation(OpenID, Education) == False:
				Success = False
				Return["Reason"] = "other"
		except:
			Success = False
			Return["Reason"] = "other"
	Return["Success"] = Success
	return Return

def ChangeEducation(OpenID, Education):
	'''
	描述：修改用户教育信息
	参数：Openid（必须有），用户的新教育情况
	返回：成功True，失败False
	'''
	Success = True
	
	#先删除全部教育信息
	if Success:
		try:
			if DeleteUserEducation(OpenID) == False:
				Success = False
		except:
			Success = False

	#增加教育信息
	if Success:
		try:
			for item in Education:
				if AddEducation(item, OpenID) == False:
					Success = False
					break
		except:
			Success = False
	return Success

def DeleteUser(OpenID):
	'''
	描述：删除一个用户
	参数：Openid
	返回：成功True，失败False
	'''
	Success = True
	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
	
	#先删除相关信息
	DeleteUserEducation(OpenID)
	DeleteUserActivity(OpenID)
	DeleteUserHistory(OpenID)


	#修改数据库
	if Success:
		try:
			
			Cursor = DataBase.cursor()
			Cursor.execute("DELETE FROM USER_LIST WHERE OPENID = ?",(OpenID,))
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	return Success

def DeleteUserEducation(OpenID):
	'''
	描述：删除一个用户对应的全部教育信息
	参数：Openid
	返回：成功True，失败False
	'''
	Success = True
	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
	
	#修改数据库
	if Success:
		try:
			
			Cursor = DataBase.cursor()
			Cursor.execute("DELETE FROM EDUCATION_LIST WHERE OPENID = ?",(OpenID,))
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	return Success

def DeleteUserActivity(OpenID):
	'''
	描述：删除一个用户创建的全部活动
	参数：Openid
	返回：成功True，失败False
	'''
	Success = True
	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
	
	#修改数据库
	if Success:
		try:
			
			Cursor = DataBase.cursor()
			Cursor.execute("DELETE FROM ACTIVITY_LIST WHERE CREATOR = ?",(OpenID,))
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	return Success

def DeleteUserHistory(OpenID):
	'''
	描述：删除一个用户对应的全部历史记录
	参数：Openid
	返回：成功True，失败False
	'''
	Success = True
	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
	
	#修改数据库
	if Success:
		try:
			
			Cursor = DataBase.cursor()
			Cursor.execute("DELETE FROM HISTORY_LIST WHERE OPENID = ?",(OpenID,))
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	return Success

def AddActivity(Name, Place, Start, End, MaxUser, Creator):
	'''
	描述：添加一个活动到数据库	
	参数：活动名，活动地点，活动开始时间，活动结束时间，创建者
	返回：{Success:True/False,id:xxx}(失败:没有)
	'''
	Return = {}
	Success = True

	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False

	#把start，end转化为时间戳
	if Success:
		try:
			StartTime = TimeStringToTimeStamp(Start)
			EndTime = TimeStringToTimeStamp(End)
			CurTime = GetCurrentTime()
			if EndTime < CurTime:
				Success = False
		except:
			Success = False
	
	#print(Name, Place, StartTime, EndTime, MaxUser, Creator)

	#插入数据库
	if Success:
		try:
			Cursor = DataBase.cursor()
			Cursor.execute("INSERT INTO ACTIVITY_LIST (ID, NAME, PLACE, START, END, MAXUSER, CURUSER, CREATOR)\
			VALUES (?,?,?,?,?,?,?,?)",(None, Name, Place, StartTime, EndTime, MaxUser, 0, Creator))
			DataBase.commit()
			Cursor.execute("SELECT MAX(ID) FROM ACTIVITY_LIST")
			ID = Cursor.fetchall()
			Return["id"] = ID[0][0]
			DataBase.close()
		except:
			Success = False

	#让creator加入活动
	if Success:
		try:
			#print(int(Return["id"]))
			InsertUserActivity(Creator, int(Return["id"]))
			CurUserAddOne(int(Return["id"]))
		except:
			Success = False

	Return["Success"] = Success
	return Return

def CheckUserJoinedActivity(User, Activity):
	'''
	描述：给定用户id和活动id，判断用户是否参加了这个活动
	参数：用户id，活动id，都是str
	返回：已参加：True，没参加：False
	'''
	Success = True
	TheName = "Database.db"
	DataBase = sqlite3.connect(TheName)
	Cursor = DataBase.cursor()
	#Query = "SELECT * FROM HISTORY_LIST WHERE OPENID = ? AND ACTIVITYID = ?", (User, Activity)
	#Params = [User, Activity]
	Info = []
	Cursor.execute("SELECT * FROM HISTORY_LIST WHERE OPENID = ? AND ACTIVITYID = ?", (User, Activity))
	Info = Cursor.fetchall()
	#print(Info)
	DataBase.commit()
	DataBase.close()
	if len(Info) != 0:
		return True
	else:
		return False

def QueryActivity(Activity):
	'''
	描述：给定活动id，查询活动具体信息
	参数：活动id
	返回：一个字典，里面有活动id，名称，地点，开始，结束，最大人数，当前人数，创建者id
	如果没有就返回空字典
	{id:"1453",name:"旱地行舟",place:"科斯坦丁尼耶金角湾"，start：”1453-05-01 00：00：00“，end：”1453-05-29 23：59：59“，maxUser：100000，curUser:50000,creator：”muhmad2“}
	'''
	Success = True

	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
	
	#查询
	if Success:
		try:
			Cursor = DataBase.cursor()
			#Query = "SELECT * FROM ACTIVITY_LIST WHERE ID = ?",(Activity)
			#Params = [Activity]
			Info = []
			Cursor.execute("SELECT * FROM ACTIVITY_LIST WHERE ID = ?",(Activity,))
			Info = Cursor.fetchall()
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	#print(Info)
	#处理数据并且返回
	Result = {}
	if Success:
		try:
			Result["id"] = Info[0][0]
			Result["name"] = Info[0][1]
			Result["place"] = Info[0][2]
			Result["start"] = TimeStampToTimeString(int(Info[0][3]))
			Result["end"] = TimeStampToTimeString(int(Info[0][4]))
			Result["maxUser"] = int(Info[0][5])
			Result["curUser"] = int(Info[0][6])
			Result["creator"] = Info[0][7]
		except:
			Success = False
	return Result

def ShowAllActivity():
	'''
	描述：查询所有活动
	参数：活动id
	返回：一个字典数组，每个字典有活动id，名称，地点，开始，结束，最大人数，当前人数，创建者id
	如果没有就返回空数组
	[{id:"1453",name:"旱地行舟",place:"科斯坦丁尼耶金角湾"，start：”1453-05-01 00：00：00“，end：”1453-05-29 23：59：59“，maxUser：100000，curUser:50000,creator：”muhmad2“}]
	'''
	Success = True

	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
	
	#查询
	if Success:
		try:
			Cursor = DataBase.cursor()
			#Query = "SELECT * FROM ACTIVITY_LIST WHERE ID = ?",(Activity)
			#Params = [Activity]
			Info = []
			Cursor.execute("SELECT * FROM ACTIVITY_LIST")
			Info = Cursor.fetchall()
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	#处理数据并且返回
	Result = []
	if Success:
		try:
			for item in Info:
				TheResult = {}
				TheResult["id"] = item[0]
				TheResult["name"] = item[1]
				TheResult["place"] = item[2]
				TheResult["start"] = TimeStampToTimeString(int(item[3]))
				TheResult["end"] = TimeStampToTimeString(int(item[4]))
				TheResult["maxUser"] = int(item[5])
				TheResult["curUser"] = int(item[6])
				TheResult["creator"] = item[7]
				Result.append(TheResult)
		except:
			Success = False
	return Result

def InsertUserActivity(User, Activity):
	'''
	描述：把一个用户-活动插入数据库
	参数：用户id，活动id
	返回：成功True，失败False
	'''
	Success = True

	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
	
	#插入数据库
	if Success:
		try:
			Cursor = DataBase.cursor()
			#print(1)
			#Query = "INSERT INTO HISTORY_LIST VALUES(ID, OPENID, ACTIVITYID, TIME)\
			#VALUES (?,?,?,?)",(None, User, Activity, str(GetCurrentTime))
			#Params = [null, User, Activity, str(GetCurrentTime())]
			Cursor.execute("INSERT INTO HISTORY_LIST (ID, OPENID, ACTIVITYID, TIME)\
			VALUES (?,?,?,?)",(None, User, Activity, GetCurrentTime()))
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	print(Success)
	return Success

def CurUserAddOne(Activity):
	'''
	描述：活动当前参与者+1
	参数：活动id
	返回：成功True，失败False
	'''
	Success = True
	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
	
	#修改数据库
	if Success:
		try:
			Info = QueryActivity(Activity)
			CurUser = Info["curUser"]
			CurUser = CurUser + 1
			Cursor = DataBase.cursor()
			#Query = "UPDATE HISTORY_LIST SET CURUSER = ? WHERE ID = ?",(CurUser, Activity)
			#Params = [str(CurUser), Activity]
			Cursor.execute("UPDATE ACTIVITY_LIST SET CURUSER = ? WHERE ID = ?",(CurUser, Activity))
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	return Success

def JoinActivity(User, Activity):
	'''
	描述：报名函数	
	参数：用户id，活动id
	返回：成功{Success：True}，失败{Success：False，Reason：xxx}
	expire：过期，full：人满 cannotfound：没找到 joined：已经参加
	'''
	Success = True

	Return = {}

	#查询该活动具体信息，判断时间是否过期以及是否可以加入人
	if Success:
		try:
			Dictionary = QueryActivity(Activity)
			#print(Dictionary)
			CurrentTime = GetCurrentTime()
			#print(CurrentTime)
			EndTime = TimeStringToTimeStamp(Dictionary["end"])
			CurrentPeople = Dictionary["curUser"]
			MaxPeople = Dictionary["maxUser"]
			#print(Dictionary, CurrentTime, EndTime, CurrentPeople, MaxPeople)

			if CurrentTime > EndTime:
				Success = False
				Return["Reason"] = "expire"
			elif CurrentPeople >= MaxPeople:
				Success = False
				Return["Reason"] = "full"
		except:
			Success = False
			Return["Reason"] = "cannotfound"
	
	#print(Dictionary)

	#判断user是否已经参加这个活动
	if Success:
		try:
			if CheckUserJoinedActivity(User, Activity) == True:
				Success = False
				Return["Reason"] = "joined"
		except:
			Success = False
			Return["Reason"] = "other"
	
	
	#参加这个活动
	if Success:
		#print(1)
		try:
			if InsertUserActivity(User, Activity) == False:
				Success = False
				Return["Reason"] = "other"
		except:
			Success = False
			Return["Reason"] = "other"

	#当前参与用户数+1
	if Success:
		try:
			if CurUserAddOne(Activity) == False:
				Success = False
				Return["Reason"] = "other"
		except:
			Success = False
			Return["Reason"] = "other"

	Return["Success"] = Success
	return Return

def DeleteActivity(Activity):
	'''
	描述：删除活动函数
	参数：活动id
	返回：成功True 失败False
	'''
	Success = True
	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
	
	#先删除历史记录
	DeleteActivityHistory(Activity)

	#修改数据库
	if Success:
		try:
			
			Cursor = DataBase.cursor()
			#Query = "UPDATE HISTORY_LIST SET CURUSER = ? WHERE ID = ?",(CurUser, Activity)
			#Params = [str(CurUser), Activity]
			Cursor.execute("DELETE FROM ACTIVITY_LIST WHERE ID = ?",(Activity,))
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	return Success

def DeleteActivityHistory(Activity):
	'''
	描述：删除一个活动对应的全部历史记录
	参数：活动id
	返回：成功True，失败False
	'''
	Success = True
	#确定路径名和文件名
	TheName = "Database.db"

	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
	
	#修改数据库
	if Success:
		try:
			
			Cursor = DataBase.cursor()
			Cursor.execute("DELETE FROM HISTORY_LIST WHERE ACTIVITYID = ?",(Activity,))
			DataBase.commit()
			DataBase.close()
		except:
			Success = False
	return Success

def ChangeActivity(Activity, Name, Place, Start, End, MaxUser):
	'''
	描述：修改活动信息
	参数：活动id，活动要修改的的名字，地点，开始时间，结束时间，最大人数。不修改的是None
	返回：成功{Success：True}，失败{Success：False，Reason：xxx}
	notfound：找不到活动，invalid：修改不合法返回：成功True，失败False
	'''
	Success = True
	#确定路径名和文件名
	TheName = "Database.db"
	Return = {}
	#打开数据库文件
	if Success:
		try:
			DataBase = sqlite3.connect(TheName)
		except:
			sys.stderr.write("Cannot open database.")
			Success = False
			Return["Reason"] = "other"
	
	#判断是否能找到这个活动
	if Success:
		try:
			Dictionary = {}
			Dictionary = QueryActivity(Activity)
			if Dictionary == False:
				Success = False
				Return["Reason"] = "notfound"
		except:
			Success = False
			Return["Reason"] = "notfound"

	#判断修改是否有效
	if Success:
		try:
			Dictionary["name"] = Name
			Dictionary["place"] = Place
			Dictionary["start"] = Start
			Dictionary["end"] = End
			Dictionary["maxUser"] = MaxUser
			if Dictionary["maxUser"] < Dictionary["curUser"]:
				Success = False
				Return["Reason"] = "invalid"
		except:
			Success = False
			Return["Reason"] = "invalid"
	

	#修改数据库
	if Success:
		try:
			Cursor = DataBase.cursor()
			#Query = "UPDATE HISTORY_LIST SET CURUSER = ? WHERE ID = ?",(CurUser, Activity)
			#Params = [str(CurUser), Activity]
			Cursor.execute("UPDATE ACTIVITY_LIST SET NAME = ?, PLACE = ?, START = ?, END = ?, MAXUSER = ? WHERE ID = ?",
			(Dictionary["name"],Dictionary["place"],TimeStringToTimeStamp(Dictionary["start"]), TimeStringToTimeStamp(Dictionary["end"]),
			Dictionary["maxUser"], Activity))

			DataBase.commit()
			DataBase.close()
		except:
			Success = False
			Return["Reason"] = "other"
	Return["Success"] = Success
	return Return
			
def JudgeCreator(OpenID, Activity):
	'''
	描述：给定用户id和活动id，判断用户是活动创始人
	参数：用户id，活动id，都是str
	返回：是True，不是False
	'''
	Success = True
	TheName = "Database.db"
	DataBase = sqlite3.connect(TheName)
	Cursor = DataBase.cursor()
	Info = []
	Cursor.execute("SELECT * FROM ACTIVITY_LIST WHERE CREATOR = ? AND ID = ?", (OpenID, Activity))
	Info = Cursor.fetchall()
	#print(Info)
	DataBase.commit()
	DataBase.close()
	if len(Info) != 0:
		return True
	else:
		return False

	
	
